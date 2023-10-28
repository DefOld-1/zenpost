import requests
import random
import asyncio

TOKEN = "6165593766:AAG5NqL3uaaURcIbce6sYHVn30rYcOhknWY"  # Замените на свой действительный токен

# URL для запросов к API Zen
ZEN_URL = "https://dzen.ru/api/v3/launcher/export"

# Каналы для копирования новостей
channels = ["popsci", "nplus1", "naukatv", "scfh", "uralscience", "nakedscience", "techinsider", "astronews", "hi-news.ru", "deep_cosmos"]

# Список для хранения новостей
news_list = []

# Функция для получения постов Zen по имени канала
def get_zen_posts(channel):
    # Подготовка параметров запроса
    params = {
        "clid": 300,
        "country_code": "ru",
        "lang": "ru",
        "channel_name": channel
    }
    # Отправка запроса и получение ответа
    response = requests.get(ZEN_URL, params=params)
    # Проверка статуса ответа
    if response.status_code == 200:
        # Преобразование ответа в формат JSON
        data = response.json()
        # Извлечение списка постов из данных
        posts = data.get("items", [])
        # Возврат списка постов
        return posts
    else:
        # Возврат пустого списка в случае ошибки
        return []

# Функция для форматирования сообщения с постом Zen
def format_zen_post(post, channel):
    # Извлечение заголовка, ссылки и изображения из поста
    title = post.get("title")
    link = post.get("share_link")
    text = post.get("text")
    image = post.get("image")
    domain_title = post.get("domain_title")
    # Форматирование текста сообщения с разметкой Markdown
    text1 = f"{title}\n\n{text}\n{domain_title}: {link}\n@sci_popular"
    # Возврат текста сообщения и изображения
    return text1, image

# Функция для получения последних 10 новостей из каждого канала и добавления их в список новостей
def update_news_list():
    for channel in channels:
        posts = get_zen_posts(channel)
        if posts:
            latest_posts = posts[:10]  # Получение последних 10 постов
            for post in latest_posts:
                if post.get("text"):  # Проверка наличия текста в посте
                    news_list.append((post, channel))

# Функция для получения случайной новости из списка
def get_random_news():
    news_with_text = [(news, channel) for news, channel in news_list if news.get("text")]
    if news_with_text:
        news, channel = random.choice(news_with_text)
        news_list.remove((news, channel))
        return news, channel
    else:
        return None, None

# Функция для публикации случайных новостей
async def publish_random_news():
    while True:
        update_news_list()  # Обновление списка новостей
        news, channel = get_random_news()
        if news and channel:
            text, image = format_zen_post(news, channel)
            if image:
                print(f"Published: {text}")
                # Здесь вы можете добавить код для публикации сообщений в Telegram
            else:
                print(f"Published: {text}")
                # Здесь вы можете добавить код для публикации сообщений в Telegram
        await asyncio.sleep(3600)  # Ожидание 1 часа

# Запуск бота и планирование публикации новостей
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(publish_random_news())
    loop.run_forever()
