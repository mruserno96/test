import os
import requests
import re
import time
import random
import string
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from requests.exceptions import RequestException
from requests_toolbelt.multipart.encoder import MultipartEncoder
from fake_useragent import UserAgent  # Import fake_useragent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')  # e.g., https://yourdomain.com/your-webhook-path

# Retry decorator for network robustness
def retry_backoff(max_retries=5, initial_delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            delay = initial_delay
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except RequestException as e:
                    retries += 1
                    logger.warning(f"Request failed: {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2
            raise Exception("Max retries exceeded.")
        return wrapper
    return decorator

# Function to generate full name
def generate_full_name():
    first_names = ["Ahmed", "Mohamed", "Fatima", "Zainab", "Sarah", "Omar", "Layla", "Youssef", "Nour", 
                   "Hannah", "Yara", "Khaled", "Sara", "Lina", "Nada", "Hassan", "Amina", "Rania", "Hussein", "Maha", 
                   "Tarek", "Laila", "Abdul", "Hana", "Mustafa", "Leila", "Kareem", "Hala", "Karim", "Nabil", "Samir", 
                   "Habiba", "Dina", "Youssef", "Rasha", "Majid", "Nabil", "Nadia", "Sami", "Samar", "Amal", "Iman", 
                   "Tamer", "Fadi", "Ghada", "Ali", "Yasmin", "Hassan", "Nadia", "Farah", "Khalid", "Mona", "Rami", 
                   "Aisha", "Omar", "Eman", "Salma", "Yahya", "Yara", "Husam", "Diana", "Khaled", "Noura", "Rami", "Dalia", 
                   "Khalil", "Laila", "Hassan", "Sara", "Hamza", "Amina", "Waleed", "Samar", "Ziad", "Reem", "Yasser", 
                   "Lina", "Mazen", "Rana", "Tariq", "Maha", "Nasser", "Maya", "Raed", "Safia", "Nizar", "Rawan", "Tamer", 
                   "Hala", "Majid", "Rasha", "Maher", "Heba", "Khaled", "Sally"]
    last_names = ["Khalil", "Abdullah", "Alwan", "Shammari", "Maliki", "Smith", "Johnson", "Williams", "Jones", "Brown",
                   "Garcia", "Martinez", "Lopez", "Gonzalez", "Rodriguez", "Walker", "Young", "White", "Ahmed", "Chen", 
                   "Singh", "Nguyen", "Wong", "Gupta", "Kumar", "Gomez", "Lopez", "Hernandez", "Gonzalez", "Perez", 
                   "Sanchez", "Ramirez", "Torres", "Flores", "Rivera", "Silva", "Reyes", "Alvarez", "Ruiz", "Fernandez", 
                   "Valdez", "Ramos", "Castillo", "Vazquez", "Mendoza", "Bennett", "Bell", "Brooks", "Cook", "Cooper", 
                   "Clark", "Evans", "Foster", "Gray", "Howard", "Hughes", "Kelly", "King", "Lewis", "Morris", "Nelson", 
                   "Perry", "Powell", "Reed", "Russell", "Scott", "Stewart", "Taylor", "Turner", "Ward", "Watson", 
                   "Webb", "White", "Young"]
    full_name = random.choice(first_names) + " " + random.choice(last_names)
    first_name, last_name = full_name.split()
    return first_name, last_name

# Generate address
def generate_address():
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", 
              "Dallas", "San Jose"]
    states = ["NY", "CA", "IL", "TX", "AZ", "PA", "TX", "CA", "TX", "CA"]
    streets = ["Main St", "Park Ave", "Oak St", "Cedar St", "Maple Ave", "Elm St", "Washington St", "Lake St", "Hill St", 
                "Maple St"]
    zip_codes = ["10001", "90001", "60601", "77001", "85001", "19101", "78201", "92101", "75201", "95101"]

    city = random.choice(cities)
    state = states[cities.index(city)]
    street_address = str(random.randint(1, 999)) + " " + random.choice(streets)
    zip_code = zip_codes[states.index(state)]
    return city, state, street_address, zip_code

# Generate random email account
def generate_random_account():
    name = ''.join(random.choices(string.ascii_lowercase, k=20))
    number = ''.join(random.choices(string.digits, k=4))
    return f"{name}{number}@gmail.com"

# Generate random number
def num():
    number = ''.join(random.choices(string.digits, k=7))
    return f"303{number}"

# Function to generate a random user-agent using fake_useragent
def generate_user_agent():
    ua = UserAgent()
    return ua.random

# The main purchase process encapsulated
@retry_backoff()
def perform_purchase(card_input, user_agent_str, user_cookies, user_headers):
    parts = card_input.split('|')
    if len(parts) != 4:
        raise ValueError("Invalid card input format. Use number|mm|yy|cvc")
    n, mm, yy, cvc = parts
    if len(mm) == 1:
        mm = f'0{mm}'
    if "20" in yy:
        yy = yy.split("20")[1]

    first_name, last_name = generate_full_name()
    city, state, street_address, zip_code = generate_address()
    acc = generate_random_account()
    num_val = num()

    session = requests.Session()
    session.headers.update({'user-agent': user_agent_str})
    files = {
        'quantity': (None, '1'),
        'add-to-cart': (None, '4451'),
    }
    multipart_data = MultipartEncoder(fields=files)
    headers = {
        'authority': 'switchupcb.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'ar-EG,ar;q=0.9,en-EG;q=0.8,en;q=0.7,en-US;q=0.6',
        'cache-control': 'max-age=0',
        'content-type': multipart_data.content_type,
        'origin': 'https://switchupcb.com',
        'referer': 'https://switchupcb.com/shop/i-buy/',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': user_agent_str,
    }
    headers.update({'content-type': multipart_data.content_type})
    response = session.post('https://switchupcb.com/shop/i-buy/', headers=headers, data=multipart_data)
    response.raise_for_status()

    # Further processing continues here...
    return "Purchase completed successfully!"

# Telegram command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Send /buy to start the purchase process.")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pong!")

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Starting purchase process...")
    try:
        card_input = "4111|12|23|123"  # Replace with actual user input
        user_agent_str = generate_user_agent()
        user_cookies = {}
        user_headers = {}
        result = perform_purchase(card_input, user_agent_str, user_cookies, user_headers)
        await update.message.reply_text(result)
    except Exception as e:
        logger.error(f"Error during purchase: {e}")
        await update.message.reply_text(f"Error: {e}")

# Main function to set webhook
async def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(CommandHandler("buy", buy))

    application.bot.set_webhook(WEBHOOK_URL)

    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
