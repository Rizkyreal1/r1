import telebot
import requests
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# Token bot Telegram
BOT_TOKEN = "8185029818:AAHiACh5_HqEWwzf2iurIWuDLG0Dp7OnSss"
bot = telebot.TeleBot(BOT_TOKEN)

# Informasi Saweria
SAWERIA_EMAIL = "hackerff980k@gmail.com"
SAWERIA_PASSWORD = "astapa12345"
SAWERIA_USER_ID = "b849c9df-a51d-468b-98d5-31717f481a1d"

# Kamus harga produk
PRODUCT_PRICES = {
    "digitalocean_10": 120000,
    "digitalocean_3": 90000,
    "alibaba_3month": 45000,
    "alibaba_1year": 45000,
    "aws": 140000,
}

# Fungsi untuk membuat pembayaran Saweria
def create_payment(amount, name, message):
    url = "https://itzpire.com/saweria/payment/create"
    params = {
        "amount": amount,
        "name": name,
        "email": SAWERIA_EMAIL,
        "user_id": SAWERIA_USER_ID,
        "msg": message,
    }
    response = requests.get(url, params=params)
    return response.json() if response.status_code == 200 else None

# Fungsi untuk mengecek status pembayaran
def check_payment_status(payment_id):
    url = "https://itzpire.com/saweria/payment/check"
    params = {"id": payment_id, "user_id": SAWERIA_USER_ID}
    response = requests.get(url, params=params)
    return response.json() if response.status_code == 200 else None

# Fungsi untuk perintah /start
@bot.message_handler(commands=["start"])
def start(message):
    text = """👋 Selamat Datang di HYPEZ STORE!

Pilih layanan cloud untuk melihat detail produk:"""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("DigitalOcean", callback_data="digitalocean")],
        [InlineKeyboardButton("Alibaba Cloud", callback_data="alibaba")],
        [InlineKeyboardButton("AWS", callback_data="aws")],
    ])
    bot.send_message(message.chat.id, text, reply_markup=keyboard)

# Fungsi untuk menangani callback detail produk
@bot.callback_query_handler(func=lambda call: call.data in ["digitalocean", "alibaba", "aws"])
def product_details(call):
    if call.data == "digitalocean":
        text = """📦 **DigitalOcean**:
1. 10 Drop CC ➜ Rp 120.000
2. 3 Drop CC ➜ Rp 90.000"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("10 Drop CC", callback_data="buy_digitalocean_10")],
            [InlineKeyboardButton("3 Drop CC", callback_data="buy_digitalocean_3")],
        ])
    elif call.data == "alibaba":
        text = """📦 **Alibaba Cloud**:
1. 3 Month ➜ Rp 45.000
2. 1 Year ➜ Rp 45.000"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("3 Month", callback_data="buy_alibaba_3month")],
            [InlineKeyboardButton("1 Year", callback_data="buy_alibaba_1year")],
        ])
    elif call.data == "aws":
        text = """📦 **Amazon Web Service (AWS)**:
Free Tier ➜ Rp 140.000"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Beli AWS", callback_data="buy_aws")],
        ])
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=keyboard)

# Fungsi untuk menangani pembelian produk
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def confirm_purchase(call):
    product_key = call.data.split("_")[1:]
    product_name = " ".join(product_key).capitalize()
    product_price = PRODUCT_PRICES["_".join(product_key)]
    text = f"""⚠️ Konfirmasi Pembelian ⚠️

Produk: {product_name}
Harga: Rp {product_price:,}

Klik "Bayar Sekarang" untuk melanjutkan pembayaran.
"""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Bayar Sekarang", callback_data=f"pay_{'_'.join(product_key)}")],
        [InlineKeyboardButton("❌ Batal", callback_data="cancel")],
    ])
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=keyboard)

# Fungsi untuk memproses pembayaran
@bot.callback_query_handler(func=lambda call: call.data.startswith("pay_"))
def process_payment(call):
    product_key = call.data.split("_")[1:]
    product_name = " ".join(product_key).capitalize()
    product_price = PRODUCT_PRICES["_".join(product_key)]
    payment = create_payment(product_price, call.from_user.username, f"Pembayaran {product_name}")
    if payment and payment.get("status") == "success":
        payment_url = payment["data"]["url"]
        bot.send_message(call.message.chat.id, f"✅ Klik tautan berikut untuk membayar:\n{payment_url}")
    else:
        bot.send_message(call.message.chat.id, "❌ Gagal memproses pembayaran. Coba lagi nanti.")

# Fungsi untuk membatalkan pembelian
@bot.callback_query_handler(func=lambda call: call.data == "cancel")
def cancel_purchase(call):
    bot.send_message(call.message.chat.id, "❌ Pembelian dibatalkan.")

# Menjalankan bot
print("Bot berjalan...")
bot.polling()