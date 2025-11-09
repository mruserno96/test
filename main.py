# bot.py  -- Safe, webhook-ready, retry + keepalive + video fallback
import os
import asyncio
import logging
import random
from functools import wraps
from aiohttp import web
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes

# ----- CONFIG -----
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g. "https://your-service.onrender.com"
PORT = int(os.getenv("PORT", "8080"))
KEEPALIVE_INTERVAL = int(os.getenv("KEEPALIVE_INTERVAL_SECONDS", str(60 * 5)))  # default 5 min
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "5"))

if not TOKEN or not WEBHOOK_URL:
    raise RuntimeError("Please set TELEGRAM_BOT_TOKEN and WEBHOOK_URL environment variables")

# ----- Safe sample captions (REPLACE with legal/allowed text) -----
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
    "💎 PACKAGE (example placeholders, REPLACE WITH LEGAL INFO)"
)

FIRST_BUTTONS = InlineKeyboardMarkup(
    [[InlineKeyboardButton("Dm For Purchase", url="https://t.me/KGS_BSEB"),
      InlineKeyboardButton("Free Service", url="https://t.me/dating18app")]]
)
SECOND_BUTTONS = FIRST_BUTTONS

# ----- Logging -----
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
logger = logging.getLogger(__name__)

# ----- Retry decorator with exponential backoff + jitter -----
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
                    # exponential backoff with jitter
                    delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
                    jitter = random.uniform(0, delay * 0.2)
                    sleep_for = delay + jitter
                    logger.warning("Error in %s: %s — retry %d/%d after %.1fs", func.__name__, e, attempt, max_attempts, sleep_for)
                    await asyncio.sleep(sleep_for)
        return wrapper
    return deco

# ----- Handlers / safe send functions -----
@retry_backoff()
async def safe_send_photo(bot, chat_id, photo, caption, reply_markup=None):
    return await bot.send_photo(chat_id=chat_id, photo=photo, caption=caption, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

@retry_backoff()
async def safe_send_video(bot, chat_id, video, caption, reply_markup=None):
    """
    Try send_video first. If it fails (common for HTTP/no-https or large/unserved mp4),
    fallback to send_document (Telegram often accepts the same URL as a document).
    This function will raise if both attempts fail (and let retry decorator handle backoff).
    """
    try:
        # try send_video first (supports_streaming may help some servers)
        return await bot.send_video(chat_id=chat_id, video=video, caption=caption, reply_markup=reply_markup, parse_mode=ParseMode.HTML, supports_streaming=True)
    except Exception as e_video:
        logger.warning("send_video failed for %s: %s — attempting send_document fallback", video, e_video)
        try:
            # fallback to document (works more reliably for some hosts and mime types)
            return await bot.send_document(chat_id=chat_id, document=video, caption=caption, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        except Exception as e_doc:
            # log both exceptions for debugging and then raise to allow retries
            logger.exception("send_document fallback also failed for %s. video_error=%s document_error=%s", video, e_video, e_doc)
            raise

async def start(update, context: ContextTypes.DEFAULT_TYPE):
    """Send first photo+buttons then video+buttons (with safe retries)."""
    chat_id = update.effective_chat.id
    try:
        await safe_send_photo(context.bot, chat_id, FIRST_IMAGE_URL, FIRST_CAPTION, reply_markup=FIRST_BUTTONS)
        # small pause so ordering is maintained and to avoid flood limits
        await asyncio.sleep(0.7)
        await safe_send_video(context.bot, chat_id, SECOND_VIDEO_URL, SECOND_CAPTION, reply_markup=SECOND_BUTTONS)
    except Exception:
        logger.exception("Failed to deliver start messages to %s", chat_id)

async def ping_cmd(update, context):
    await update.message.reply_text("Pong ✅")

# ----- Background keepalive task (self-ping) -----
async def keepalive_task(app: Application):
    """Periodically call the /health endpoint to keep container awake."""
    url = os.environ.get("KEEPALIVE_URL") or f"{WEBHOOK_URL.rstrip('/')}/health"
    logger.info("Keepalive task will ping %s every %ds", url, KEEPALIVE_INTERVAL)
    # Use a dedicated aiohttp ClientSession to avoid using internals
    import aiohttp
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(url) as r:
                    logger.debug("Keepalive ping status: %s", r.status)
            except Exception as e:
                logger.warning("Keepalive ping failed: %s", e)
            await asyncio.sleep(KEEPALIVE_INTERVAL)

# ----- Webhook / Aiohttp server for Telegram updates + health endpoint -----
async def handle_health(request):
    return web.Response(text="ok")

async def on_startup(app: Application):
    webhook_url = WEBHOOK_URL.rstrip("/") + f"/webhook/{TOKEN}"
    logger.info("Setting webhook to %s", webhook_url)
    await app.bot.set_webhook(webhook_url)
    # start keepalive background task
    app.create_task(keepalive_task(app))

async def on_shutdown(app: Application):
    try:
        await app.bot.delete_webhook()
        logger.info("Webhook removed")
    except Exception as e:
        logger.warning("Error removing webhook: %s", e)

def build_aiohttp_app(application: Application):
    aio_app = web.Application()
    aio_app.router.add_post(f"/webhook/{TOKEN}", application.update_queue.put)
    aio_app.router.add_get("/health", handle_health)
    return aio_app

# ----- Main startup -----
def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ping", ping_cmd))

# Register lifecycle callbacks
application.post_init.append(on_startup)
application.post_shutdown.append(on_shutdown)

# Run as webhook (Render provides HTTPS). We bind to PORT and let Telegram call /webhook/<TOKEN>.
listen_addr = "0.0.0.0"
logger.info("Starting webhook on port %s", PORT)
application.run_webhook(
    listen=listen_addr,
    port=PORT,
    url_path=f"webhook/{TOKEN}",
    webhook_url=WEBHOOK_URL.rstrip("/") + f"/webhook/{TOKEN}",
)


if __name__ == "__main__":
    main()
