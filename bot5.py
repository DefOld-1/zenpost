from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import requests
import random
import asyncio

TOKEN = "6165593766:AAG5NqL3uaaURcIbce6sYHVn30rYcOhknWY"  # Replace with your actual token
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# URL for Zen API requests
ZEN_URL = "https://dzen.ru/api/v3/launcher/export"

# Channels to copy news from
channels = ["popsci", "nplus1", "naukatv", "scfh", "uralscience", "nakedscience", "techinsider", "astronews", "hi-news.ru", "deep_cosmos"]

# List to store the news
news_list = []

# Function to get Zen posts by channel name
def get_zen_posts(channel):
    # Prepare request parameters
    params = {
        "clid": 300,
        "country_code": "ru",
        "lang": "ru",
        "channel_name": channel
    }
    # Send request and get response
    response = requests.get(ZEN_URL, params=params)
    # Check response status
    if response.status_code == 200:
        # Convert response to JSON format
        data = response.json()
        # Extract list of posts from the data
        posts = data.get("items", [])
        # Return the list of posts
        return posts
    else:
        # Return an empty list in case of an error
        return []

# Function to format a message with a Zen post
def format_zen_post(post, channel):
    # Extract title, link, and image from the post
    title = post.get("title")
    link = post.get("share_link")
    text = post.get("text")
    image = post.get("image")
    domain_title = post.get("domain_title")
    # Format the message text with Markdown markup
    #text1 = f"{title} \n \n {text} \n {link} \n \n@sci_popular"
    text1 = f"{title} \n \n{text}\n{domain_title}: {link}\n@sci_popular"
    # Return the message text and image
    return text1, image

# Function to get the latest 10 news from each channel and add them to the news list
def update_news_list():
    for channel in channels:
        posts = get_zen_posts(channel)
        if posts:
            latest_posts = posts[:10]  # Get the latest 10 posts
            for post in latest_posts:
                if post.get("text"):  # Check if the post has text
                    news_list.append((post, channel))

# Function to get a random news from the list
def get_random_news():
    news_with_text = [(news, channel) for news, channel in news_list if news.get("text")]
    if news_with_text:
        news, channel = random.choice(news_with_text)
        news_list.remove((news, channel))
        return news, channel
    else:
        return None, None

# Handler for the /start command
@dp.message_handler(commands=["start"])
async def send_welcome(msg: types.Message):
    await msg.reply("I'm a bot that copies posts from Zen to a Telegram channel. News will be published automatically every hour.")

# Function to publish random news
async def publish_random_news():
    while True:
        update_news_list()  # Update the news list
        news, channel = get_random_news()
        if news and channel:
            text, image = format_zen_post(news, channel)
            if image:
                await bot.send_photo(chat_id="-1001365520775", photo=image, caption=text)
            else:
                await bot.send_message(chat_id="-1001365520775", text=text)
        await asyncio.sleep(3600)  # Wait for 1 hour

# Start the bot and schedule the publishing of news
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(publish_random_news())
    executor.start_polling(dp, loop=loop)