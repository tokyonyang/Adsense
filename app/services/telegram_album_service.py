from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import requests

TELEGRAM_API_BASE = "https://api.telegram.org/bot"


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def credentials() -> tuple[str, str]:
    token = env("TELEGRAM_BOT_TOKEN")
    chat_id = env("TELEGRAM_CHAT_ID")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN이 설정되지 않았습니다.")
    if not chat_id:
        raise RuntimeError("TELEGRAM_CHAT_ID가 설정되지 않았습니다.")
    return token, chat_id


def send_media_group(image_paths: list[str | Path], *, caption: str = "") -> dict[str, Any]:
    """
    Telegram 앨범 전송. 최대 10개 media까지 가능.
    첫 번째 이미지에만 caption을 붙입니다.
    """
    if not image_paths:
        return {"ok": False, "reason": "no images"}

    token, chat_id = credentials()
    url = f"{TELEGRAM_API_BASE}{token}/sendMediaGroup"

    media = []
    files = {}

    for idx, path in enumerate(image_paths[:10]):
        p = Path(path)
        field = f"photo{idx}"
        item = {"type": "photo", "media": f"attach://{field}"}
        if idx == 0 and caption:
            item["caption"] = caption[:1000]
        media.append(item)
        files[field] = p.open("rb")

    try:
        response = requests.post(
            url,
            data={"chat_id": chat_id, "media": json.dumps(media, ensure_ascii=False)},
            files=files,
            timeout=120,
        )
        try:
            data = response.json()
        except Exception:
            data = {"ok": False, "description": response.text}

        if not response.ok or not data.get("ok"):
            raise RuntimeError(f"Telegram media group 전송 실패: {data}")

        return data
    finally:
        for f in files.values():
            try:
                f.close()
            except Exception:
                pass


def send_text_message(text: str, *, disable_web_page_preview: bool = True) -> dict[str, Any]:
    token, chat_id = credentials()
    url = f"{TELEGRAM_API_BASE}{token}/sendMessage"

    results = []
    chunks = []
    current = ""
    for block in text.split("\n\n"):
        candidate = f"{current}\n\n{block}".strip() if current else block
        if len(candidate) > 3800:
            if current:
                chunks.append(current)
            current = block
        else:
            current = candidate
    if current:
        chunks.append(current)

    for chunk in chunks:
        response = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": chunk,
                "disable_web_page_preview": disable_web_page_preview,
            },
            timeout=30,
        )
        data = response.json() if response.text else {}
        if not response.ok or not data.get("ok"):
            raise RuntimeError(f"Telegram 텍스트 전송 실패: {data}")
        results.append(data)

    return {"ok": True, "sent_parts": len(results)}
