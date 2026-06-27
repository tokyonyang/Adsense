from __future__ import annotations

import json
from pathlib import Path

from app.services.overnight_hotissue_service import build_overnight_payload, build_text_report
from app.services.overnight_cardnews_render_service import build_overnight_cardnews_pages
from app.services.telegram_album_service import send_media_group, send_text_message


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

    # 1) 텍스트 먼저 전송
    send_text_message(text_report, disable_web_page_preview=True)

    # 2) 카드뉴스 전송
    image_paths = build_overnight_cardnews_pages(payload, output_dir=Path("tmp/overnight_hotissue"))
    send_media_group(
        image_paths,
        caption="🌅 간밤의 핫이슈\n미국뉴스·미증시·국내뉴스·트렌드·날씨를 카드뉴스로 정리했습니다.",
    )

    print("[overnight-hotissue result]")
    print(json.dumps({
        "us_news": len(payload.get("us_news") or []),
        "korea_news": len(payload.get("korea_news") or []),
        "market_indices": len((payload.get("us_market") or {}).get("indices") or []),
        "popular_keywords": len((payload.get("keywords") or {}).get("popular_keywords") or []),
        "realtime_keywords": len((payload.get("keywords") or {}).get("realtime_keywords") or []),
        "weather_regions": len(payload.get("weather") or []),
        "quote": payload.get("quote"),
        "pages": len(image_paths),
    }, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
