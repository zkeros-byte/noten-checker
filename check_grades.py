import requests
import hashlib
import os
import json
import re

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
    """Hole die Daten vom Intranet."""
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(URL, data=DATA, cookies=COOKIES, headers=headers)
    r.raise_for_status()
    return r.text


def extract_relevant_text(raw_html):
    """
    Filtere nur die echten Noten-Daten heraus,
    um technische Änderungen (z. B. Session-IDs, Zeitstempel) zu ignorieren.
    """
    # Versuche, nur JSON-ähnliche Teile zu finden, die "grade" enthalten
    grades = re.findall(r'"grade"\s*:\s*"[^"]*"', raw_html)
    subjects = re.findall(r'"subject"\s*:\s*"[^"]*"', raw_html)
    combined = "\n".join(grades + subjects)
    return combined


def hash_text(text):
    """Erzeuge Hash für den Vergleich."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def send_discord_message(message):
    """Sende Nachricht an Discord."""
    if not DISCORD_WEBHOOK:
        print("Discord Webhook fehlt!")
        return
    payload = {"content": message}
    try:
        requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
        print("Discord Nachricht gesendet.")
    except Exception as e:
        print("Fehler beim Senden:", e)


def main():
    raw = fetch_grades()
    filtered = extract_relevant_text(raw)
    current_hash = hash_text(filtered)
    last_file = "last_hash.txt"

    # Prüfe, ob Hash-Datei existiert (vom letzten Lauf)
    if os.path.exists(last_file):
        with open(last_file, "r") as f:
            last_hash = f.read().strip()
    else:
        last_hash = ""

    if current_hash != last_hash:
        # Wenn es keine alte Datei gibt, ist das der erste Lauf → keine Nachricht
        if last_hash == "":
            print("Erster Lauf – Hash gespeichert, aber keine Nachricht gesendet.")
        else:
            print("Änderung erkannt – sende Nachricht.")
            send_discord_message("📢 **Neue oder geänderte Note im Intranet!**")
        # Hash speichern
        with open(last_file, "w") as f:
            f.write(current_hash)
    else:
        print("Keine Änderung erkannt.")


if __name__ == "__main__":
    main()
