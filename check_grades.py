import requests
import hashlib
import os

# === KONFIGURATION ===
URL = "https://intranet.tam.ch/bmz/gradebook/ajax-list-get-grades"

# Diese Werte holt GitHub aus Secrets (siehe weiter unten)
COOKIES = {
    "username": os.getenv("COOKIE_USERNAME"),
    "school": os.getenv("COOKIE_SCHOOL"),
    "sturmuser": os.getenv("COOKIE_STURMUSER"),
    "sturmsession": os.getenv("COOKIE_SESSION"),
}

# Formulardaten (Payload aus deinem Screenshot)
DATA = {
    "studentId": "11884169",
    "courseId": "1167368",
    "periodId": "83"
}

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
# =====================


def fetch_grades():
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(URL, data=DATA, cookies=COOKIES, headers=headers)
    r.raise_for_status()
    return r.text


def hash_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def send_discord_message(msg):
    payload = {"content": msg}
    try:
        r = requests.post(DISCORD_WEBHOOK, json=payload)
        r.raise_for_status()
        print("Discord Nachricht gesendet.")
    except Exception as e:
        print("Fehler beim Senden an Discord:", e)


def main():
    html = fetch_grades()
    current_hash = hash_text(html)
    last_file = "last_hash.txt"

    last_hash = ""
    if os.path.exists(last_file):
        last_hash = open(last_file).read().strip()

    if current_hash != last_hash:
        open(last_file, "w").write(current_hash)
        send_discord_message("📢 **Neue Note oder Änderung im Intranet!**")
        print("Änderung erkannt — Nachricht gesendet.")
    else:
        print("Keine Änderung erkannt.")


if __name__ == "__main__":
    main()
