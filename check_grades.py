import os
import hashlib
import requests

def fetch_grades():
    url = "https://intranet.tam.ch/bmz/gradebook/ajax-list-get-grades"
    payload = {
        "studentId": "11884169",
        "courseId": "1167368",
        "periodId": "83"
    }
    cookies = {
        "username": os.getenv("COOKIE_USERNAME"),
        "school": os.getenv("COOKIE_SCHOOL"),
        "sturmuser": os.getenv("COOKIE_STURMUSER"),
        "sturmsession": os.getenv("COOKIE_SESSION")
    }
    response = requests.post(url, data=payload, cookies=cookies)
    return response.text

def send_discord_message(message):
    webhook = os.getenv("DISCORD_WEBHOOK")
    requests.post(webhook, json={"content": message})

def main():
    html = fetch_grades()
    current_hash = hashlib.sha256(html.encode()).hexdigest()

    # Prüfen, ob es schon eine gespeicherte Datei gibt
    if os.path.exists("last_hash.txt"):
        with open("last_hash.txt", "r") as f:
            last_hash = f.read().strip()
    else:
        last_hash = ""

    if current_hash != last_hash:
        print("Änderung erkannt – sende Nachricht")
        send_discord_message("📢 Neue Note oder Änderung im Intranet!")
        with open("last_hash.txt", "w") as f:
            f.write(current_hash)
    else:
        print("Keine Änderung erkannt.")

if __name__ == "__main__":
    main()
