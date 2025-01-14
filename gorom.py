import requests
import random
import time
from datetime import datetime, timedelta

# Получение токена
url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
payload = {
    'scope': 'GIGACHAT_API_PERS',
}
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json',
    'RqUID': '5554e856-6c64-4054-b879-decca792da15',
    'Authorization': 'Basic MjM1MGJiYmYtNzI1ZS00ZGQzLWFkNWUtMjk2ZDdiMjI2MGQ0OjA5MTcyMmIyLThjOTItNDQwYS05Mzc2LTBiMGJmOWYxOWY4Ng=='
}

response = requests.post(url, headers=headers, data=payload, verify=False)
if response.status_code == 200:
    access_token = response.json().get('access_token')
else:
    print(f"Ошибка при получении токена: {response.text}")
    exit()

# Завтрашняя дата на русском
tomorrow_date = (datetime.now() + timedelta(days=1)).strftime('%d %B')
month_mapping = {
    'january': 'января', 'february': 'февраля', 'march': 'марта', 'april': 'апреля',
    'may': 'мая', 'june': 'июня', 'july': 'июля', 'august': 'августа',
    'september': 'сентября', 'october': 'октября', 'november': 'ноября', 'december': 'декабря'
}
month_in_english = tomorrow_date.split()[1].lower()
if month_in_english in month_mapping:
    tomorrow_date = tomorrow_date.replace(tomorrow_date.split()[1], month_mapping[month_in_english])

# Эмодзи для знаков зодиака
zodiac_emojis = {
    "Овен": "♈", "Телец": "♉", "Близнецы": "♊", "Рак": "♋",
    "Лев": "♌", "Дева": "♍", "Весы": "♎", "Скорпион": "♏",
    "Стрелец": "♐", "Козерог": "♑", "Водолей": "♒", "Рыбы": "♓"
}

# Генерация короткого гороскопа
def generate_horoscope_for_sign(sign):
    prompt = f"""
    Придумай легкий и краткий гороскоп для знака зодиака {sign} на завтра ({tomorrow_date}).
    Гороскоп должен быть из 1–3 предложений, позитивный или нейтральный. Без эмодзи в тексте.
    """
    chat_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    chat_headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    chat_data = {
        "model": "GigaChat",
        "messages": [{"role": "user", "content": prompt}]
    }
    chat_response = requests.post(chat_url, headers=chat_headers, json=chat_data, verify=False)
    if chat_response.status_code == 200:
        response_data = chat_response.json()
        return response_data['choices'][0]['message']['content']
    else:
        print(f"Ошибка при получении ответа от GigaChat: {chat_response.text}")
        return "Не удалось сгенерировать гороскоп."

# Генерация оценок звёздочками
def generate_stars():
    return "★" * random.randint(1, 5)

# Генерация и отправка гороскопов
bot_token = '7825529193:AAGKdoPMszeNFnZ50ur0IAJ0K_Myp2g1B7k'
channel_id = '@checkhyppo'
signs = list(zodiac_emojis.keys())

for sign in signs:
    horoscope = generate_horoscope_for_sign(sign)
    stars_career = generate_stars()
    stars_love = generate_stars()
    stars_health = generate_stars()

    horoscope_text = (
        f"{zodiac_emojis[sign]} {sign}, гороскоп на {tomorrow_date}:\n\n"
        f"{horoscope}\n\n"
        f"Карьера: {stars_career}\n"
        f"Любовь: {stars_love}\n"
        f"Здоровье: {stars_health}"
    )

    telegram_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    telegram_payload = {
        'chat_id': channel_id,
        'text': horoscope_text,
        'parse_mode': 'HTML'
    }
    telegram_response = requests.post(telegram_url, data=telegram_payload)
    if telegram_response.status_code == 200:
        print(f"Гороскоп для {sign} успешно отправлен в Telegram канал.")
    else:
        print(f"Ошибка при отправке гороскопа для {sign}: {telegram_response.text}")
    
    # Добавляем задержку перед отправкой следующего знака
    delay = random.randint(0, 30)  # Задержка в секундах (от 2 до 7 минут)
    print(f"Задержка перед следующим знаком: {delay} секунд.")
    time.sleep(delay)
