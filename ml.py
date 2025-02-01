import logging
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext, CommandHandler

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
async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    chat_id = update.message.chat_id

    try:
        # Cek apakah format input benar (harus ada 2 angka: ID dan server)
        user_id, server = text.split()

        # Kirim perintah ke bot target
        send_info_request(user_id, server, chat_id)

        # Balas user bahwa permintaan sedang diproses
        await context.bot.send_message(chat_id, "Cek akun sedang diproses, mohon tunggu...")

    except ValueError:
        await context.bot.send_message(chat_id, "Format salah! Kirim seperti ini: `1197609514 13865`")
    except Exception as e:
        await context.bot.send_message(chat_id, f"Error: {e}")

# Fungsi untuk mengecek balasan dari @bengkelmlbb_bot
async def check_bot_response(context: CallbackContext):
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
                        await context.bot.send_message(user_chat_id, text)
                        del pending_requests[user_chat_id]
                        break

# Fungsi utama menjalankan bot
async def main():
    # Setup bot menggunakan Application
    app = Application.builder().token(BOT_TOKEN).build()

    # Menambahkan handler untuk pesan teks
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Menambahkan job queue untuk pengecekan balasan
    job_queue = app.job_queue
    job_queue.run_repeating(check_bot_response, interval=5, first=0)

    # Menjalankan bot
    print("Bot sedang berjalan...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
