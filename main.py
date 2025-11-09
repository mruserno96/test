# main.py
import os
import asyncio
import logging
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes
from aiohttp import ClientSession

# ---------------- CONFIG ----------------
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g. https://your-app.onrender.com
PORT = int(os.getenv("PORT", "8080"))
KEEPALIVE_INTERVAL = int(os.getenv("KEEPALIVE_INTERVAL_SECONDS", "300"))  # 5 minutes
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "5"))

if not TOKEN or not WEBHOOK_URL:
    raise RuntimeError("Please set TELEGRAM_BOT_TOKEN and WEBHOOK_URL environment variables.")

# ---------------- CONTENT ----------------
FIRST_IMAGE_URL = "https://trendpayexchange.wuaze.com/image/phototg.jpg"
FIRST_CAPTION = """Hey Guys It's All Viral Trend 😈 😀

IF YOU'RE INTERESTED IN ANY CHANNEL⭐️
📌 DM ME WHICH CHANNEL YOU WANT 
📌 AND YOUR PREFERRED PAYMENT METHOD ✉️

ADMIN :- @KGS_BSEB

Dm Here For More information

Dive into your next adventure with us! 🚀☺️
"""

SECOND_VIDEO_URL = "http://trendpayexchange.wuaze.com/image/videotg.mp4"
SECOND_CAPTION = """✅ SAMPLE 👉

https://t.me/bbypreview18bot?start=NTYsODYrQVJZQkw=

💵 PRICE > 999₹
Pay Here - @Nikksuplier

💎 PACKAGE LIST 💎
(Replace with your legal info or service list)
"""

FIRST_BUTTONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("Dm For Purchase", url="https://t.me/KGS_BSEB"),
        InlineKeyboardButton("Free Service", url="https://t.me/dating18app")
    ]
])
SECOND_BUTTONS = FIRST_BUTTONS

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("bot")

# ---------------- RETRY DECORATOR ----------------
def retry_backoff(max_attempts=MAX_RETRIES, base_delay=1.0, max_delay=30.0):
    def deco(func):
        async def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.exception("Max retries reached for %s", func.__name__)
                        raise
                    delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
                    delay += random.uniform(0, delay * 0.3)
                    logger.warning("Retry %d/%d after %.1fs for %s (%s)",
                                   attempt, max_attempts, delay, func.__name__, e)
                    await asyncio.sleep(delay)
        return wrapper
    return deco

# ---------------- HANDLERS ----------------
@retry_backoff()
async def safe_send_photo(bot, chat_id, photo, caption, reply_markup=None):
    return await bot.send_photo(chat_id=chat_id, photo=photo, caption=caption,
                                reply_markup=reply_markup, parse_mode=ParseMode.HTML)

@retry_backoff()
async def safe_send_video(bot, chat_id, video, caption, reply_markup=None):
    return await bot.send_video(chat_id=chat_id, video=video, caption=caption,
                                reply_markup=reply_markup, parse_mode=ParseMode.HTML)

async def start(update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    try:
        await safe_send_photo(context.bot, chat_id, FIRST_IMAGE_URL, FIRST_CAPTION, reply_markup=FIRST_BUTTONS)
        await asyncio.sleep(0.8)
        await safe_send_video(context.bot, chat_id, SECOND_VIDEO_URL, SECOND_CAPTION, reply_markup=SECOND_BUTTONS)
    except Exception as e:
        logger.exception("Error sending messages to %s: %s", chat_id, e)

async def ping(update, context):
    await update.message.reply_text("Pong ✅")

# ---------------- KEEPALIVE ----------------
async def keepalive_task():
    url = WEBHOOK_URL.rstrip("/") + "/health"
    async with ClientSession() as session:
        while True:
            try:
                async with session.get(url) as resp:
                    logger.info("Keepalive ping: %s", resp.status)
            except Exception as e:
                logger.warning("Keepalive failed: %s", e)
            await asyncio.sleep(KEEPALIVE_INTERVAL)

# ---------------- MAIN ----------------
def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ping", ping))

    async def startup():
        # Set webhook
        webhook_full = WEBHOOK_URL.rstrip("/") + f"/webhook/{TOKEN}"
        await application.bot.set_webhook(webhook_full)
        logger.info("Webhook set: %s", webhook_full)
        asyncio.create_task(keepalive_task())

    # Start webhook listener
    logger.info("Starting webhook on port %d", PORT)
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=f"webhook/{TOKEN}",
        webhook_url=WEBHOOK_URL.rstrip("/") + f"/webhook/{TOKEN}",
        allowed_updates=None,
        stop_signals=None,
        bootstrap_retries=MAX_RETRIES,
    )

    # Launch keepalive separately
    asyncio.get_event_loop().create_task(startup())

if __name__ == "__main__":
    main()
