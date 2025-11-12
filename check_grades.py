import requests
import hashlib
import os

URL = "https://intranet.tam.ch/bmz/gradebook/ajax-list-get-grades"

COOKIES = {
    "username": os.getenv("COOKIE_USERNAME"),
    "school": os.getenv("COOKIE_SCHOOL"),
    "sturmuser": os.getenv("COOKIE_STURMUSER"),
    "sturmsession": os.getenv("COOKIE_SESSION"),
}

DATA = {
    "studentId": "11884169",
    "courseId": "1167368",
    "periodId": "83"
}

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

def fetch_grades():
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(URL, data=DATA, cookies=COOKIES, headers=headers)
    r.raise_for_status()
    return r.text

def hash_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def send_discord_message(message):
    if not DISCORD_WEBHOOK:
        print("Discord Webhook fehlt!")
        return
    payload = {"content": message}
    try:
        requests.post(DISCORD_WEBHOOK, json=payload)
        print("Discord Nachricht gesendet.")
    except Exception as e:
        print("Fehler beim Senden:", e)

def main():
    html = fetch_grades()
    current_hash = hash_text(html)
    last_hash_file = "/tmp/last_hash.txt"  # wird im Cloud-System zwischengespeichert

    last_hash = ""
    if os.path.exists(last_hash_file):
        with open(last_hash_file, "r") as f:
            last_hash = f.read().strip()

    if current_hash != last_hash:
        print("Änderung erkannt – sende Nachricht")
        send_discord_message("📢 **Neue Note oder Änderung im Intranet!**")
        with open(last_hash_file, "w") as f:
            f.write(current_hash)
    else:
        print("Keine Änderung erkannt.")

if __name__ == "__main__":
    main()
