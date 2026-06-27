from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests


TELEGRAM_API_BASE = "https://api.telegram.org/bot"


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def send_telegram_photo(
    photo_path: str | Path,
    *,
    caption: str = "",
    parse_mode: str | None = None,
) -> dict[str, Any]:
    bot_token = env("TELEGRAM_BOT_TOKEN")
    chat_id = env("TELEGRAM_CHAT_ID")

    if not bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN이 설정되지 않았습니다.")
    if not chat_id:
        raise RuntimeError("TELEGRAM_CHAT_ID가 설정되지 않았습니다.")

    url = f"{TELEGRAM_API_BASE}{bot_token}/sendPhoto"
    photo_path = Path(photo_path)

    with photo_path.open("rb") as f:
        response = requests.post(
            url,
            data={
                "chat_id": chat_id,
                "caption": caption,
                **({"parse_mode": parse_mode} if parse_mode else {}),
            },
            files={"photo": f},
            timeout=60,
        )

    try:
        data = response.json()
    except Exception:
        data = {"ok": False, "description": response.text}

    if not response.ok or not data.get("ok"):
        raise RuntimeError(f"Telegram 이미지 전송 실패: {data}")

    return data
