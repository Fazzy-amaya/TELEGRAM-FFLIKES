import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message, Update
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from flask import Flask, request

API_TOKEN = "8321209822:AAG3ryvGXpWXMYemRnn6o8yifwTXXDcFjns"
WEBHOOK_URL = "https://telegram-fflikes.onrender.com/webhook"

bot = Bot(API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
app = Flask(__name__)

@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("👋 Welcome to FazzyBot!\nUse /help to see commands.")

@dp.message(Command("help"))
async def help_handler(message: Message):
    await message.answer("🛠️ Commands:\n/start - Start\n/help - Help\n/like bd <number>")

@dp.message(Command("like"))
async def like_handler(message: Message):
    text = message.text.strip()
    if text.startswith("/like bd "):
        bd_value = text.replace("/like bd ", "").strip()
        if bd_value.isdigit():
            await message.answer(f"👍 BD {bd_value} liked!")
        else:
            await message.answer("❌ Invalid BD number.")
    else:
        await message.answer("❓ Use /like bd <number>")

@app.route("/", methods=["GET"])
def home():
    return "✅ FazzyBot is alive!"

@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    try:
        data = request.get_data().decode("utf-8")
        update = Update.model_validate_json(data)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(dp.feed_update(bot, update))
    except Exception as e:
        print(f"Webhook error: {e}")
    return "OK"

async def setup_webhook():
    await bot.set_webhook(WEBHOOK_URL)
    print("✅ Webhook registered.")

def run_webhook():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(setup_webhook())

if __name__ == "__main__":
    run_webhook()
    app.run(host="0.0.0.0", port=10000)
