import requests
import random
import asyncio
from telegram import Bot, InputFile

TOKEN = "6165593766:AAG5NqL3uaaURcIbce6sYHVn30rYcOhknWY"  # Замените на свой токен Telegram
bot = Bot(token=TOKEN)

# URL для запросов к Zen API
ZEN_URL = "https://dzen.ru/api/v3/launcher/export"

# Каналы для копирования новостей
channels = ["popsci", "nplus1", "naukatv", "scfh", "uralscience", "nakedscience", "techinsider", "astronews", "hi-news.ru", "deep_cosmos"]

# Список для хранения новостей
news_list = []

# Функция для получения постов Zen по имени канала
async def get_zen_posts(channel):
    # Подготовьте параметры запроса
    params = {
        "clid": 300,
        "country_code": "ru",
        "lang": "ru",
        "channel_name": channel
    }
    # Отправьте запрос и получите ответ
    response = requests.get(ZEN_URL, params=params)
    # Проверьте статус ответа
    if response.status_code == 200:
        # Преобразуйте ответ в формат JSON
        data = response.json()
        # Извлеките список постов из данных
        posts = data.get("items", [])
        # Верните список постов
        return posts
    else:
        # В случае ошибки верните пустой список
        return []

# Функция для форматирования сообщения с постом Zen
def format_zen_post(post, channel):
    # Извлеките заголовок, ссылку и изображение из поста
    title = post.get("title")
    link = post.get("share_link")
    text = post.get("text")
    image = post.get("image")
    domain_title = post.get("domain_title")
    # Форматируйте текст сообщения с разметкой Markdown
    text1 = f"{title} \n\n{text}\n{domain_title}: {link}\n@sci_popular"
    # Верните текст сообщения и изображение
    return text1, image

# Функция для получения последних 10 новостей из каждого канала и добавления их в список новостей
async def update_news_list():
    for channel in channels:
        posts = await get_zen_posts(channel)
        if posts:
            latest_posts = posts[:10]  # Получите последние 10 постов
            for post in latest_posts:
                if post.get("text"):  # Проверьте, есть ли текст в посте
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
        await update_news_list()  # Обновите список новостей
        news, channel = get_random_news()
        if news and channel:
            text, image = format_zen_post(news, channel)
            if image:
                await bot.send_photo(chat_id="1001365520775", photo=InputFile(image), caption=text)
            else:
                await bot.send_message(chat_id="1001365520775", text=text)
        await asyncio.sleep(3600)  # Подождите 1 час

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(publish_random_news())
