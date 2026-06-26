import os
import html
import requests


def clean_telegram_text(text: str) -> str:
    """실수로 이스케이프된 줄바꿈/따옴표를 텔레그램 표시용으로 복구합니다."""
    return (
        str(text or "")
        .replace("\\r\\n", "\n")
        .replace("\\n", "\n")
        .replace('\\"', '"')
    )


def html_escape(text: str) -> str:
    return html.escape(str(text or ""), quote=False)


def send_telegram(text: str):
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        print("[INFO] Telegram secrets not set. Skip.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": clean_telegram_text(text),
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    r = requests.post(url, json=payload, timeout=20)
    if r.status_code >= 400:
        raise RuntimeError(f"Telegram failed: {r.status_code} {r.text[:300]}")
