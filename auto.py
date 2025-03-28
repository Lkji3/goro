import os
import sys
import time
import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

# Конфигурация
TOKEN = "7825529193:AAH06S3J0b5NhvxqXI8UK7vte-HTddsC7vc"
CHAT_ID = 1111041097
ADMIN_ID = 1111041097
POST_SCHEDULE = {
    "morning": {"time": "07:00", "script": "goodmorning.py", "max_retries": 3},
    "day": {"time": "20:30", "script": "1.py", "max_retries": 3},
    "night": {"time": "23:00", "script": "goodnight.py", "max_retries": 3}
}

# Настройка логов
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('bot.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class PostBot:
    def __init__(self):
        self.bot = Bot(TOKEN)
        self.retry_counts = {name: 0 for name in POST_SCHEDULE}
        self.schedule_task = None

    async def send_alert(self, message: str):
        try:
            await self.bot.send_message(ADMIN_ID, message)
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления: {e}")

    async def run_script(self, script_name: str) -> bool:
        try:
            result = await asyncio.create_subprocess_exec(
                "python", script_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                raise Exception(stderr.decode().strip())
                
            logger.info(f"Скрипт {script_name} выполнен успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка в {script_name}: {e}")
            await self.send_alert(f"❌ Ошибка в {script_name}:\n{e}")
            return False

    async def scheduled_post(self, post_name: str):
        post = POST_SCHEDULE[post_name]
        self.retry_counts[post_name] = 0
        
        while self.retry_counts[post_name] < post["max_retries"]:
            if await self.run_script(post["script"]):
                await self.send_alert(f"✅ Пост {post_name} опубликован!")
                return
                
            self.retry_counts[post_name] += 1
            if self.retry_counts[post_name] < post["max_retries"]:
                await self.send_alert(f"♻️ Попытка {self.retry_counts[post_name]}/{post['max_retries']}...")
                await asyncio.sleep(300)
        
        await self.send_alert(f"🚨 Пост {post_name} НЕ опубликован после {post['max_retries']} попыток!")

    async def check_schedule(self):
        """Альтернатива JobQueue с asyncio"""
        while True:
            now = datetime.now().strftime("%H:%M")
            for name, post in POST_SCHEDULE.items():
                if now == post["time"]:
                    await self.scheduled_post(name)
            await asyncio.sleep(60)  # Проверка каждую минуту

    async def show_posts_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("Утренний пост", callback_data='morning')],
            [InlineKeyboardButton("Дневной пост", callback_data='day')],
            [InlineKeyboardButton("Ночной пост", callback_data='night')],
            [InlineKeyboardButton("Проверить статус", callback_data='status')],
            [InlineKeyboardButton("🔄 Рестарт бота", callback_data='restart')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Выберите действие:', reply_markup=reply_markup)

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        if query.data in POST_SCHEDULE:
            await query.edit_message_text(text=f"🔄 Запускаю {query.data} пост...")
            await self.scheduled_post(query.data)
        elif query.data == 'status':
            status = "\n".join([f"{name}: {count} попыток" for name, count in self.retry_counts.items()])
            await query.edit_message_text(text=f"📊 Статус постов:\n{status}")
        elif query.data == 'restart':
            await query.edit_message_text(text="🔄 Инициирую перезапуск бота...")
            os.execv(sys.executable, ['python'] + sys.argv)
        else:
            await query.edit_message_text(text="❌ Неизвестная команда")

    async def restart_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🔄 Инициирую перезапуск...")
        os.execv(sys.executable, ['python'] + sys.argv)

    async def on_error(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        error = str(context.error)
        logger.critical(f"КРИТИЧЕСКАЯ ОШИБКА: {error}")
        await self.send_alert(f"💥 Критическая ошибка:\n{error}\n\nПерезапуск через 5 минут...")
        await asyncio.sleep(300)
        os.execv(sys.executable, ['python'] + sys.argv)

async def main():
    bot = PostBot()
    
    # Создаем Application без JobQueue
    app = Application.builder().token(TOKEN).build()
    
    # Обработчики команд
    app.add_handler(CommandHandler("start", bot.show_posts_menu))
    app.add_handler(CommandHandler("restart", bot.restart_command))
    app.add_handler(CommandHandler("posts", bot.show_posts_menu))
    app.add_handler(CallbackQueryHandler(bot.button_handler))
    app.add_error_handler(bot.on_error)
    
    # Запускаем проверку расписания в фоне
    bot.schedule_task = asyncio.create_task(bot.check_schedule())
    
    await bot.send_alert("🤖 Бот запущен в режиме 24/7!")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        if bot.schedule_task:
            bot.schedule_task.cancel()
        await app.stop()
        await app.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен вручную")
    except Exception as e:
        logger.critical(f"Фатальная ошибка: {e}")
        sys.exit(1)
