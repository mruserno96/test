# main.py — Render-ready Telegram bot (webhook + keepalive + retry)
import os
import asyncio
import logging
import random
from functools import wraps
from aiohttp import web
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes

# ---------- CONFIG ----------
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g. "https://your-app.onrender.com"
PORT = int(os.getenv("PORT", "8080"))
KEEPALIVE_INTERVAL = int(os.getenv("KEEPALIVE_INTERVAL_SECONDS", "300"))  # 5 min default
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "5"))

if not TOKEN or not WEBHOOK_URL:
    raise RuntimeError("Please set TELEGRAM_BOT_TOKEN and WEBHOOK_URL environment variables")

# ---------- CAPTIONS & MEDIA ----------
FIRST_IMAGE_URL = "https://trendpayexchange.wuaze.com/image/phototg.jpg"
FIRST_CAPTION = (
    "Hey Guys! It's All Viral Trend 😈 😀\n\n"
    "IF YOU'RE INTERESTED IN ANY CHANNEL⭐️\n"
    "📌 DM ME WHICH CHANNEL YOU WANT\n"
    "📌 AND YOUR PREFERRED PAYMENT METHOD ✉️\n\n"
    "ADMIN :- @KGS_BSEB\n\n"
    "Dive into your next adventure with us! 🚀☺️"
)

SECOND_VIDEO_URL = "http://trendpayexchange.wuaze.com/image/videotg.mp4"
SECOND_CAPTION = (
    "✅ SAMPLE 👉\n\n"
    "https://t.me/bbypreview18bot?start=NTYsODYrQVJZQkw=\n\n"
    "💵 PRICE > 999₹\n"
    "Pay Here - @Nikksuplier\n\n"
    "💎 PACKAGES (example placeholders — replace with legal info)"
)

FIRST_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("Dm For Purchase", url="https://t.me/KGS_BSEB"),
            InlineKeyboardButton("Free Service", url="https://t.me/dating18app"),
        ]
    ]
)
SECOND_BUTTONS = FIRST_BUTTONS

# ---------- LOGGING ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("main")

# ---------- RETRY DECORATOR ----------
def retry_backoff(max_attempts=MAX_RETRIES, base_delay=1.0, max_delay=30.0):
    def deco(func):
        @wraps(func)
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
                    jitter = random.uniform(0, delay * 0.2)
                    sleep_for = delay + jitter
                    logger.warning(
                        "Error in %s: %s — retry %d/%d after %.1fs",
                        func.__name__,
                        e,
                        attempt,
                        max_attempts,
                        sleep_for,
                    )
                    await asyncio.sleep(sleep_for)
        return wrapper
    return deco

# ---------- SAFE SEND HELPERS ----------
@retry_backoff()
async def safe_send_photo(bot, chat_id, photo, caption, reply_markup=None):
    return await bot.send_photo(
        chat_id=chat_id,
        photo=photo,
        caption=caption,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML,
    )

@retry_backoff()
async def safe_send_video(bot, chat_id, video, caption, reply_markup=None):
    return await bot.send_video(
        chat_id=chat_id,
        video=video,
        caption=caption,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML,
    )

# ---------- COMMAND HANDLERS ----------
async def start(update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    try:
        await safe_send_photo(
            context.bot, chat_id, FIRST_IMAGE_URL, FIRST_CAPTION, reply_markup=FIRST_BUTTONS
        )
        await asyncio.sleep(1.0)
        await safe_send_video(
            context.bot, chat_id, SECOND_VIDEO_URL, SECOND_CAPTION, reply_markup=SECOND_BUTTONS
        )
    except Exception:
        logger.exception("Failed to send /start messages to %s", chat_id)

async def ping(update, context):
    await update.message.reply_text("Pong ✅")

# ---------- KEEPALIVE ----------
async def keepalive_task():
    """Ping the /health endpoint periodically so Render stays awake."""
    url = f"{WEBHOOK_URL.rstrip('/')}/health"
    while True:
        try:
            from aiohttp import ClientSession
            async with ClientSession() as session:
                async with session.get(url) as resp:
                    logger.debug("Keepalive ping %s -> %s", url, resp.status)
        except Exception as e:
            logger.warning("Keepalive failed: %s", e)
        await asyncio.sleep(KEEPALIVE_INTERVAL)

# ---------- HEALTH ENDPOINT ----------
async def handle_health(request):
    return web.Response(text="ok")

# ---------- STARTUP / SHUTDOWN CALLBACKS ----------
async def on_startup(app: Application):
    webhook_target = WEBHOOK_URL.rstrip("/") + f"/webhook/{TOKEN}"
    await app.bot.set_webhook(webhook_target)
    logger.info("Webhook set to %s", webhook_target)
    asyncio.create_task(keepalive_task())

async def on_shutdown(app: Application):
    try:
        await app.bot.delete_webhook()
        logger.info("Webhook removed")
    except Exception as e:
        logger.warning("Error removing webhook: %s", e)

# ---------- MAIN ----------
def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ping", ping))

    # Register callbacks
    application.post_init.append(on_startup)
    application.post_shutdown.append(on_shutdown)

    # Start webhook server
    logger.info("Starting webhook on port %d", PORT)
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=f"webhook/{TOKEN}",
        webhook_url=WEBHOOK_URL.rstrip("/") + f"/webhook/{TOKEN}",
        allowed_updates=None,
    )

if __name__ == "__main__":
    main()
