# bot.py
import os
import logging
import asyncio
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler

# ---------- Configuration ----------
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("Please set the TELEGRAM_BOT_TOKEN environment variable")

FIRST_IMAGE_URL = "https://trendpayexchange.wuaze.com/image/phototg.jpg"
FIRST_CAPTION = """Hey Guys It's All Viral Trend 😈 😀

IF YOU'RE INTERESTED IN ANY CHANNEL⭐️
📌 DM ME WHICH CHANNEL YOU WANT 
📌 AND YOUR PREFERRED PAYMENT METHOD ✉️

ADMIN :- @KGS_BSEB

Dm Here For More information

Dive into your next adventure with us! 🚀☺️
"""

FIRST_BUTTONS = [
    [
        InlineKeyboardButton(text="Dm For Purchhase", url="https://t.me/KGS_BSEB"),
        InlineKeyboardButton(text="Free Service", url="https://t.me/dating18app"),
    ]
]

SECOND_VIDEO_URL = "http://trendpayexchange.wuaze.com/image/videotg.mp4"
SECOND_CAPTION = """✅ SAMPLE 👉

https://t.me/bbypreview18bot?start=NTYsODYrQVJZQkw=

💵 PRICE > 999₹
Pay Here - @Nikksuplier
"""

SECOND_BUTTONS = [
    [
        InlineKeyboardButton(text="Dm For Purchhase", url="https://t.me/KGS_BSEB"),
        InlineKeyboardButton(text="Free Service", url="https://t.me/dating18app"),
    ]
]

# ---------- Logging ----------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# ---------- Handlers ----------
async def start(update, context):
    """Handle /start: send photo+buttons then video+buttons"""
    try:
        chat_id = update.effective_chat.id

        # Send first image + caption + buttons
        keyboard1 = InlineKeyboardMarkup(FIRST_BUTTONS)
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=FIRST_IMAGE_URL,
            caption=FIRST_CAPTION,
            reply_markup=keyboard1,
            parse_mode=ParseMode.HTML,
        )

        # Small pause so Telegram orders stay consistent and user sees first message first
        await asyncio.sleep(0.6)

        # Send video + caption + buttons
        keyboard2 = InlineKeyboardMarkup(SECOND_BUTTONS)
        await context.bot.send_video(
            chat_id=chat_id,
            video=SECOND_VIDEO_URL,
            caption=SECOND_CAPTION,
            reply_markup=keyboard2,
            parse_mode=ParseMode.HTML,
        )

    except Exception as e:
        logger.exception("Error in /start handler: %s", e)


# Optional health check command
async def ping(update, context):
    await update.message.reply_text("Pong ✅")


# ---------- Bot startup ----------
def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ping", ping))

    # Run the bot (long-polling). On Render you can run this as a worker/process.
    logger.info("Bot starting (polling)...")
    application.run_polling(allowed_updates=None)


if __name__ == "__main__":
    main()
