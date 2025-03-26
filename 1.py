import requests
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.error import RetryAfter
import asyncio

# Токен вашего бота
BOT_TOKEN = "7825529193:AAH06S3J0b5NhvxqXI8UK7vte-HTddsC7vc"
# ID вашего канала (например, @your_channel_name)
CHANNEL_ID = "@hyppolove"

# Список знаков зодиака с эмодзи
ZODIAC_SIGNS = {
    "Овен": {"number": 1, "emoji": "♈️"},
    "Телец": {"number": 2, "emoji": "♉️"},
    "Близнецы": {"number": 3, "emoji": "♊️"},
    "Рак": {"number": 4, "emoji": "♋️"},
    "Лев": {"number": 5, "emoji": "♌️"},
    "Дева": {"number": 6, "emoji": "♍️"},
    "Весы": {"number": 7, "emoji": "♎️"},
    "Скорпион": {"number": 8, "emoji": "♏️"},
    "Стрелец": {"number": 9, "emoji": "♐️"},
    "Козерог": {"number": 10, "emoji": "♑️"},
    "Водолей": {"number": 11, "emoji": "♒️"},
    "Рыбы": {"number": 12, "emoji": "♓️"},
}

# Функция для получения гороскопа на завтра
def get_horoscope(sign: int, day: str = "tomorrow") -> str:
    """
    Получает гороскоп для указанного знака зодиака и дня.
    :param sign: Номер знака зодиака (1-12).
    :param day: День (tomorrow, today, yesterday или дата в формате ГГГГ-ММ-ДД).
    :return: Текст гороскопа.
    """
    url = f"https://www.horoscope.com/us/horoscopes/general/horoscope-general-daily-{day}.aspx?sign={sign}"
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        horoscope_text = soup.find("div", class_="main-horoscope")
        if horoscope_text:
            return horoscope_text.p.text.strip()
    return "Гороскоп не найден."

# Функция для перевода даты с английского на русский
def translate_date(date: str) -> str:
    """
    Переводит дату с английского на русский и убирает год.
    Пример: "Mar 23, 2025" → "23 марта".
    """
    month_translation = {
        "Jan": "января",
        "Feb": "февраля",
        "Mar": "марта",
        "Apr": "апреля",
        "May": "мая",
        "Jun": "июня",
        "Jul": "июля",
        "Aug": "августа",
        "Sep": "сентября",
        "Oct": "октября",
        "Nov": "ноября",
        "Dec": "декабря",
    }
    # Разделяем дату на части
    parts = date.split()
    if len(parts) == 3:
        month_en, day, year = parts
        # Переводим месяц
        month_ru = month_translation.get(month_en, month_en)
        # Возвращаем дату в формате "число месяц"
        return f"{day} {month_ru}"
    return date  # Если формат даты не распознан, возвращаем оригинал

# Функция для извлечения даты из текста гороскопа
def extract_date(text: str) -> str:
    """
    Извлекает дату из текста гороскопа и переводит её на русский.
    """
    if " - " in text:
        date_part = text.split(" - ", 1)[0]  # Берем часть до " - "
        # Переводим дату на русский
        return translate_date(date_part)
    return ""

# Функция для очистки текста от даты и года
def clean_horoscope_text(text: str) -> str:
    """
    Удаляет дату и год из текста гороскопа.
    """
    if " - " in text:
        text = text.split(" - ", 1)[1]  # Берем часть после даты
    return text

# Функция для перевода текста с помощью MyMemory API
def translate_to_russian(text: str) -> str:
    """
    Переводит текст на русский с помощью MyMemory API.
    """
    url = "https://api.mymemory.translated.net/get"
    params = {
        "q": text,
        "langpair": "en|ru"  # Переводим с английского на русский
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("responseData"):
            return data["responseData"]["translatedText"]
    return text  # Возвращаем оригинальный текст в случае ошибки

# Асинхронная функция для публикации гороскопов
async def publish_horoscopes():
    bot = Bot(token=BOT_TOKEN)
    while True:
        for sign_name, sign_data in ZODIAC_SIGNS.items():
            try:
                # Получаем гороскоп на завтра
                horoscope_text = get_horoscope(sign_data["number"], "tomorrow")
                # Извлекаем дату и переводим её
                date = extract_date(horoscope_text)
                # Очищаем текст от даты и года
                horoscope_text_cleaned = clean_horoscope_text(horoscope_text)
                # Переводим текст на русский
                horoscope_text_ru = translate_to_russian(horoscope_text_cleaned)
                # Формируем сообщение в формате "Знак зодиака, дата:\nописание"
                message = f"{sign_data['emoji']} {sign_name}, {date}:\n{horoscope_text_ru}"
                # Отправляем сообщение в канал
                await bot.send_message(chat_id=CHANNEL_ID, text=message)
                # Ждем 30 секунд между сообщениями, чтобы избежать блокировки
                await asyncio.sleep(0)
            except RetryAfter as e:
                # Если Telegram просит подождать, ждем указанное время
                await asyncio.sleep(e.retry_after)
            except Exception as e:
                # Логируем другие ошибки
                print(f"Ошибка: {e}")

# Запуск бота
async def main():
    await publish_horoscopes()

if __name__ == "__main__":
    asyncio.run(main())
