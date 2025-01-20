from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
import os
from Navy.database import dB
from Navy.helpers import CMD, Emoji, Tools

# Inisialisasi bot
app = Client("my_bot", bot_token="8185029818:AAF-4ckmWh-DudFnrNSw2J4FLEcPdiyoKuA")

# Fungsi utama saweria
@CMD.UBOT("saweria")
async def saweria(client, message):
    em = Emoji(client)
    em.get()
    proses_ = em.get_costum_text()[4]
    proses = await message.reply(f"{em.proses}**{proses_}**")
    args = ["login", "payment", "balance", "cekpay"]
    command = message.command
    if len(command) < 2 or command[1] not in args:
        return await proses.edit(
            f"{em.gagal}**Please give me valid query, only supported `login`, `payment`, `balance`, and `cekpay`]**"
        )
    if command[1] == "login":
        reply = message.reply_to_message
        if not reply:
            return await proses.edit(
                f"{em.gagal}**Please reply to message with format: aku1244haha@gmail.com pasword123**"
            )
        mail, pw = Tools.parse_text(reply)
        url = f"https://itzpire.com/saweria/login?email={mail}&password={pw}"
        result = await Tools.fetch.get(url)
        if result.status_code == 200:
            data = result.json()
            msg = f"""
<blockquote>{em.sukses}**Succesfully login saweria!!

user_id: `{data['data']['user_id']}`
token: `{data['data']['token']}`

Please dont share this data!!**</blockquote>"""
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
                f"{em.gagal}**Please login first to make payment!!**"
            )
        mail = info["email"]
        pw = info["pw"]
        url = f"https://itzpire.com/saweria/balance?email={mail}&password={pw}"
        result = await Tools.fetch.get(url)
        if result.status_code == 200:
            data = result.json()
            msg = f"""
<blockquote>{em.sukses}**Your balance in saweria!!

Saldo Pending: `{data['data']['pending']}`
Saldo Available: `{data['data']['available']}`
Mata Uang: `{data['data']['currency']}`**</blockquote>"""
            return await proses.edit(msg)
        else:
            return await proses.edit(
                f"{em.gagal}**Failed to fetch data**: {result.status_code}"
            )
    elif command[1] == "cekpay":
        info = dB.get_var(client.me.id, "SAWERIA_LOGIN")
        if not info:
            return await proses.edit(
                f"{em.gagal}**Please login first to make payment!!**"
            )
        if len(message.command) < 3:
            return await proses.edit(
                f"{em.gagal}**Please give me id payment. Example: `{message.text.split()[0]} cekpay 5f694d83-4b60-4640-a22c-1da47d224a63`**"
            )
        id_pay = message.text.split(None, 2)[2]
        url = f"https://itzpire.com/saweria/check-payment?id={id_pay}&user_id={info['user_id']}"
        result = await Tools.fetch.get(url)
        if result.status_code == 200:
            data = result.json()
            status = data["status"]
            teks = data["msg"]
            if teks == "OA4XSN":
                msg = f"""
<b><blockquote>{em.sukses}Status Payment!!
ID: `{id_pay}`
Status: Succesed
Message: Successful payment !!</blockquote></b>"""
            else:
                msg = f"""
<b><blockquote>{em.sukses}Status Payment!!
ID: `{id_pay}`
Status: {status}
Message: {teks}</blockquote></b>"""
            return await proses.edit(msg)
        else:
            return await proses.edit(
                f"{em.gagal}**Failed to fetch data**: {result.status_code}"
            )
    elif command[1] == "payment":
        info = dB.get_var(client.me.id, "SAWERIA_LOGIN")
        if not info:
            return await proses.edit(
                f"{em.gagal}**Please login first to make payment!!**"
            )
        reply = message.reply_to_message
        amount = reply.text.split()[0] if reply else message.text.split(None, 3)[2]
        thanks = "Thanks for payment." if not reply else reply.text.split(maxsplit=1)[1]
        email = info["email"]
        user_id = info["user_id"]
        url = f"https://itzpire.com/saweria/create-payment?amount={amount}&name={client.me.first_name}&email={email}&user_id={user_id}&msg={thanks}"
        result = await Tools.fetch.get(url)
        if result.status_code == 200:
            data = result.json()
            total = data["data"]["amount"]
            id_payment = data["data"]["id"]
            currency = data["data"]["currency"]
            pesan = data["data"]["message"]
            expired = data["data"]["expired_at"]
            type = data["data"]["payment_type"]
            qris = f"{total}.png"
            await client.bash(f"wget {data['data']['qr_image']} -O {qris}")
            msg = f"""
<blockquote><b>{em.sukses}Successed Generate Payment!!
Total: {total}
ID: `{id_payment}`
Currency: {currency}
Type: {type}
Expired at: {expired}
Message: {pesan}</b></blockquote>"""
            try:
                await proses.delete()
                return await message.reply_photo(qris, caption=msg)
            except Exception:
                return await proses.edit(
                    f"{em.gagal}**Failed to send qris image!!**\n\n" + msg
                )
        else:
            return await proses.edit(
                f"{em.gagal}**Failed to fetch data**: {result.status_code}"
            )

# Memulai bot
app.run()
