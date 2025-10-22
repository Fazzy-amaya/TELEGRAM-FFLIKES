import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message, Update
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from flask import Flask, request
import threading
from datetime import datetime, timedelta

# === Your settings ===
API_TOKEN = "8321209822:AAG3ryvGXpWXMYemRnn6o8yifwTXXDcFjns"
WEBHOOK_URL = "https://telegram-fflikes.onrender.com/webhook"

# === Bot + Dispatcher ===
bot = Bot(API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# === Flask app ===
app = Flask(__name__)

# === Command handlers ===
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("👋 Welcome to FazzyBot!\nUse /help to see what I can do.")

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "🛠️ Available commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/like bd <number> - Like a specific BD"
    )

@dp.message(Command("like"))
async def cmd_like(message: Message):
    text = message.text.strip()
    if text.startswith("/like bd "):
        bd_value = text.replace("/like bd ", "").strip()
        if bd_value.isdigit():
            await message.answer(f"👍 BD {bd_value} liked successfully.")
        else:
            await message.answer("❌ Invalid BD number.")
    else:
        await message.answer("❓ Unknown like command format. Use /like bd <number>")

# === Flask routes ===
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

# === Webhook setup ===
async def set_webhook():
    await bot.set_webhook(WEBHOOK_URL)

async def run_async_tasks():
    print("🤖 FazzyBot starting...")
    await set_webhook()
    # If you have other async startup tasks, add them here (e.g., schedulers)

# === Main ===
if __name__ == "__main__":
    asyncio.run(run_async_tasks())
    app.run(host="0.0.0.0", port=10000)
