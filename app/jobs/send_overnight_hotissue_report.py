from __future__ import annotations

import json
from pathlib import Path

from app.services.overnight_hotissue_service import build_overnight_payload, build_text_report
from app.services.overnight_cardnews_render_service import build_overnight_cardnews_pages
from app.services.telegram_album_service import send_media_group, send_text_message


def split_telegram_text(text: str, limit: int = 3400) -> list[str]:
    """Telegram sendMessage limit is 4096 chars. Keep margin for safety."""
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for line in text.splitlines():
        add_len = len(line) + 1
        if current and current_len + add_len > limit:
            chunks.append("\n".join(current).strip())
            current = []
            current_len = 0
        current.append(line)
        current_len += add_len

    if current:
        chunks.append("\n".join(current).strip())

    return [c for c in chunks if c]


def send_text_report(text_report: str) -> None:
    chunks = split_telegram_text(text_report)
    total = len(chunks)
    for idx, chunk in enumerate(chunks, start=1):
        if total > 1:
            header = f"🌅 간밤의 핫이슈 텍스트 리포트 ({idx}/{total})\n\n"
            send_text_message(header + chunk, disable_web_page_preview=True)
        else:
            send_text_message(chunk, disable_web_page_preview=True)


def main() -> None:
    payload = build_overnight_payload()
    text_report = build_text_report(payload)

    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    (reports_dir / "latest_overnight_hotissue.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    (reports_dir / "latest_overnight_hotissue_report.txt").write_text(text_report, encoding="utf-8")

    # 1) 텍스트 리포트 전송: 링크가 많아질 수 있으므로 자동 분할
    send_text_report(text_report)

    # 2) 카드뉴스 전송
    image_paths = build_overnight_cardnews_pages(payload, output_dir=Path("tmp/overnight_hotissue"))
    send_media_group(
        image_paths,
        caption="🌅 간밤의 핫이슈\n미국뉴스·미증시·국내뉴스·트렌드·SNS·날씨를 카드뉴스로 정리했습니다.",
    )

    print("[overnight-hotissue result]")
    print(json.dumps({
        "us_news": len(payload.get("us_news") or []),
        "korea_news": len(payload.get("korea_news") or []),
        "market_indices": len((payload.get("us_market") or {}).get("indices") or []),
        "popular_keywords": len((payload.get("keywords") or {}).get("popular_keywords") or []),
        "realtime_keywords": len((payload.get("keywords") or {}).get("realtime_keywords") or []),
        "sns_trends": len((payload.get("keywords") or {}).get("sns_trends") or []),
        "weather_regions": len(payload.get("weather") or []),
        "quote": payload.get("quote"),
        "pages": len(image_paths),
    }, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
