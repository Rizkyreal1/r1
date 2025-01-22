import telebot
import requests
import time

# Token bot Telegram kamu
BOT_TOKEN = "8185029818:AAF-4ckmWh-DudFnrNSw2J4FLEcPdiyoKuA"
bot = telebot.TeleBot(BOT_TOKEN)

# Informasi Saweria
SAWERIA_EMAIL = "hackerff980k@gmail.com"
SAWERIA_PASSWORD = "astapa12345"
SAWERIA_USER_ID = "b849c9df-a51d-468b-98d5-31717f481a1d"

# Fungsi untuk login Saweria (opsional jika butuh autentikasi)
def login_saweria(email, password):
    url = "https://itzpire.com/saweria/login"
    params = {"email": email, "password": password}
    response = requests.get(url, params=params)
    return response.json()

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
    if response.status_code == 200:
        return response.json()  # Mengembalikan data pembayaran
    else:
        return None

# Fungsi untuk cek status pembayaran
def check_payment_status(payment_id):
    url = "https://itzpire.com/saweria/payment/check"
    params = {"id": payment_id, "user_id": SAWERIA_USER_ID}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Memulai bot
@bot.message_handler(commands=["start"])
def welcome(message):
    bot.reply_to(message, "Halo! Selamat datang di toko kami. Ketik /order untuk memulai pesanan.")

# Menangani pesanan user
@bot.message_handler(commands=["order"])
def take_order(message):
    bot.send_message(message.chat.id, "Silakan masukkan nama barang dan jumlah yang ingin dipesan (contoh: 'Baju 2'):")
    bot.register_next_step_handler(message, process_order)

def process_order(message):
    try:
        order = message.text
        bot.send_message(message.chat.id, f"Pesanan kamu: {order}\nMasukkan nominal pembayaran (contoh: '50000'): ")
        bot.register_next_step_handler(message, process_payment, order)
    except Exception as e:
        bot.send_message(message.chat.id, f"Terjadi kesalahan: {str(e)}")

def process_payment(message, order):
    try:
        amount = message.text
        bot.send_message(message.chat.id, "Masukkan nama kamu untuk pembayaran:")
        bot.register_next_step_handler(message, create_saweria_payment, order, amount)
    except Exception as e:
        bot.send_message(message.chat.id, f"Terjadi kesalahan: {str(e)}")

def create_saweria_payment(message, order, amount):
    try:
        name = message.text
        msg = f"Pembayaran pesanan: {order}"
        payment = create_payment(amount, name, msg)
        if payment and payment["status"] == "success":
            payment_id = payment["data"]["id"]
            payment_link = payment["data"]["link"]  # Asumsikan API menyediakan link pembayaran
            bot.send_message(message.chat.id, f"Silakan bayar pesanan kamu:\n\n{payment_link}")
            bot.send_message(message.chat.id, "Saya akan mengecek status pembayaran setiap 1 menit.")
            
            # Cek pembayaran setiap 1 menit
            while True:
                time.sleep(60)  # Tunggu 1 menit
                status = check_payment_status(payment_id)
                if status and status["data"]["status"] == "PAID":  # Asumsikan "PAID" menandakan pembayaran selesai
                    bot.send_message(message.chat.id, "Pembayaran berhasil! Pesanan kamu akan segera diproses.")
                    break
                else:
                    bot.send_message(message.chat.id, "Menunggu pembayaran...")
        else:
            bot.send_message(message.chat.id, "Gagal membuat pembayaran. Silakan coba lagi.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Terjadi kesalahan: {str(e)}")

# Menjalankan bot
bot.polling()
