import asyncio
import aiohttp
import threading
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from datetime import datetime, timedelta
from flask import Flask

# === Telegram Bot Setup ===
API_TOKEN = "8321209822:AAFQZ_tzIW2jJe2eUDkpuz-JIUjXAr4mZLc"
ALLOWED_GROUP_ID = -100290233316
VIP_USER_ID = 7431583417

bot = Bot(API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# === Flask app (Render keeps it alive) ===
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Telegram Bot is running successfully on Render!"

# === Bot Logic ===
user_usage = {}
like_usage = {"BD": 0, "IND": 0}

def join_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Join Channel", url="https://t.me/FAZZYAMAYA")],
    ])

def vip_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Join Channel", url="https://t.me/FAZZYAMAYA")],
        [InlineKeyboardButton(text="💎 Buy VIP", url="https://t.me/FAZZYAMAYA")],
    ])

def verify_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Verify For Extra Likes", url="https://shortxlinks.in/RTubx")],
    ])

def reset_daily_limits():
    user_usage.clear()
    like_usage["BD"] = 0
    like_usage["IND"] = 0
    print("✅ Daily limits reset.")

async def daily_reset_scheduler():
    while True:
        now = datetime.now()
        next_reset = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
        wait_seconds = (next_reset - now).total_seconds()
        await asyncio.sleep(wait_seconds)
        reset_daily_limits()

async def fetch_json(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            if r.status == 200:
                return await r.json()
    return None

def group_only(func):
    async def wrapper(msg: Message):
        if msg.chat.id != ALLOWED_GROUP_ID:
            return
        return await func(msg)
    return wrapper

@dp.message(Command("like"))
@group_only
async def like_handler(msg: Message):
    parts = msg.text.split()
    if len(parts) != 3:
        await msg.reply("❗ Correct format: /like bd uid", reply_markup=join_keyboard())
        return
    region, uid = parts[1].upper(), parts[2]
    if region not in ["BD", "IND"]:
        await msg.reply("❗ Only BD or IND regions are supported!", reply_markup=join_keyboard())
        return

    user_id = msg.from_user.id
    if user_id != VIP_USER_ID:
        count = user_usage.get(user_id, {}).get("like", 0)
        if count >= 1:
            await msg.reply("🚫 You have already used your like command today!", reply_markup=verify_keyboard())
            return

    if like_usage[region] >= 30 and user_id != VIP_USER_ID:
        await msg.reply(
            f"⚠️ Daily like limit reached for {region} region. Please try again tomorrow.",
            reply_markup=join_keyboard()
        )
        return

    wait = await msg.reply("⏳ Sending Likes, Please Wait.....")
    url = f"https://fazzyamaya.onrender.com/like/like?server_name={region.lower()}&uid={uid}&key=DANGERxGAMER"
    data = await fetch_json(url)

    if not data:
        await wait.edit_text("❌ Failed to send request. Check UID or try later.", reply_markup=join_keyboard())
        return

    if data.get("status") == 2:
        await wait.edit_text(
            f"🚫 Max Likes Reached for Today\n\n"
            f"👤 Name: {data.get('PlayerNickname', 'N/A')}\n"
            f"🆔 UID: {uid}", reply_markup=join_keyboard()
        )
        return

    await wait.edit_text(
        f"✅ Successfully Sent Likes!\n\n"
        f"👤 Name: {data.get('PlayerNickname', 'N/A')}\n"
        f"🆔 UID: {uid}\n"
        f"🌍 Region: {region}", reply_markup=vip_keyboard()
    )

    user_usage.setdefault(user_id, {})["like"] = user_usage.get(user_id, {}).get("like", 0) + 1
    like_usage[region] += 1


# === Async Bot Runner ===
async def run_bot():
    asyncio.create_task(daily_reset_scheduler())
    print("🚀 Telegram bot started successfully!")
    await dp.start_polling(bot)


# === Thread wrapper for bot (so Flask stays alive) ===
def start_bot_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bot())


if __name__ == "__main__":
    threading.Thread(target=start_bot_thread, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
