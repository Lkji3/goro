import os
import sys
import time
import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

# Конфигурация
TOKEN = "7825529193:AAEIIA_IrpWM4bb1EGqAWrBxJABlZKko7sE"
CHAT_ID = 1111041097
ADMIN_ID = 1111041097  # Ваш username или ID
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

    async def send_alert(self, message: str):
        """Отправка уведомления админу"""
        try:
            await self.bot.send_message(ADMIN_ID, message)
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления: {e}")

    async def run_script(self, script_name: str) -> bool:
        """Запуск скрипта поста с обработкой ошибок"""
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
        """Публикация поста с повторами при ошибке"""
        post = POST_SCHEDULE[post_name]
        self.retry_counts[post_name] = 0
        
        while self.retry_counts[post_name] < post["max_retries"]:
            if await self.run_script(post["script"]):
                await self.send_alert(f"✅ Пост {post_name} опубликован!")
                return
                
            self.retry_counts[post_name] += 1
            if self.retry_counts[post_name] < post["max_retries"]:
                await self.send_alert(f"♻️ Попытка {self.retry_counts[post_name]}/{post['max_retries']}...")
                await asyncio.sleep(300)  # 5 минут перед повтором
        
        await self.send_alert(f"🚨 Пост {post_name} НЕ опубликован после {post['max_retries']} попыток!")

    async def check_schedule(self, context: ContextTypes.DEFAULT_TYPE):
        """Проверка расписания"""
        now = datetime.now().strftime("%H:%M")
        for name, post in POST_SCHEDULE.items():
            if now == post["time"]:
                await self.scheduled_post(name)

    async def show_posts_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показывает меню с кнопками для постов"""
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
        """Обработчик нажатий на кнопки"""
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
        """Ручной перезапуск через Telegram"""
        await update.message.reply_text("🔄 Инициирую перезапуск...")
        os.execv(sys.executable, ['python'] + sys.argv)

    async def on_error(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Обработка неожиданных ошибок"""
        error = str(context.error)
        logger.critical(f"КРИТИЧЕСКАЯ ОШИБКА: {error}")
        await self.send_alert(f"💥 Критическая ошибка:\n{error}\n\nПерезапуск через 5 минут...")
        await asyncio.sleep(300)
        os.execv(sys.executable, ['python'] + sys.argv)

async def main():
    bot = PostBot()
    app = Application.builder().token(TOKEN).build()
    
    # Обработчики команд
    app.add_handler(CommandHandler("start", bot.show_posts_menu))
    app.add_handler(CommandHandler("restart", bot.restart_command))
    app.add_handler(CommandHandler("posts", bot.show_posts_menu))
    
    # Обработчик кнопок
    app.add_handler(CallbackQueryHandler(bot.button_handler))
    
    # Обработчик ошибок
    app.add_error_handler(bot.on_error)
    
    # Планировщик
    job_queue = app.job_queue
    job_queue.run_repeating(bot.check_schedule, interval=60.0)  # Проверка каждую минуту
    
    await bot.send_alert("🤖 Бот запущен в режиме 24/7!")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    while True:
        await asyncio.sleep(3600)  # Просто поддерживаем работу

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен вручную")
    except Exception as e:
        logger.critical(f"Фатальная ошибка: {e}")
        sys.exit(1)
