import telebot
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Token bot Telegram
BOT_TOKEN = "7942538474:AAFOsYXylG48VhTbqXOLj_R9KLFtMCyqWN4"
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
        "msg": message
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
    text = """Hello 👻
    
Selamat datang di HYPEZ STORE!
Pilih layanan cloud di bawah ini untuk melihat detail produk:"""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("DigitalOcean", callback_data='digitalocean')],
        [InlineKeyboardButton("Alibaba Cloud", callback_data='alibaba')],
        [InlineKeyboardButton("AWS", callback_data='aws')],
    ])
    bot.send_message(message.chat.id, text, reply_markup=keyboard)

# Fungsi untuk menangani detail produk
@bot.callback_query_handler(func=lambda call: call.data in ["digitalocean", "alibaba", "aws"])
def product_details(call):
    if call.data == 'digitalocean':
        text = """DigitalOcean:
1. 10 Drop CC ➜ Rp 120,000
2. 3 Drop CC ➜ Rp 90,000"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("10 Drop CC", callback_data='buy_digitalocean_10')],
            [InlineKeyboardButton("3 Drop CC", callback_data='buy_digitalocean_3')],
        ])
    elif call.data == 'alibaba':
        text = """Alibaba Cloud:
1. 3 Month 4GB 2CPU ➜ Rp 45,000
2. 1 Year 1GB 1CPU ➜ Rp 45,000"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("3 Month", callback_data='buy_alibaba_3month')],
            [InlineKeyboardButton("1 Year", callback_data='buy_alibaba_1year')],
        ])
    elif call.data == 'aws':
        text = "AWS Free Tier ➜ Rp 140,000"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Beli AWS", callback_data='buy_aws')],
        ])
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=keyboard)

# Fungsi untuk konfirmasi pembayaran
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def confirm_purchase(call):
    product_key = call.data.split("_")[1:]
    product_name = " ".join(product_key).capitalize()
    product_price = PRODUCT_PRICES["_".join(product_key)]
    text = f"""⚠️ Konfirmasi Pembelian ⚠️

Detail Produk:
➜ Nama Produk: {product_name}
➜ Harga: Rp {product_price:,}

Klik tombol di bawah untuk melanjutkan pembayaran."""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Lanjutkan Pembayaran", callback_data=f'pay_{"_".join(product_key)}')],
    ])
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=keyboard)

# Fungsi untuk pembayaran
@bot.callback_query_handler(func=lambda call: call.data.startswith("pay_"))
def process_payment(call):
    product_key = call.data.split("_")[1:]
    product_name = " ".join(product_key).capitalize()
    product_price = PRODUCT_PRICES["_".join(product_key)]
    payment = create_payment(product_price, call.from_user.username, f"Pembayaran {product_name}")
    
    if payment and payment.get("status") == "success":
        payment_url = payment["data"]["url"]
        qr_code_url = payment["data"]["qr_url"]  # Asumsi QR code ada di URL ini
        additional_info = f"""QR CODE DI SINI
➜ Nama Produk: {product_name}
➜ Harga: Rp {product_price:,}"""

        # Mengirim QR code dan informasi tambahan
        bot.send_message(call.message.chat.id, additional_info)
        bot.send_photo(call.message.chat.id, qr_code_url, caption="Scan QR code untuk pembayaran.")

        # Jika URL lain perlu ditampilkan, bisa ditambahkan di bawah ini
        bot.send_message(call.message.chat.id, f"Silakan bayar melalui tautan ini:\n{payment_url}")

    else:
        bot.send_message(call.message.chat.id, "Gagal memproses pembayaran. Coba lagi nanti.")

# Menjalankan bot
bot.polling()
