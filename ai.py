import time
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, CallbackContext

# Token bot Telegram dan informasi Saweria
BOT_TOKEN = "8185029818:AAHjSM0tRioIYrNKYJdCuQYkuwkoi2qjnHo"
SAWERIA_EMAIL = "hackerff980k@gmail.com"
SAWERIA_PASSWORD = "astapa12345"
SAWERIA_USER_ID = "b849c9df-a51d-468b-98d5-31717f481a1d"

bot = ApplicationBuilder().token(BOT_TOKEN).build()

PRODUCT_PRICES = {
    "digitalocean_10": 120000.00,
    "digitalocean_3": 90000.00,
    "alibaba_3month": 45000.00,
    "alibaba_1year": 45000.00,
    "aws": 140000.00,
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
async def start(update: Update, context: CallbackContext, query_message=None):
    user = update.effective_user
    username = f"@{user.username}" if user.username else user.first_name

    text = f"""Hello 👻

 — Hai, {username} 👋🏻
                      
 Selamat datang di HYPEZ STORE
   • Total User Bot: 🙍🏻‍♂️ 1723 Orang
   • Total Transaksi Terselesaikan: 7489x

Pilih layanan cloud di bawah ini untuk melihat detail produk:
    """
    keyboard = [
        [InlineKeyboardButton("DigitalOcean", callback_data='digitalocean')],
        [InlineKeyboardButton("Alibaba Cloud", callback_data='alibaba')],
        [InlineKeyboardButton("AWS", callback_data='aws')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query_message:
        await query_message.edit_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

# Fungsi untuk detail produk
async def product_details(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == 'digitalocean':
        text = """1. DigitalOcean
Digital Ocean 10 Drop CC
Price ➜ 120,000.00

Digital Ocean 3 Drop CC
Price ➜ 90,000.00"""
        keyboard = [
            [InlineKeyboardButton("Digital Ocean 10 Drop", callback_data='confirm_digitalocean_10')],
            [InlineKeyboardButton("Digital Ocean 3 Drop", callback_data='confirm_digitalocean_3')],
            [InlineKeyboardButton("Kembali", callback_data='menu_awal')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(text, reply_markup=reply_markup)

    elif query.data == 'alibaba':
        text = """2. AlibabaCloud
Alibaba 4gb 2cpu 3 month
Price ➜ 45,000.00

Alibaba 1gb 1cpu 1 year
Price ➜ 45,000.00"""
        keyboard = [
            [InlineKeyboardButton("4gb 2cpu 3 Month", callback_data='confirm_alibaba_3month')],
            [InlineKeyboardButton("1gb 1cpu 1 Year", callback_data='confirm_alibaba_1year')],
            [InlineKeyboardButton("Kembali", callback_data='menu_awal')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(text, reply_markup=reply_markup)

    elif query.data == 'aws':
        text = """3. Amazon Web Service
AWS Free Tier
Price ➜ 140,000.00"""
        keyboard = [
            [InlineKeyboardButton("AWS Free Tier", callback_data='confirm_aws')],
            [InlineKeyboardButton("Kembali", callback_data='menu_awal')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(text, reply_markup=reply_markup)

    elif query.data == 'menu_awal':
        await start(update, context, query.message)

# Fungsi untuk konfirmasi pembelian
async def confirm_purchase(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    product_key = query.data.split('_')[1:]  # Mengambil identifier produk
    product_name = " ".join(product_key).capitalize()
    product_price = PRODUCT_PRICES.get("_".join(product_key), 0)

    text = f"""⚠️ Konfirmasi Pembelian ⚠️

Detail Produk:
➜ Nama Produk: {product_name}
➜ Harga: {product_price:,.2f}

Apakah Anda yakin ingin melanjutkan pembelian ini?
    """
    keyboard = [
        [InlineKeyboardButton("✅ Ya, Lanjutkan", callback_data=f'buy_{"_".join(product_key)}')],
        [InlineKeyboardButton("❌ Tidak, Kembali", callback_data='menu_awal')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(text, reply_markup=reply_markup)

# Fungsi untuk menangani pembelian dan integrasi Saweria
async def buy_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    product_key = query.data.split('_')[1:]  # Mengambil identifier produk
    product_name = " ".join(product_key).capitalize()
    product_price = PRODUCT_PRICES.get("_".join(product_key), 0)

    # Hapus pesan konfirmasi sebelumnya (tombol "Ya, Lanjutkan" & "Tidak, Kembali")
    await query.message.delete()

    # Menyusun invoice pembayaran
    text = f"""🔰 Payment Invoice

Detail:
➜ Tanggal: {time.strftime('%d/%m/%Y, %H:%M')}
➜ Nama Produk: {product_name}
➜ Total Item: 1x
➜ Harga: {product_price:,.2f}
➜ Fee: 0
➜ Total Dibayar: {product_price:,.2f}

⚠️ Mohon segera melakukan pembayaran dengan memindai kode QR yang terlampir.  
💳 Pastikan jumlah pembayaran sesuai dengan nominal yang tertera pada invoice: Rp {product_price:,.2f}.
    """

    # Proses pembayaran menggunakan Saweria
    payment = create_payment(product_price, "User", f"Pembelian {product_name}")
    if payment and payment["status"] == "success":
        payment_id = payment["data"]["id"]
        payment_url = payment["data"]["url"]
        qr_image = payment["data"]["qr_image"]

        # Mengirimkan QR dan Invoice dalam satu pesan
        await query.message.reply_photo(
            photo=open(qr_image, 'rb'),
            caption=text
        )

        # Cek status pembayaran setiap 1 menit
        while True:
            time.sleep(60)
            status = check_payment_status(payment_id)
            if status and status["data"]["status"] == "PAID":
                await query.message.reply_text("Pembayaran berhasil! Pesanan kamu akan segera diproses.")
                break
            else:
                await query.message.reply_text("Menunggu pembayaran...")

# Fungsi utama
if __name__ == "__main__":
    # Menambahkan handler untuk /start dan tombol
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(product_details, pattern='^(digitalocean|alibaba|aws|menu_awal)$'))
    app.add_handler(CallbackQueryHandler(confirm_purchase, pattern='^confirm_.*$'))
    app.add_handler(CallbackQueryHandler(buy_handler, pattern='^buy_.*$'))

    print("Bot sedang berjalan...")
    app.run_polling()
