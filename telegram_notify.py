import os, requests

def send_telegram(text: str):
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        print("[INFO] Telegram secrets not set. Skip.")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": False}
    r = requests.post(url, data=payload, timeout=20)
    if r.status_code >= 400:
        raise RuntimeError(f"Telegram failed: {r.status_code} {r.text[:300]}")
