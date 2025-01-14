import asyncio
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
import time

# Kamus harga produk
PRODUCT_PRICES = {
    "Digital Ocean 10 Drop": 120000,
    "Digital Ocean 3 Drop": 90000,
    "Alibaba 4GB 2CPU (3 Month)": 45000,
    "Alibaba 1GB 1CPU (1 Year)": 45000,
    "AWS Free Tier": 140000,
}

# Fungsi untuk /start dan /buy
async def start(update: Update, context: CallbackContext):
    text = """📦 *Panduan Pembelian:*
1️⃣ Pilih layanan yang tersedia.
2️⃣ Klik produk yang ingin dibeli.
3️⃣ Konfirmasi pembelian Anda.
4️⃣ Lakukan pembayaran menggunakan QRIS yang disediakan.

Pilih layanan untuk melanjutkan pembelian:
"""
    keyboard = ReplyKeyboardMarkup(
        [["DigitalOcean", "Alibaba Cloud", "AWS"], ["Batal"]],
        resize_keyboard=True,
    )
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")

# Fungsi untuk menangani pilihan layanan
async def service_handler(update: Update, context: CallbackContext):
    text = update.message.text
    if text == "DigitalOcean":
        reply = """Produk DigitalOcean tersedia:
- Digital Ocean 10 Drop ➜ Rp120.000
- Digital Ocean 3 Drop ➜ Rp90.000"""
        keyboard = ReplyKeyboardMarkup(
            [["Digital Ocean 10 Drop", "Digital Ocean 3 Drop"], ["Kembali"]],
            resize_keyboard=True,
        )
    elif text == "Alibaba Cloud":
        reply = """Produk Alibaba Cloud tersedia:
- Alibaba 4GB 2CPU (3 Month) ➜ Rp45.000
- Alibaba 1GB 1CPU (1 Year) ➜ Rp45.000"""
        keyboard = ReplyKeyboardMarkup(
            [["Alibaba 4GB 2CPU (3 Month)", "Alibaba 1GB 1CPU (1 Year)"], ["Kembali"]],
            resize_keyboard=True,
        )
    elif text == "AWS":
        reply = """Produk AWS tersedia:
- AWS Free Tier ➜ Rp140.000"""
        keyboard = ReplyKeyboardMarkup([["AWS Free Tier"], ["Kembali"]], resize_keyboard=True)
    elif text == "Batal":
        reply = "Transaksi dibatalkan. Ketik /start untuk memulai kembali."
        keyboard = ReplyKeyboardRemove()
    else:
        reply = "Pilihan tidak valid. Ketik /start untuk memulai kembali."
        keyboard = ReplyKeyboardRemove()
    await update.message.reply_text(reply, reply_markup=keyboard)

# Fungsi untuk konfirmasi pembelian
async def confirm_purchase(update: Update, context: CallbackContext):
    product_name = update.message.text
    if product_name not in PRODUCT_PRICES:
        await update.message.reply_text("Produk tidak valid. Ketik /start untuk memulai kembali.")
        return

    price = PRODUCT_PRICES[product_name]
    text = f"""⚠️ *Konfirmasi Pembelian* ⚠️

Detail Produk:
- Nama Produk: {product_name}
- Harga: Rp{price:,.0f}

Apakah Anda yakin ingin melanjutkan pembelian ini?
"""
    keyboard = ReplyKeyboardMarkup([["✅ Lanjutkan", "❌ Batal"]], resize_keyboard=True)
    context.user_data["product"] = product_name
    context.user_data["price"] = price
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")

# Fungsi untuk menangani pembayaran
async def payment_handler(update: Update, context: CallbackContext):
    if update.message.text == "✅ Lanjutkan":
        product_name = context.user_data.get("product")
        price = context.user_data.get("price")

        if not product_name or not price:
            await update.message.reply_text("Data produk tidak valid. Ketik /start untuk memulai kembali.")
            return

        # Simulasi proses pembayaran
        await update.message.reply_text("Tunggu sebentar...")
        await asyncio.sleep(3)

        text = f"""🔰 *Payment Invoice* 🔰

**Detail:**
- **Tanggal:** {time.strftime('%d/%m/%Y, %H:%M')}
- **Nama Produk:** {product_name}
- **Harga:** Rp{price:,.0f}
- **Fee:** Rp0
- **Total Dibayar:** Rp{price:,.0f}

📌 *Silahkan melakukan pembayaran dengan scan QRIS berikut.*
Harap segera lakukan pembayaran sebelum 30 menit, dan pastikan nominal sesuai dengan invoice
"""
        qr_image_path = "xId62njS.jpg"  # Path gambar QRIS
        await update.message.reply_photo(
            photo=open(qr_image_path, 'rb'),
            caption=text,
            parse_mode="Markdown",
        )

        # Menghapus data setelah pembayaran selesai
        context.user_data.clear()

    elif update.message.text == "❌ Batal":
        await update.message.reply_text(
            "Pembelian dibatalkan. Ketik /start untuk memulai kembali.",
            reply_markup=ReplyKeyboardRemove(),
        )

# Fungsi utama
if __name__ == "__main__":
    app = ApplicationBuilder().token("8185029818:AAEIcDBCQ3GBSjZAb5yZyFMFnbFduRFQMWE").build()

    # Tambahkan handler
    app.add_handler(CommandHandler(["start", "buy"], start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, service_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_purchase))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, payment_handler))

    print("Bot sedang berjalan...")
    app.run_polling()