import os
import logging
from datetime import time, datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)
import subprocess

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("script_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Конфигурация
TOKEN = "7825529193:AAH06S3J0b5NhvxqXI8UK7vte-HTddsC7vc"  # Замените на токен от @BotFather
YOUR_USERNAME = "lkji33"  # Ваш Telegram username (без @)
SCRIPT_PATHS = {
    "morning": "goodmorning.py",
    "day": "1.py",
    "night": "goodnight.py",
}

# Расписание выполнения
SCHEDULE = {
    "morning": time(7, 0),  # 7:00
    "day": time(20, 0),     # 20:00
    "night": time(23, 0),   # 23:00
}

# Клавиатура с кнопками
KEYBOARD = ReplyKeyboardMarkup(
    [["☀ Утро", "🌆 День", "🌙 Ночь"]],
    resize_keyboard=True,
    one_time_keyboard=False
)

def run_script(script_name: str) -> dict:
    """Запускает скрипт и возвращает результат"""
    result = {
        "success": False,
        "output": "",
        "error": "",
        "script": script_name,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "filename": SCRIPT_PATHS.get(script_name, "unknown"),
    }

    if script_name not in SCRIPT_PATHS:
        result["error"] = "Скрипт не найден в конфигурации"
        return result

    script_path = SCRIPT_PATHS[script_name]
    if not os.path.exists(script_path):
        result["error"] = f"Файл {script_path} не существует"
        return result

    try:
        process = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True,
            check=True
        )
        result.update({
            "output": process.stdout.strip(),
            "error": process.stderr.strip(),
            "success": True
        })
    except subprocess.CalledProcessError as e:
        result.update({
            "output": e.stdout.strip(),
            "error": e.stderr.strip(),
            "success": False
        })
    except Exception as e:
        result["error"] = str(e)

    return result

async def send_log_to_user(update: Update, result: dict):
    """Отправляет лог выполнения"""
    try:
        status = "✅ УСПЕШНО" if result["success"] else "❌ ОШИБКА"
        message = (
            f"🕒 Время: {result['time']}\n"
            f"📜 Скрипт: {result['script']} ({result['filename']})\n"
            f"🔹 Статус: {status}\n"
        )

        if result["output"]:
            message += f"\n📝 Вывод:\n{result['output']}\n"
        if result["error"]:
            message += f"\n⚠ Ошибки:\n{result['error']}\n"

        await update.message.reply_text(message, reply_markup=KEYBOARD)
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения: {e}")

async def callback_morning(context: ContextTypes.DEFAULT_TYPE):
    """Утренний скрипт"""
    result = run_script("morning")
    await send_log_to_user(context.job, result)

async def callback_day(context: ContextTypes.DEFAULT_TYPE):
    """Дневной скрипт"""
    result = run_script("day")
    await send_log_to_user(context.job, result)

async def callback_night(context: ContextTypes.DEFAULT_TYPE):
    """Вечерний скрипт"""
    result = run_script("night")
    await send_log_to_user(context.job, result)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Инициализация бота"""
    if update.effective_user.username != YOUR_USERNAME:
        await update.message.reply_text("⛔ Доступ запрещен!")
        return

    # Удаляем старые задания
    for job in context.job_queue.jobs():
        job.schedule_removal()

    # Добавляем новые задания
    context.job_queue.run_daily(callback_morning, time=SCHEDULE["morning"])
    context.job_queue.run_daily(callback_day, time=SCHEDULE["day"])
    context.job_queue.run_daily(callback_night, time=SCHEDULE["night"])

    await update.message.reply_text(
        "🤖 Бот запущен! Расписание:\n"
        f"☀ Утро 07:00 - goodmorning.py\n"
        f"🌆 День 20:00 - 1.py\n"
        f"🌙 Ночь 23:00 - goodnight.py\n\n"
        "Используйте кнопки ниже для запуска скриптов:",
        reply_markup=KEYBOARD
    )

async def manual_run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ручной запуск скрипта через команду"""
    if update.effective_user.username != YOUR_USERNAME:
        await update.message.reply_text("⛔ Доступ запрещен!")
        return

    if not context.args:
        await update.message.reply_text("Используйте: /run <morning|day|night>")
        return

    script_name = context.args[0].lower()
    if script_name not in SCRIPT_PATHS:
        await update.message.reply_text("Доступные скрипты: morning, day, night")
        return

    await update.message.reply_text(f"⏳ Запускаю {script_name}...")
    result = run_script(script_name)
    await send_log_to_user(update, result)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий кнопок"""
    if update.effective_user.username != YOUR_USERNAME:
        await update.message.reply_text("⛔ Доступ запрещен!")
        return

    text = update.message.text
    script_map = {
        "☀ Утро": "morning",
        "🌆 День": "day",
        "🌙 Ночь": "night"
    }

    if text not in script_map:
        await update.message.reply_text("Используйте кнопки для запуска скриптов")
        return

    script_name = script_map[text]
    await update.message.reply_text(f"⏳ Запускаю {script_name} скрипт...")
    result = run_script(script_name)
    await send_log_to_user(update, result)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ошибок"""
    logger.error(f"Ошибка: {context.error}")
    if update and isinstance(update, Update):
        if update.effective_user.username == YOUR_USERNAME:
            await update.message.reply_text(
                f"⚠ Ошибка: {context.error}",
                reply_markup=KEYBOARD
            )

def main():
    """Основная функция запуска"""
    try:
        application = Application.builder().token(TOKEN).build()
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("run", manual_run))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))
        application.add_error_handler(error_handler)
        
        logger.info("Бот запускается...")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Фатальная ошибка: {e}")
        raise

if __name__ == "__main__":
    main()
