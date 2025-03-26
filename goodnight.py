import requests
import json
import time
import base64
import re
import random

# Получение токена
url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
payload = {
    'scope': 'GIGACHAT_API_PERS',  # Сфера действия (для физических лиц)
}
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json',
    'RqUID': '5554e856-6c64-4054-b879-decca792da15',  # Уникальный ID запроса
    'Authorization': 'Basic MjM1MGJiYmYtNzI1ZS00ZGQzLWFkNWUtMjk2ZDdiMjI2MGQ0OjA5MTcyMmIyLThjOTItNDQwYS05Mzc2LTBiMGJmOWYxOWY4Ng=='  # Замените на свой ключ
}

# Отправка запроса на получение токена
response = requests.post(url, headers=headers, data=payload, verify=False)
if response.status_code == 200:
    access_token = response.json().get('access_token')  # Сохраняем токен
    print(f"Access Token: {access_token}")
else:
    print(f"Ошибка при получении токена: {response.text}")
    exit()

# Теперь используем токен для получения ответа от модели GigaChat
chat_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

chat_headers = {
    'Authorization': f'Bearer {access_token}',  # Вставляем токен в заголовок
    'Content-Type': 'application/json',
    'Accept': 'application/json',
}


def generate_motivational_request():
    templates = [
        "Как вдохновить себя на спокойный вечер? Напиши 2-3 предложения.",
        "Напиши вдохновляющий текст для завершения дня. Напиши 2-3 предложения.",
        "Поделись мотивацией для ночного отдыха. Напиши 2-3 предложения.",
        "Как создать атмосферу уюта перед сном? Напиши краткий текст. Напиши 2-3 предложения.",
        "Напиши короткую мотивационную фразу для хорошего вечера. Напиши 2-3 предложения.",
        "Ночная мотивация. Напиши 2-3 предложения.",
        "Создай позитивное сообщение для завершения дня. Напиши 2-3 предложения.",
        "Как закончить день с хорошим настроением? Напиши 2-3 предложения.",
        "Напиши текст, который вдохновит на спокойный вечер. Напиши 2-3 предложения.",
        "Как сделать вечер более радостным? Напиши 2-3 предложения.",
        "Создай текст для вечернего поста, который поднимет настроение. Напиши 2-3 предложения.",
        "Как зарядить позитивом на ночь? Напиши 2-3 предложения.",
        "Напиши вдохновляющий совет для успешного завершения дня. Напиши 2-3 предложения.",
        "Как настроиться на спокойный вечер? Напиши 2-3 предложения.",
        "Создай ночную мотивацию для всех, кто готовится ко сну. Напиши 2-3 предложения.",
        "Напиши несколько строк, которые вдохновят на отдых перед сном. Напиши 2-3 предложения.",
        "Как пробудить в себе желание расслабиться перед сном? Напиши 2-3 предложения.",
        "Создай текст, который поможет закончить день с улыбкой. Напиши 2-3 предложения.",
        "Как сделать вечер более продуктивным? Напиши 2-3 предложения.",
        "Напиши фразу, которая поднимет настроение на ночь. Напиши 2-3 предложения.",
        "Как вдохновить себя на спокойный вечер? Напиши 2-3 предложения.",
        "Создай послание, которое подарит надежду на завтра. Напиши 2-3 предложения.",
        "Напиши текст, который поможет расслабиться перед сном. Напиши 2-3 предложения.",
        "Как сделать вечер более приятным? Напиши 2-3 предложения.",
        "Напиши несколько слов, которые вдохновят на спокойный отдых. Напиши 2-3 предложения.",
        "Как закончить день с позитивом? Напиши 2-3 предложения.",
        "Создай текст для вечернего саморазмышления. Напиши 2-3 предложения.",
        "Как вдохновить других на спокойный вечер? Напиши 2-3 предложения.",
        "Предложи мотивацию для тех, кто хочет завершить день с позитивом. Напиши 2-3 предложения.",
        "Напиши текст с позитивным настроением для вечернего поста. Напиши 2-3 предложения.",
        "Как настроиться на спокойный вечер? Напиши 2-3 предложения.",
        "Создай вдохновляющее сообщение для друзей на ночь. Напиши 2-3 предложения.",
        "Напиши короткий текст, который поможет закончить день с радостью. Напиши 2-3 предложения.",
        "Как вдохновить себя на спокойный отдых? Напиши 2-3 предложения.",
        "Создай текст, который поможет забыть о проблемах перед сном. Напиши 2-3 предложения.",
        "Напиши несколько вдохновляющих слов для вечернего настроя. Напиши 2-3 предложения.",
        "Как пробудить в себе желание действовать перед сном? Напиши 2-3 предложения.",
        "Создай короткий текст, который будет мотивировать на спокойный вечер. Напиши 2-3 предложения.",
        "Как сделать вечер более радостным и продуктивным? Напиши 2-3 предложения.",
        "Напиши фразу, которая поможет закончить день с оптимизмом. Напиши 2-3 предложения.",
        "Как вдохновить себя на новую ночь? Напиши 2-3 предложения.",
        "Создай послание, которое будет вдохновлять на протяжении ночи. Напиши 2-3 предложения.",
        "Напиши текст, который поможет настроиться на позитивный лад перед сном. Напиши 2-3 предложения.",
        "Как сделать вечер более приятным? Напиши 2-3 предложения.",
        "Напиши короткую фразу, которая поднимет настроение на всю ночь. Напиши 2-3 предложения.",
        "Как вдохновить себя на спокойный отдых? Напиши 2-3 предложения.",
        "Создай текст, который поможет забыть о стрессе перед сном. Напиши 2-3 предложения.",
        "Напиши несколько слов, которые будут мотивировать на спокойный вечер. Напиши 2-3 предложения.",
        "Как закончить день с улыбкой? Напиши 2-3 предложения.",
        "Создай вдохновляющее сообщение для своих близких на ночь. Напиши 2-3 предложения.",
        "Напиши текст, который поможет настроиться на продуктивный вечер. Напиши 2-3 предложения.",
        "Как пробудить в себе желание действовать перед сном? Напиши 2-3 предложения.",
        "Напиши фразу, которая поможет закончить день с позитивом. Напиши 2-3 предложения.",
        "Как вдохновить себя на новые начинания вечером? Напиши 2-3 предложения.",
        "Создай текст, который поможет забыть о проблемах перед сном. Напиши 2-3 предложения.",
        "Напиши несколько вдохновляющих слов для вечернего настроя. Напиши 2-3 предложения.",
        "Как сделать вечер более радостным и продуктивным? Напиши 2-3 предложения.",
        "Создай мотивационное сообщение для друзей на ночь. Напиши 2-3 предложения.",
        "Напиши короткий текст, который поможет закончить день с радостью. Напиши 2-3 предложения.",
        "Как настроиться на успех вечером? Напиши 2-3 предложения.",
        "Напиши мотивационную фразу для вечерней зарядки. Напиши 2-3 предложения.",
    ]
    return random.choice(templates)


# Динамический запрос в GigaChat
chat_data = {
    "model": "GigaChat",  # Указываем модель GigaChat
    "messages": [
        {
            "role": "user",  # Указываем, что это сообщение от пользователя
            "content": generate_motivational_request()  # Используем случайно сгенерированный текст
        }
    ]
}


# Отправляем POST-запрос
chat_response = requests.post(chat_url, headers=chat_headers, json=chat_data, verify=False)

# Обработка ответа
if chat_response.status_code == 200:
    response_data = chat_response.json()
    answer = response_data['choices'][0]['message']['content']  # Получаем ответ от модели
    print(answer)  # Печатаем ответ на экран
    
    # Запись ответа в текстовый файл
    with open("response.txt", "w", encoding="utf-8") as file:
        file.write(answer)
    print("Ответ записан в файл 'response.txt'.")
    
else:
    print(f"Ошибка при получении ответа от GigaChat: {chat_response.text}")
    exit()

# --- Формирование темы и текста поста ---


# Тема + ответ
post = f"Доброй ночи \n\n{answer}"

print("\n--- Генерация поста ---")
print(post)

# --- Генерация изображения ---

class Text2ImageAPI:

    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_model(self):
        response = requests.get(self.URL + 'key/api/v1/models', headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    def generate(self, prompt, model, images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": f"{prompt}"
            }
        }

        data = {
            'model_id': (None, model),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/text2image/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

    def check_generation(self, request_id, attempts=40, delay=10):
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/text2image/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                print(f"Изображение сгенерировано успешно: {data['images']}")
                return data['images']

            attempts -= 1
            print(f"Задача в статусе {data['status']}, попытка {40 - attempts}...")
            time.sleep(delay)
        print("Не удалось получить изображение после завершения генерации.")
        return None

    def download_image(self, image_base64, file_path):
        # Декодируем Base64 в байты
        image_data = base64.b64decode(image_base64)
        
        # Записываем байты в файл
        with open(file_path, 'wb') as file:
            file.write(image_data)
            print(f"Изображение сохранено по пути: {file_path}")
        return file_path


# Пример использования API Kandinsky
api_url = 'https://api-key.fusionbrain.ai/'
api_key = 'B003A085CA0287E8EAE86ECC00B259FC'
secret_key = '67505534A526F5635FAFEAABED29C9F4'

api = Text2ImageAPI(api_url, api_key, secret_key)


def generate_image_prompt():
    # Список вариантов для генерации изображений
    prompts = [
        "Звёздное небо над спокойным озером",
        "Лунный свет, отражающийся на поверхности моря",
        "Ночной город с огнями и тишиной",
        "Тайный лес при свете луны",
        "Небо, усыпанное звёздами, над горными вершинами",
        "Свет фонарей на пустынной улице ночью",
        "Ночной пейзаж с мерцающими огнями вдали",
        "Тёмное небо с яркой кометой, проносящейся мимо",
    ]
    return random.choice(prompts)

try:
    # Выбор модели
    model_id = api.get_model()
    print(f"Модель выбрана: {model_id}")

    # Генерация изображения с динамическим запросом
    prompt = generate_image_prompt()
    print(f"Сгенерированный запрос для изображения: {prompt}")
    uuid = api.generate(prompt, model_id)
    print(f"Запрос на генерацию изображения отправлен, UUID: {uuid}")

    # Проверка статуса и получение изображения
    images_base64 = api.check_generation(uuid)

    bot_token = '7825529193:AAH06S3J0b5NhvxqXI8UK7vte-HTddsC7vc'  # Токен вашего Telegram бота
    channel_id = '@hyppolove'  # ID вашего канала (с @ на начале)

    # Форматируем текст сообщения
    caption = post  # Убедитесь, что переменная `post` заранее заполнена
    caption = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', caption)  # Заменяем **текст** на <b>текст</b>

    # Ограничиваем длину текста до 1024 символов
    max_caption_length = 1024
    if len(caption) > max_caption_length:
        caption = caption[:max_caption_length]

    if images_base64:
        print(f"Изображение получено: {images_base64[0]}")  # Вывод Base64 изображения
        # Скачиваем изображение
        image_path = api.download_image(images_base64[0], 'generated_image.png')

        # Отправка изображения в Telegram
        with open(image_path, 'rb') as image_file:
            telegram_url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'
            telegram_payload = {
                'chat_id': channel_id,
                'caption': caption,
                'parse_mode': 'HTML'
            }
            files = {'photo': image_file}
            telegram_response = requests.post(telegram_url, data=telegram_payload, files=files)

            if telegram_response.status_code == 200:
                print("Ответ и изображение успешно отправлены в Telegram канал.")
            else:
                print(f"Ошибка при отправке в Telegram: {telegram_response.text}")
    else:
        print("Не удалось получить изображение, отправляем только текст.")
        # Отправка текста без фото
        telegram_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        telegram_payload = {
            'chat_id': channel_id,
            'text': caption,
            'parse_mode': 'HTML'
        }
        telegram_response = requests.post(telegram_url, data=telegram_payload)

        if telegram_response.status_code == 200:
            print("Ответ успешно отправлен в Telegram канал.")
        else:
            print(f"Ошибка при отправке текста в Telegram: {telegram_response.text}")

except Exception as e:
    print(f"Произошла ошибка при работе с API: {e}")
