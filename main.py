from pyrogram import Client, filters
import os

# Inisialisasi bot
app = Client("my_bot", bot_token="8185029818:AAF-4ckmWh-DudFnrNSw2J4FLEcPdiyoKuA")

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
