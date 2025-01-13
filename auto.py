import os
import schedule
import time
from telegram import Bot
from threading import Thread

# Укажите ваш токен бота
TELEGRAM_BOT_TOKEN = "7825529193:AAGKdoPMszeNFnZ50ur0IAJ0K_Myp2g1B7k"
CHANNEL_ID = "@checkhyppo"  # Укажите ID или username канала
USER_ID = "@lkji33"  # Укажите username или ID пользователя для уведомлений

bot = Bot(token=TELEGRAM_BOT_TOKEN)

def send_message(script_name, time):
    try:
        # Запуск скрипта
        os.system(f"python {script_name}")

        # Отправка сообщения в канал (опционально)
        bot.send_message(chat_id=CHANNEL_ID, text=f"Скрипт {script_name} успешно запущен в {time}.")

        # Отправка уведомления пользователю
        bot.send_message(chat_id=USER_ID, text=f"Скрипт {script_name} успешно выполнен в {time}.")
    except Exception as e:
        print(f"Ошибка при запуске скрипта {script_name}: {e}")

def schedule_scripts():
    # Расписание выполнения скриптов
    schedule.every().day.at("07:00").do(send_message, script_name="goodmorning.py", time="07:00")
    schedule.every().day.at("20:00").do(send_message, script_name="gorom.py", time="20:00")
    schedule.every().day.at("23:00").do(send_message, script_name="goodnight.py", time="23:00")

    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    # Запуск расписания в отдельном потоке
    thread = Thread(target=schedule_scripts)
    thread.start()

    print("Бот запущен и ожидает выполнения задач...")

if __name__ == "__main__":
    main()
