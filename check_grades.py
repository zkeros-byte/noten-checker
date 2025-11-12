import os
import hashlib
import requests

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
    "periodId": "83",
}

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

# Test-/Debug-Schalter (werden vom Workflow gesetzt)
FORCE_NOTIFY = os.getenv("FORCE_NOTIFY", "0") == "1"   # erzwingt Push
FAKE_CHANGE  = os.getenv("FAKE_CHANGE", "0") == "1"    # haengt TEST an Antwort an

LAST_HASH_FILE = "last_hash.txt"  # wird via Artifact zwischen Laeufen gespeichert

def fetch_grades():
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(URL, data=DATA, cookies=COOKIES, headers=headers, timeout=30)
    r.raise_for_status()
    return r.text

def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def send_discord(msg: str):
    if not DISCORD_WEBHOOK:
        print("WARN: DISCORD_WEBHOOK fehlt")
        return
    resp = requests.post(DISCORD_WEBHOOK, json={"content": msg})
    try:
        resp.raise_for_status()
        print("Discord Nachricht gesendet.")
    except Exception as e:
        print("Fehler beim Senden an Discord:", e, "Status:", resp.status_code, "Body:", resp.text)

def main():
    html = fetch_grades()
    if FAKE_CHANGE:
        html += "TESTAENDERUNG"
        print("FAKE_CHANGE aktiv → Antworttext kuenstlich geaendert.")

    current_hash = sha256(html)
    last_hash = ""

    if os.path.exists(LAST_HASH_FILE):
        with open(LAST_HASH_FILE, "r") as f:
            last_hash = f.read().strip()
        print("Vorhandener last_hash:", last_hash)
    else:
        print("Kein last_hash gefunden (erster Lauf oder kein Artifact).")

    print("Neuer Hash:", current_hash)

    changed = (current_hash != last_hash)
    print("Geaendert? ->", changed)

    if FORCE_NOTIFY:
        print("FORCE_NOTIFY aktiv → Push wird unabhängig vom Vergleich gesendet.")
        send_discord("Erzwungener Test-Push (FORCE_NOTIFY=1).")

    if changed:
        send_discord("Neue Note oder Aenderung erkannt (Hash unterschiedlich).")
        with open(LAST_HASH_FILE, "w") as f:
            f.write(current_hash)
        print("last_hash.txt aktualisiert.")
    else:
        print("Keine Aenderung erkannt (Hash gleich).")

if __name__ == "__main__":
    main()
