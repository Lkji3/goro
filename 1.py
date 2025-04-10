import requests
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.error import RetryAfter
import asyncio

# Конфигурация (ЗАМЕНИТЕ НА СВОИ ДАННЫЕ!)
BOT_TOKEN = "7825529193:AAEIIA_IrpWM4bb1EGqAWrBxJABlZKko7sE"  # Замените на ваш токен
CHANNEL_ID = -1002419012006   # Замените на ID вашего канала

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

def get_horoscope(sign: int, day: str = "tomorrow") -> str:
    """Получает гороскоп для знака зодиака."""
    url = f"https://www.horoscope.com/us/horoscopes/general/horoscope-general-daily-{day}.aspx?sign={sign}"
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        horoscope_text = soup.find("div", class_="main-horoscope")
        return horoscope_text.p.text.strip() if horoscope_text else "Гороскоп не найден."
    return "Ошибка при получении гороскопа."

def translate_date(date: str) -> str:
    """Переводит дату с английского на русский (например, 'Mar 23, 2025' → '23 марта')."""
    month_translation = {
        "Jan": "января", "Feb": "февраля", "Mar": "марта", "Apr": "апреля",
        "May": "мая", "Jun": "июня", "Jul": "июля", "Aug": "августа",
        "Sep": "сентября", "Oct": "октября", "Nov": "ноября", "Dec": "декабря",
    }
    parts = date.split()
    if len(parts) == 3:
        month_en, day, _ = parts
        return f"{day} {month_translation.get(month_en, month_en)}"
    return date

def extract_date(text: str) -> str:
    """Извлекает дату из текста гороскопа."""
    return translate_date(text.split(" - ")[0]) if " - " in text else ""

def clean_horoscope_text(text: str) -> str:
    """Удаляет дату из текста гороскопа."""
    return text.split(" - ", 1)[1] if " - " in text else text

def translate_to_russian(text: str) -> str:
    """Переводит текст на русский с помощью MyMemory API."""
    response = requests.get(
        "https://api.mymemory.translated.net/get",
        params={"q": text, "langpair": "en|ru"}
    )
    if response.status_code == 200:
        return response.json().get("responseData", {}).get("translatedText", text)
    return text

async def publish_horoscopes():
    """Отправляет гороскопы для всех знаков зодиака."""
    bot = Bot(token=BOT_TOKEN)
    for sign_name, sign_data in ZODIAC_SIGNS.items():
        try:
            # Получаем и обрабатываем гороскоп
            horoscope_en = get_horoscope(sign_data["number"])
            date = extract_date(horoscope_en)
            text_cleaned = clean_horoscope_text(horoscope_en)
            text_ru = translate_to_russian(text_cleaned)
            
            # Формируем и отправляем сообщение
            message = f"{sign_data['emoji']} {sign_name}, {date}:\n{text_ru}"
            await bot.send_message(chat_id=CHANNEL_ID, text=message)
            
            # Пауза между сообщениями (30 секунд)
            await asyncio.sleep(30)
            
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception as e:
            print(f"Ошибка для {sign_name}: {e}")

async def main():
    """Основная функция."""
    await publish_horoscopes()

if __name__ == "__main__":
    asyncio.run(main())
