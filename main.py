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
import user_agent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name)

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

# Generate address
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

# Generate random email account
def generate_random_account():
    name = ''.join(random.choices(string.ascii_lowercase, k=20))
    number = ''.join(random.choices(string.digits, k=4))
    return f"{name}{number}@gmail.com"

# Generate random number
def num():
    number = ''.join(random.choices(string.digits, k=7))
    return f"303{number}"

# The main purchase process encapsulated
@retry_backoff()
def perform_purchase(card_input, user_agent_str, user_cookies, user_headers):
    # Parse card input
    parts = card_input.split('|')
    if len(parts) != 4:
        raise ValueError("Invalid card input format. Use number|mm|yy|cvc")
    n, mm, yy, cvc = parts
    if len(mm) == 1:
        mm = f'0{mm}'
    if "20" in yy:
        yy = yy.split("20")[1]

    # Generate user info
    first_name, last_name = generate_full_name()
    city, state, street_address, zip_code = generate_address()
    acc = generate_random_account()
    num_val = num()

    session = requests.Session()
    session.headers.update({'user-agent': user_agent_str})
    # First request: add to cart
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

    # Second request: go to checkout
    headers_checkout = {
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
        'user-agent': user_agent_str,
    }
    response2 = session.get('https://switchupcb.com/checkout/', cookies=session.cookies, headers=headers_checkout)
    response2.raise_for_status()

    # Extract tokens with regex
    text = response2.text
    try:
        sec = re.search(r'update_order_review_nonce":"(.*?)"', text).group(1)
        nonce = re.search(r'save_checkout_form.*?nonce":"(.*?)"', text).group(1)
        check = re.search(r'name="woocommerce-process-checkout-nonce" value="(.*?)"', text).group(1)
        create = re.search(r'create_order.*?nonce":"(.*?)"', text).group(1)
    except AttributeError:
        raise RuntimeError("Failed to extract security tokens.")

        # Update order review
    headers_update = {
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
        'user-agent': user_agent_str,
    }
    params = {'wc-ajax': 'update_order_review'}
    data = f"security={sec}&payment_method=stripe&country=US&state={state}&postcode={zip_code}&city={city}&address={street_address}&address_2=&s_country=US&s_state={state}&s_postcode={zip_code}&s_city={city}&s_address={street_address}&s_address_2=&has_full_address=true&post_data=wc_order_attribution_source_type%3Dtypein%26wc_order_attribution_referrer%3D(none)%26wc_order_attribution_utm_campaign%3D(none)%26wc_order_attribution_utm_source%3D(direct)%26wc_order_attribution_utm_medium%3D(none)%26wc_order_attribution_utm_content%3D(none)%26wc_order_attribution_utm_id%3D(none)%26wc_order_attribution_utm_term%3D(none)%26wc_order_attribution_utm_source_platform%3D(none)%26wc_order_attribution_utm_creative_format%3D(none)%26wc_order_attribution_utm_marketing_tactic%3D(none)%26wc_order_attribution_session_entry%3Dhttps%253A%252F%252Fswitchupcb.com%252F%26wc_order_attribution_session_start_time%3D2025-01-15%252016%253A33%253A26%26wc_order_attribution_session_pages%3D15%26wc_order_attribution_session_count%3D1%26wc_order_attribution_user_agent%3DMozilla%252F5.0%2520(Linux%253B%2520Android%252010%253B%2520K)%2520AppleWebKit%252F537.36%2520(KHTML%252C%2520like%2520Gecko)%2520Chrome%252F124.0.0.0%2520Mobile%2520Safari%252F537.36%26billing_first_name%3D{first_name}%26billing_last_name%3D{last_name}%26billing_company%3D%26billing_country%3DUS%26billing_address_1%3D{street_address}%26billing_address_2%3D%26billing_city%3D{city}%26billing_state%3D{state}%26billing_postcode%3D{zip_code}%26billing_phone%3D{num_val}%26billing_email%3D{acc}%26account_username%3D%26account_password%3D%26order_comments%3D%26g-recaptcha-response%3D%26payment_method%3Dstripe%26wc-stripe-payment-method-upe%3D%26wc_stripe_selected_upe_payment_type%3D%26wc-stripe-is-deferred-intent%3D1%26terms-field%3D1%26woocommerce-process-checkout-nonce%3D{check}%26_wp_http_referer%3D%252F%253Fwc-ajax%253Dupdate_order_review"
    response3 = session.post('https://switchupcb.com/', headers=headers_update, params=params, data=data)
    response3.raise_for_status()

    # Create order
    json_payload = {
        'nonce': create,
        'payer': None,
        'bn_code': 'Woo_PPCP',
        'context': 'checkout',
        'order_id': '0',
        'payment_method': 'ppcp-gateway',
        'funding_source': 'card',
        'form_encoded': f"billing_first_name={first_name}&billing_last_name={last_name}&billing_company=&billing_country=US&billing_address_1={street_address}&billing_address_2=&billing_city={city}&billing_state={state}&billing_postcode={zip_code}&billing_phone={num_val}&billing_email={acc}&account_username=&account_password=&order_comments=&wc_order_attribution_source_type=typein&wc_order_attribution_referrer=%28none%29&wc_order_attribution_utm_campaign=%28none%29&wc_order_attribution_utm_source=%28direct%29&wc_order_attribution_utm_medium=%28none%29&wc_order_attribution_utm_content=%28none%29&wc_order_attribution_utm_id=%28none%29&wc_order_attribution_utm_term=%28none%29&wc_order_attribution_session_entry=https%3A%2F%2Fswitchupcb.com%2Fshop%2Fdrive-me-so-crazy%2F&wc_order_attribution_session_start_time=2024-03-15+10%3A00%3A46&wc_order_attribution_session_pages=3&wc_order_attribution_session_count=1&wc_order_attribution_user_agent={user_agent_str}&g-recaptcha-response=&wc-stripe-payment-method-upe=&wc_stripe_selected_upe_payment_type=card&payment_method=ppcp-gateway&terms=on&tems-field=1&woocommerce-process-checkout-nonce={check}&_wp_http_referer=%2F%3Fwc-ajax%3Dupdate_order_review&ppcp-funding-source=card",
        'createaccount': False,
        'save_payment_method': False,
    }
    response4 = session.post('https://switchupcb.com/', headers=headers, params={'wc-ajax': 'ppc-create-order'}, json=json_payload)
    response4.raise_for_status()

    # Extract order id
    res_json = response4.json()
    if 'data' in res_json and 'id' in res_json['data']:
        order_id = res_json['data']['id']
        custom_id = res_json['data'].get('custom_id', '')
    else:
        raise RuntimeError("Failed to get order ID")
    
    # Generate session IDs for PayPal
    lol1 = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    lol2 = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    lol3 = ''.join(random.choices(string.ascii_lowercase + string.digits, k=11))
    session_id = f'uid_{lol1}_{lol3}'
    button_session_id = f'uid_{lol2}_{lol3}'

    # PayPal request for card fields
    headers_paypal = {
        'authority': 'www.paypal.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'ar-EG,ar;q=0.9,en-EG;q=0.8,en;q=0.7,en-US;q=0.6', 
        'referer': 'https://www.paypal.com/smart/buttons?style.label=paypal&style.layout=vertical&style.color=gold&style.shape=rect&style.tagline=false&style.menuPlacement=below&allowBillingPayments=true&applePaySupport=false&buttonSessionID=uid_378e07784c_mtc6nde6ndk&buttonSize=large&customerId=&clientID=AY7TjJuH5RtvCuEf2ZgEVKs3quu69UggsCg29lkrb3kvsdGcX2ljKidYXXHPParmnymd9JacfRh0hzEp&clientMetadataID=uid_b5c925a7b4_mtc6nde6ndk&commit=true&components.0=buttons&components.1=funding-eligibility&currency=USD&debug=false&disableSetCookie=true&enableFunding.0=venmo&enableFunding.1=paylater&env=production&experiment.enableVenmo=true&experiment.venmoVaultWithoutPurchase=false&experiment.venmoWebEnabled=false&flow=purchase&fundingEligibility=eyJwYXlwYWwiOnsiZWxpZ2libGUiOnRydWUsInZhdWx0YWJsZSI6ZmFsc2V9LCJwYXlsYXRlciI6eyJlbGlnaWJsZSI6ZmFsc2UsInZhdWx0YWJsZSI6ZmFsc2UsInByb2R1Y3RzIjp7InBheUluMyI6eyJlbGlnaWJsZSI6ZmFsc2UsInZhcmlhbnQiOm51bGx9LCJwYXlJbjQiOnsiZWxpZ2libGUiOmZhbHNlLCJ2YXJpYW50IjpudWxsfSwicGF5bGF0ZXIiOnsiZWxpZ2libGUiOmZhbHNlLCJ2YXVsdGFibGUiOmZhbHNlfSwiZWxvIjp7ImVsaWdpYmxlIjp0cnVlLCJ2YXVsdGFibGUiOnRydWUsInZhdWx0YWJsZSI6dHJ1ZX0sIm1hc3RlcmNhcmQiOnsiZWxpZ2libGUiOnRydWUsInZhdWx0YWJsZSI6dHJ1ZX0sImFtZXgiOnsiZWxpZ2libGUiOnRydWUsInZhdWx0YWJsZSI6dHJ1ZX0sImRpc2NvdmVyIjp7ImVsaWdpYmxlIjpmYWxzZSwidmF1bHRhYmxlIjp0cnVlfSwiaGlwZXIiOnsiZWxpZ2libGUiOmZhbHNlLCJ2YXVsdGFibGUiOmZhbHNlfSwiZWxvIjp7ImVsaWdpYmxlIjpmYWxzZSwidmF1bHRhYmxlIjp0cnVlfSwiamNiIjp7ImVsaWdpYmxlIjpmYWxzZSwidmF1bHRhYmxlIjp0cnVlfSwiZWxvIjp7ImVsaWdpYmxlIjpmYWxzZSwidmF1bHRhYmxlIjp0cnVlfSwiWJwIjp7ImVsaWdpYmxlIjpmYWxzZX0sIlJmIjp7ImVsaWdpYmxlIjpmYWxzZX0sIlNhdGlzIjp7ImVsaWdpYmxlIjpmYWxzZX0sInBhaWR5Ijp7ImVsaWdpYmxlIjpmYWxzZX19&intent=capture&locale.country=EG&locale.lang=ar&hasShippingCallback=false&pageType=checkout&platform=mobile&renderedButtons.0=paypal&renderedButtons.1=card&sessionID=uid_b5c925a7b4_mtc6nde6ndk&sdkCorrelationID=prebuild&sdkMeta=eyJ1cmwiOiJodHRwczovL3d3dy5wYXlwYWwuY29tL3Nkay9qcz9jbGllbnQtaWQ9QVk3VGpKdUg1UnR2Q3VFZjJaZ0VWS3MzcXV1NjlVZ2dzQ2cyOWxrcmIza3ZzZEdjWDJsaktpZFlYWEhQUGFybW55bWQ5SmFjZlJoMGh6RXAmY3VycmVuY3k9VVNEJmludGVncmF0aW9uLWRhdGU9MjAyNC0xMi0zMSZjb21wb25lbnRzPWJ1dHRvbnMsZnVuZGluZy1lbGlnaWJpbGl0eSZ2YXVsdD1mYWxzZSZjb21taXQ9dHJ1ZSZpbnRlbnQ9Y2FwdHVyZSZlbmFibGUtZnVuZGluZz12ZW5tbyxwYXlsYXRlciIsImF0dHJzIjp7ImRhdGEtcGFydG5lci1hdHRyaWJ1dGlvbi1pZCI6Ildvb19QUENQIiwiZGF0YS11aWQiOiJ1aWRfcHdhZWVpc2N1dHZxa2F1b2Nvd2tnZnZudmtveG5tIn19&sdkVersion=5.0.465&storageID=uid_ba45630ca6_mtc6nde6ndk&supportedNativeBrowser=true&supportsPopups=true&vault=false',
    'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'iframe',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': user_agent_str,
    }
    params_paypal = {
        'sessionID': session_id,
        'buttonSessionID': button_session_id,
        'locale.x': 'ar_EG',
        'commit': 'true',
        'hasShippingCallback': 'false',
        'env': 'production',
        'country.x': 'EG',
        'sdkMeta': 'meta_string_here',  # keep same or generate as needed
        'disable-card': '',
        'token': order_id,
    }
    # Request for card fields
    response_paypal = requests.get('https://www.paypal.com/smart/card-fields', params=params_paypal, headers=headers_paypal)
    response_paypal.raise_for_status()

    # Generate random code for payment
    def generate_random_code():
        characters = string.ascii_letters + string.digits
        return ''.join(random.choices(characters, k=17))
    random_code = generate_random_code()

    # Final payment request
    headers_pay = {
        'authority': 'www.paypal.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://www.paypal.com',
        'referer': 'https://www.paypal.com/smart/card-fields',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': user_agent_str,
    }
    json_data_pay = {
        'query': 'mutation payWithCard($token: String!, $card: CardInput!, ... )',  # truncated for brevity, insert your full GraphQL mutation
        'variables': {
            'token': order_id,
            'card': {
                'cardNumber': n,
                'type': 'VISA',
                'expirationDate': mm + '/20' + yy,
                'postalCode': zip_code,
                'securityCode': cvc,
            },
            'firstName': first_name,
            'lastName': last_name,
            'billingAddress': {
                'givenName': first_name,
                'familyName': last_name,
                'line1': street_address,
                'line2': None,
                'city': city,
                'state': state,
                'postalCode': zip_code,
                'country': 'US',
            },
            'email': acc,
            'currencyConversionType': 'VENDOR',
        },
        'operationName': 'payWithCard',
    }
    response_pay = requests.post('https://www.paypal.com/graphql', headers=headers_pay, json=json_data_pay)
    if 'ADD_SHIPPING_ERROR' in response_pay.text:
        raise RuntimeError("Payment error detected.")

    # You may parse response_pay.json() further as needed
    return "Purchase completed successfully!"

# Telegram command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Send /buy to start the purchase process.")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pong!")

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Starting purchase process...")
    try:
        # Example: ask user for card details or use default/hardcoded
        card_input = "4111|12|23|123"  # Replace with actual user input if needed
        user_agent_str = user_agent.generate_user_agent()
        user_cookies = {}  # Set if needed
        user_headers = {}  # Set if neededresult = perform_purchase(card_input, user_agent_str, user_cookies, user_headers)
        await update.message.reply_text(result)
    except Exception as e:
        logger.error(f"Error during purchase: {e}")
        await update.message.reply_text(f"Error: {e}")

# Main function to set webhook
async def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(CommandHandler("buy", buy))

    # Set webhook (replace with your actual webhook URL)
    application.bot.set_webhook(WEBHOOK_URL)

    # Run the application
    await application.run_polling()

# Start the bot
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
