import os
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
import requests

# Inisialisasi bot
app = Client("my_bot", bot_token="8185029818:AAF-4ckmWh-DudFnrNSw2J4FLEcPdiyoKuA")

# Helper untuk emoji
class Emoji:
    def __init__(self, client):
        self.client = client
        self.sukses = "✅"
        self.gagal = "❌"
        self.proses = "⏳"
    
    def get(self):
        return self

    def get_costum_text(self):
        return ["", "", "", "", "Processing..."]  # Dummy text for processing

# Helper untuk Tools
class Tools:
    @staticmethod
    def parse_text(message):
        return message.text.split()

    @staticmethod
    def fetch(url):
        response = requests.get(url)
        return response

# Database mockup (misalnya dengan dictionary)
class Database:
    def __init__(self):
        self.db = {}

    def set_var(self, user_id, key, value):
        if user_id not in self.db:
            self.db[user_id] = {}
        self.db[user_id][key] = value

    def get_var(self, user_id, key):
        return self.db.get(user_id, {}).get(key)

# Inisialisasi objek database
dB = Database()

# Memuat plugin dari folder 'plugins' jika ada
plugin_folder = "plugins"
for filename in os.listdir(plugin_folder):
    if filename.endswith(".py"):
        exec(open(f"{plugin_folder}/{filename}").read())

@app.on_message(filters.command("saweria"))
async def saweria(client, message):
    em = Emoji(client)
    em.get()
    proses_ = em.get_costum_text()[4]
    proses = await message.reply(f"{em.proses}**{proses_}**")
    args = ["login", "payment", "balance", "cekpay"]
    command = message.command
    if len(command) < 2 or command[1] not in args:
        return await proses.edit(
            f"{em.gagal}**Please give me valid query, only supported `login`, `payment`, `balance`, and `cekpay**"
        )
    
    if command[1] == "login":
        reply = message.reply_to_message
        if not reply:
            return await proses.edit(
                f"{em.gagal}**Please reply to message with format: aku1244haha@gmail.com password123**"
            )
        mail, pw = Tools.parse_text(reply)
        url = f"https://itzpire.com/saweria/login?email={mail}&password={pw}"
        result = Tools.fetch(url)
        if result.status_code == 200:
            data = result.json()
            msg = f"""
<blockquote>{em.sukses}**Successfully logged into Saweria!!

user_id: `{data['data']['user_id']}`
token: `{data['data']['token']}`

Please don't share this data!**</blockquote>"""
            kwarg = {
                "email": mail,
                "pw": pw,
                "user_id": data["data"]["user_id"],
                "token": data["data"]["token"],
            }
            dB.set_var(client.me.id, "SAWERIA_LOGIN", kwarg)
            return await proses.edit(msg)
        else:
            return await proses.edit(
                f"{em.gagal}**Failed to fetch data**: {result.status_code}"
            )
    
    elif command[1] == "balance":
        info = dB.get_var(client.me.id, "SAWERIA_LOGIN")
        if not info:
            return await proses.edit(
                f"{em.gagal}**Please login first to make a payment!!**"
            )
        mail = info["email"]
        pw = info["pw"]
        url = f"https://itzpire.com/saweria/balance?email={mail}&password={pw}"
        result = Tools.fetch(url)
        if result.status_code == 200:
            data = result.json()
            msg = f"""
<blockquote>{em.sukses}**Your balance in Saweria!!

Pending Balance: `{data['data']['pending']}`
Available Balance: `{data['data']['available']}`
Currency: `{data['data']['currency']}`**</blockquote>"""
            return await proses.edit(msg)
        else:
            return await proses.edit(
                f"{em.gagal}**Failed to fetch data**: {result.status_code}"
            )
    
    elif command[1] == "cekpay":
        info = dB.get_var(client.me.id, "SAWERIA_LOGIN")
        if not info:
            return await proses.edit(
                f"{em.gagal}**Please login first to make a payment!!**"
            )
        if len(message.command) < 3:
            return await proses.edit(
                f"{em.gagal}**Please provide the payment ID. Example: `{message.text.split()[0]} cekpay 5f694d83-4b60-4640-a22c-1da47d224a63`**"
            )
        id_pay = message.text.split(None, 2)[2]
        url = f"https://itzpire.com/saweria/check-payment?id={id_pay}&user_id={info['user_id']}"
        result = Tools.fetch(url)
        if result.status_code == 200:
            data = result.json()
            status = data["status"]
            message_text = data["msg"]
            if message_text == "OA4XSN":
                msg = f"""
<b><blockquote>{em.sukses}Payment Status!!
ID: `{id_pay}`
Status: Succeeded
Message: Successful payment!!</blockquote></b>"""
            else:
                msg = f"""
<b><blockquote>{em.sukses}Payment Status!!
ID: `{id_pay}`
Status: {status}
Message: {message_text}</blockquote></b>"""
            return await proses.edit(msg)
        else:
            return await proses.edit(
                f"{em.gagal}**Failed to fetch data**: {result.status_code}"
            )
    
    elif command[1] == "payment":
        info = dB.get_var(client.me.id, "SAWERIA_LOGIN")
        if not info:
            return await proses.edit(
                f"{em.gagal}**Please login first to make a payment!!**"
            )
        reply = message.reply_to_message
        amount = reply.text.split()[0] if reply else message.text.split(None, 3)[2]
        thanks = "Thanks for payment." if not reply else reply.text.split(maxsplit=1)[1]
        email = info["email"]
        user_id = info["user_id"]
        url = f"https://itzpire.com/saweria/create-payment?amount={amount}&name={client.me.first_name}&email={email}&user_id={user_id}&msg={thanks}"
        result = Tools.fetch(url)
        if result.status_code == 200:
            data = result.json()
            total = data["data"]["amount"]
            id_payment = data["data"]["id"]
            currency = data["data"]["currency"]
            message_text = data["data"]["message"]
            expired = data["data"]["expired_at"]
            payment_type = data["data"]["payment_type"]
            qris = f"{total}.png"
            await client.bash(f"wget {data['data']['qr_image']} -O {qris}")
            msg = f"""
<blockquote><b>{em.sukses}Payment Created Successfully!!
Total: {total}
ID: `{id_payment}`
Currency: {currency}
Type: {payment_type}
Expired at: {expired}
Message: {message_text}</b></blockquote>"""
            try:
                await proses.delete()
                return await message.reply_photo(qris, caption=msg)
            except Exception:
                return await proses.edit(
                    f"{em.gagal}**Failed to send QR code image!!**\n\n" + msg
                )
        else:
            return await proses.edit(
                f"{em.gagal}**Failed to fetch data**: {result.status_code}"
            )

# Jalankan bot
app.run()
