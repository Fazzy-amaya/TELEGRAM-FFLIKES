import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message, Update
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from flask import Flask, request
import threading

# === Your bot settings ===
API_TOKEN = "8321209822:AAG3ryvGXpWXMYemRnn6o8yifwTXXDcFjns"
WEBHOOK_URL = "https://telegram-fflikes.onrender.com/webhook"

# === Bot setup ===
bot = Bot(API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# === Flask app ===
app = Flask(__name__)

# === Telegram command handlers ===
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("👋 Welcome to FazzyBot!\nUse /help to see what I can do.")

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "🛠️ Commands:\n"
        "/start - Welcome message\n"
        "/help - Show help info\n"
        "/like bd <number> - Like a specific BD"
    )

@dp.message(Command("like"))
async def cmd_like(message: Message):
    text = message.text.strip()
    if text.startswith("/like bd "):
        bd_number = text.replace("/like bd ", "").strip()
        if bd_number.isdigit():
            await message.answer(f"👍 BD {bd_number} liked successfully.")
        else:
            await message.answer("❌ Invalid BD number.")
    else:
        await message.answer("❓ Unknown like format. Use /like bd <number>")

# === Flask route: must be sync ===
@app.route("/", methods=["GET"])
def home():
    return "✅ FazzyBot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_data().decode("utf-8")
        update = Update.model_validate_json(data)
        loop = asyncio.get_event_loop()
        loop.create_task(dp.feed_update(bot, update))
    except Exception as e:
        print(f"Webhook Error: {e}")
    return "OK"

# === Webhook registration ===
async def setup_webhook():
    await bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Webhook set: {WEBHOOK_URL}")

# === Startup tasks ===
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(setup_webhook())

# === Main ===
