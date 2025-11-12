import os, hashlib, requests, json

URL = "https://intranet.tam.ch/bmz/gradebook/ajax-list-get-grades"

# Aus GitHub Secrets / Env
COOKIES = {
    "username": os.environ["COOKIE_USERNAME"],
    "school": os.environ["COOKIE_SCHOOL"],
    "sturmuser": os.environ["COOKIE_STURMUSER"],
    "sturmsession": os.environ["COOKIE_SESSION"],
}
RAW_PAYLOAD = os.environ["GRADES_PAYLOAD"]  # exakt so, wie in DevTools kopiert
NTFY_TOPIC = os.environ["NTFY_TOPIC"]       # z. B. tam-grades-salmane

LAST_HASH_FILE = "last_hash.txt"

def fetch_grades():
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
        # hilft oft:
        "Referer": "https://intranet.tam.ch/bmz/default/gradebook/index",
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari",
    }
    r = requests.post(URL, headers=headers, cookies=COOKIES, data=RAW_PAYLOAD, timeout=30)
    r.raise_for_status()
    return r.text

def notify(text):
    try:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=text.encode("utf-8"), timeout=15)
    except Exception as e:
        print("ntfy Fehler:", e)

def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def main():
    body = fetch_grades()
    h = sha256(body)

    last = ""
    if os.path.exists(LAST_HASH_FILE):
        last = open(LAST_HASH_FILE, "r", encoding="utf-8").read().strip()

    if h != last:
        open(LAST_HASH_FILE, "w", encoding="utf-8").write(h)
        # Optional: versuche kurz die Anzahl Items/Notes zu extrahieren, falls JSON
        excerpt = ""
        try:
            data = json.loads(body)
            if isinstance(data, dict):
                # haeufig gibt es keys wie "data" oder "grades"; wir versuchen beides
                for k in ("data", "grades", "items", "rows"):
                    if k in data and isinstance(data[k], list):
                        excerpt = f"Neue/veraenderte Noten erkannt. Anzahl Eintraege: {len(data[k])}"
                        break
        except Exception:
            pass

        notify(excerpt or "Neue/veraenderte Noten erkannt (Gradebook).")
        print("Aenderung erkannt — Push gesendet.")
    else:
        print("Keine Aenderung.")

if __name__ == "__main__":
    main()
