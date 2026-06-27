from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests

TELEGRAM_API_BASE = "https://api.telegram.org/bot"


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _telegram_credentials() -> tuple[str, str]:
    bot_token = env("TELEGRAM_BOT_TOKEN")
    chat_id = env("TELEGRAM_CHAT_ID")

    if not bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN이 설정되지 않았습니다.")
    if not chat_id:
        raise RuntimeError("TELEGRAM_CHAT_ID가 설정되지 않았습니다.")

    return bot_token, chat_id


def send_telegram_photo(
    photo_path: str | Path,
    *,
    caption: str = "",
    parse_mode: str | None = None,
) -> dict[str, Any]:
    bot_token, chat_id = _telegram_credentials()
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


def send_telegram_document(
    document_path: str | Path,
    *,
    caption: str = "",
    parse_mode: str | None = None,
) -> dict[str, Any]:
    """
    Telegram sendDocument는 sendPhoto보다 압축이 적어 원본 화질 보존에 유리합니다.
    채팅방에서는 파일처럼 보일 수 있지만, 이미지를 확대/저장할 때 품질이 좋습니다.
    """
    bot_token, chat_id = _telegram_credentials()
    url = f"{TELEGRAM_API_BASE}{bot_token}/sendDocument"
    document_path = Path(document_path)

    with document_path.open("rb") as f:
        response = requests.post(
            url,
            data={
                "chat_id": chat_id,
                "caption": caption,
                **({"parse_mode": parse_mode} if parse_mode else {}),
            },
            files={"document": f},
            timeout=90,
        )

    try:
        data = response.json()
    except Exception:
        data = {"ok": False, "description": response.text}

    if not response.ok or not data.get("ok"):
        raise RuntimeError(f"Telegram 문서 이미지 전송 실패: {data}")

    return data
