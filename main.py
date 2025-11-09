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
SECOND_CAPTION = """💎 𝗣𝗔𝗖𝗞𝗔𝗚𝗘 1.O 💎

- A1) 𝗖𝗣 𝗟𝗜𝗧𝗧𝗟𝗘 𝗟𝗨𝗦𝗧 (𝗚𝗢𝗟𝗗) 
- A2) 𝗖𝗣 + 𝗣𝗘𝗗𝗢 (𝗚𝗢𝗟𝗗)  
- A3) 𝗖𝗣 𝗜𝗡𝗗𝗜𝗔𝗡 + 𝗙𝗢𝗥𝗘𝗜𝗚𝗡 (𝗚𝗢𝗟𝗗)  
- A4) 𝗠𝗜𝗫𝗘𝗗 𝗖𝗣 (𝗚𝗢𝗟𝗗)  
- A5) 𝗖𝗣 14+ (𝗚𝗢𝗟𝗗)  
- A6) 𝗠𝗔𝗟𝗟𝗨 𝗖𝗣 (𝗚𝗢𝗟𝗗)  
- A7) 𝗖𝗣 𝗜𝗡𝗗𝗢𝗡𝗘𝗦𝗜𝗔 (𝗚𝗢𝗟𝗗)  
- A8) 𝗙𝗔𝗠𝗜𝗟𝗬 𝗖𝗣 (𝗚𝗢𝗟𝗗)  
- A9) 𝗟𝗢𝗡𝗚 𝗧𝗜𝗠𝗘 𝗖𝗣 (𝗚𝗢𝗟𝗗)  
- A10) 𝗪𝗛𝗜𝗧𝗘 𝗖𝗣 (𝗚𝗢𝗟𝗗)  
- A11) 𝗖𝗣 𝗟𝗜𝗙𝗘 (𝗚𝗢𝗟𝗗)  
- A12) 𝗖𝗣 𝗧33𝗡𝗦 𝗕𝗔𝗕𝗘𝗦 (𝗚𝗢𝗟𝗗)
- A13) 𝗖𝗣 𝗕𝗥𝗢-𝗦𝗜𝗦 (𝗚𝗢𝗟𝗗)  
- A14) 𝗧33𝗡𝗦 𝗖𝗣 𝗠𝗜𝗫 (𝗚𝗢𝗟𝗗)  
- A15) 𝗖𝗣 𝗕𝗟𝗢𝗪𝗝𝗢𝗕 (𝗚𝗢𝗟𝗗)
- A16) 𝗜𝗡𝗗𝗜𝗔𝗡 𝗣𝗘𝗗𝗢 𝗖𝗣 (𝗚𝗢𝗟𝗗)
- A17) 𝗖𝗛𝗜𝗡𝗘𝗦𝗘 𝗖𝗣 (𝗚𝗢𝗟𝗗)  
- A18) 𝗖𝗣 𝗚𝗔𝗬 (𝗚𝗢𝗟𝗗)
- A19) 𝗚𝗢𝗟𝗗𝗘𝗡 𝗖𝗣
- A20) 𝗖𝗣 𝗥𝗘𝗔𝗟 𝗦𝗠𝗜𝗧𝗛 (𝗚𝗢𝗟𝗗)
- A21) 𝗖𝗣 𝗟𝗜𝗧𝗧𝗟𝗘 𝗧𝗪𝗜𝗡𝗞𝗟𝗘 (𝗚𝗢𝗟𝗗) 
- A22) 𝗖𝗣 𝗧33𝗡𝗦 (𝗚𝗢𝗟𝗗)  
- A23) 𝗖𝗣 𝗛𝗢𝗥𝗡𝗘𝗬 𝗦𝗜𝗦𝗧𝗘𝗥𝗦 (𝗚𝗢𝗟𝗗)  
- A24) 𝗖𝗣 𝗩𝗜𝗥𝗔𝗟 𝗜𝗡𝗗𝗜𝗔𝗡 (𝗚𝗢𝗟𝗗)  
- A25) 𝗖𝗣 𝗖𝗥𝗢𝗪𝗡 𝗔𝗥𝗖 (𝗚𝗢𝗟𝗗)  
- A26) 𝗖𝗣 𝗣𝗘𝗗𝗢 (𝗚𝗢𝗟𝗗)  
- A27) 𝗖𝗣 𝗟𝗜𝗧𝗧𝗟𝗘 𝗨𝗡𝗜𝗖𝗢𝗥𝗡 (𝗚𝗢𝗟𝗗)  
- A28) 𝗖𝗣 𝗜𝗡𝗗𝗜𝗔𝗡 𝗧𝗢𝗨𝗖𝗛 (𝗚𝗢𝗟𝗗)  
- A29) 𝗖𝗣 𝗖𝗨𝗧𝗘𝗡 𝗖𝗥𝗨𝗦𝗧 (𝗚𝗢𝗟𝗗) 
- A30) 𝗖𝗣 𝗙𝗢𝗥𝗘𝗜𝗚𝗡 𝗝𝗔𝗣𝗔𝗡𝗘𝗦𝗘 (𝗚𝗢𝗟𝗗

━━━━━━━༺💎༻━━━━━━
✅ SAMPLE 👉 

https://t.me/dating18app

💵 PRICE > 999₹ 
Pay Here - @KGS_BSEB
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
