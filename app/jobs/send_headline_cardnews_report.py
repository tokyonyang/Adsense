from __future__ import annotations

import json
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta

from app.services.daily_hotissue_source import build_daily_hotissue_payload, hot_items_to_anchor_groups
from app.services.headline_cardnews_render_service import build_cardnews_pages
from app.services.headline_cardnews_summary_service import summarize_anchor_groups_with_gemini
from app.services.market_chart_service import attach_market_charts
from app.services.telegram_album_service import send_media_group, send_text_message

KST = timezone(timedelta(hours=9))


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def weekday_ko(dt: datetime) -> str:
    return "월화수목금토일"[dt.weekday()]


def build_link_digest(issues: list[dict], payload: dict) -> str:
    now = datetime.now(KST)
    lines = [
        f"{now:%Y년 %m월%d일}({weekday_ko(now)})☀️☀️🌤",
        "💛 아침 헤드라인 뉴스 · 원문 링크",
        "",
        "※ Daily AdSense SEO HOT Issue 편집 엔진 기준으로 생성했습니다.",
        f"편집 정책: {payload.get('editorial_policy') or payload.get('category_policy') or '-'}",
        f"슬롯 구성: {payload.get('slot_mix') or '-'}",
        f"카드뉴스 기준 이슈: {len(issues)}개",
        "",
    ]

    for issue in issues:
        lines.append(f"{issue.get('rank')}. [{issue.get('category')}] {issue.get('headline')}")
        if issue.get("chart"):
            c = issue.get("chart") or {}
            if c.get("caption"):
                lines.append(f"   관련 지표: {c.get('caption')}")
        if issue.get("anchor_title") and issue.get("anchor_title") != issue.get("headline"):
            lines.append(f"   Daily 기준 키워드: {issue.get('anchor_title')}")
        if issue.get("insight"):
            lines.append(f"   전망 인사이트: {issue.get('insight')}")
        for idx, link in enumerate(issue.get("links") or [], start=1):
            title = link.get("title") or link.get("domain") or "원문"
            url = link.get("url") or ""
            if url:
                lines.append(f"   {idx}) {title}\n      {url}")
        lines.append("")

    return "\n".join(lines).strip()


def main():
    payload = build_daily_hotissue_payload(prefer_saved=True)

    hot_items = payload.get("morning_items") or payload.get("card_items") or payload.get("hot_items") or []

    if not hot_items:
        send_text_message("💛 아침 헤드라인 뉴스\n\nDaily HOT Issue 기준 항목이 없어 카드뉴스를 생성하지 못했습니다.")
        return

    max_issues = int(env("HEADLINE_CARDNEWS_ISSUES", "5"))
    anchor_groups = hot_items_to_anchor_groups(hot_items, max_issues=max_issues)
    issues = summarize_anchor_groups_with_gemini(anchor_groups)

    # v1.29: 환율/금리/유가/증시 등에는 시장 추이 차트를 붙이고 insight를 보강합니다.
    issues = attach_market_charts(issues)

    out_dir = Path("tmp/headline_cardnews")
    image_paths = build_cardnews_pages(issues, output_dir=out_dir)

    caption = "💛 아침 헤드라인 뉴스\n기사 흐름·시장 영향·전망 인사이트를 카드뉴스로 정리했습니다."
    send_media_group(image_paths, caption=caption)

    if env("HEADLINE_SEND_LINK_DIGEST", "true").lower() == "true":
        send_text_message(build_link_digest(issues, payload), disable_web_page_preview=True)

    print("[daily-hotissue-cardnews result]")
    print(json.dumps({
        "hot_items": len(hot_items),
        "cardnews_issues": len(issues),
        "pages": len(image_paths),
        "slot_mix": payload.get("slot_mix"),
        "category_mix": payload.get("category_mix"),
        "source_items": [
            {
                "keyword": x.get("keyword"),
                "slot": x.get("slot"),
                "category": x.get("category"),
                "editorial_score": x.get("editorial_score"),
                "adsense_score": x.get("adsense_score"),
                "noise_score": x.get("noise_score"),
            }
            for x in hot_items
        ],
        "issues_preview": [
            {
                "rank": x.get("rank"),
                "category": x.get("category"),
                "headline": x.get("headline"),
                "anchor_title": x.get("anchor_title"),
                "summary_lines": x.get("summary_lines"),
                "insight": x.get("insight"),
                "chart": {
                    "title": (x.get("chart") or {}).get("title"),
                    "caption": (x.get("chart") or {}).get("caption"),
                    "available": (x.get("chart") or {}).get("available"),
                } if x.get("chart") else None,
                "links": x.get("links"),
            }
            for x in issues
        ],
    }, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
