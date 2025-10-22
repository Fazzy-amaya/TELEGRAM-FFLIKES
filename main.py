import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message, Update
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from flask import Flask, request
import aiohttp
import threading
import json
from datetime import datetime, timedelta

API_TOKEN = "8321209822:AAG3ryvGXpWXMYemRnn6o8yifwTXXDcFjns"
WEBHOOK_URL = "https://telegram-fflikes.onrender.com/webhook"  # your Render URL

bot = Bot(API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
app = Flask(__name__)

# === Bot logic (same as yours, not repeated here) ===
# ... keep your existing command handlers etc. unchanged ...

@app.route("/")
def home():
    return "✅ FazzyBot is running with webhook!"

@app.route("/webhook", methods=["POST"])
async def webhook():
    try:
        data = request.get_data().decode("utf-8")
        update = Update.model_validate_json(data)
        await dp.feed_update(bot, update)
    except Exception as e:
        print(f"Error handling update: {e}")
    return "OK"

async def set_webhook():
    await bot.set_webhook(WEBHOOK_URL)

async def run_async_tasks():
    print("🤖 FazzyBot starting...")
    asyncio.create_task(daily_reset_scheduler())
    await set_webhook()

# Start Flask in main thread
if __name__ == "__main__":
    asyncio.run(run_async_tasks())
    app.run(host="0.0.0.0", port=10000)
