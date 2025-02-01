import logging
import requests
import time
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

# Token bot kamu
BOT_TOKEN = "7923529334:AAG2Axyxrvdom9tt7QmWMtjUcps0UAhMu74"

# ID bot target (@bengkelmlbb_bot)
TARGET_BOT_ID = 6362953495  # Ganti dengan ID asli bot @bengkelmlbb_bot

# Setup logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Dictionary untuk menyimpan request yang sedang diproses
pending_requests = {}

# Fungsi untuk meneruskan perintah /info ke bot target
def send_info_request(user_id, server, chat_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TARGET_BOT_ID,  # Kirim ke bot tujuan
        "text": f"/info {user_id} {server}"
    }
    requests.post(url, data=data)
    
    # Simpan request agar bisa dihubungkan dengan balasan
    pending_requests[chat_id] = (user_id, server)

# Fungsi untuk menangani pesan masuk dari user
def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    chat_id = update.message.chat_id

    try:
        # Cek apakah format input benar (harus ada 2 angka: ID dan server)
        user_id, server = text.split()

        # Kirim perintah ke bot target
        send_info_request(user_id, server, chat_id)

        # Balas user bahwa permintaan sedang diproses
        context.bot.send_message(chat_id, "Cek akun sedang diproses, mohon tunggu...")

    except ValueError:
        context.bot.send_message(chat_id, "Format salah! Kirim seperti ini: `1197609514 13865`")
    except Exception as e:
        context.bot.send_message(chat_id, f"Error: {e}")

# Fungsi untuk mengecek balasan dari @bengkelmlbb_bot
def check_bot_response(context: CallbackContext):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    response = requests.get(url).json()

    for update in response.get("result", []):
        if "message" in update:
            message = update["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "")

            # Cek apakah ini balasan dari @bengkelmlbb_bot
            if chat_id == TARGET_BOT_ID and any(req in text for req in pending_requests.values()):
                for user_chat_id, (user_id, server) in pending_requests.items():
                    if f"ID: {user_id}" in text and f"Server: {server}" in text:
                        # Kirim balasan ke user yang meminta
                        context.bot.send_message(user_chat_id, text)
                        del pending_requests[user_chat_id]
                        break

# Fungsi utama menjalankan bot
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    job_queue = updater.job_queue

    # Menambahkan handler untuk pesan teks
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Menjalankan pengecekan balasan dari @bengkelmlbb_bot setiap 5 detik
    job_queue.run_repeating(check_bot_response, interval=5)

    # Menjalankan bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
