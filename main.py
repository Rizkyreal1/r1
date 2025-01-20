from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
import os

# Inisialisasi bot
app = Client("my_bot", bot_token="YOUR_BOT_TOKEN")

# Memuat plugin dari folder 'plugins'
plugin_folder = "plugins"
for filename in os.listdir(plugin_folder):
    if filename.endswith(".py"):
        exec(open(f"{plugin_folder}/{filename}").read())

@app.on_message(filters.command("saweria"))
async def saweria(client, message):
    # Panggil fungsi dari plugin 'saweria' di sini
    pass

app.run()
