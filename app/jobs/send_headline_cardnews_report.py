from __future__ import annotations

import json
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta

from app.services.daily_hotissue_source import build_daily_hotissue_payload, hot_items_to_anchor_groups
from app.services.headline_cardnews_render_service import build_cardnews_pages
from app.services.headline_cardnews_summary_service import summarize_anchor_groups_with_gemini
from app.services.telegram_album_service import send_media_group, send_text_message

KST = timezone(timedelta(hours=9))


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def weekday_ko(dt: datetime) -> str:
    return "월화수목금토일"[dt.weekday()]


def build_link_digest(issues: list[dict], payload: dict) -> str:
    now = datetime.now(KST)
    categories = payload.get("effective_categories") or []
    lines = [
        f"{now:%Y년 %m월%d일}({weekday_ko(now)})☀️☀️🌤",
        "💛 아침 헤드라인 뉴스 · 원문 링크",
        "",
        "※ Daily AdSense SEO HOT Issue TOP Item을 기준으로 생성했습니다.",
        f"수집 기준: 최근 {payload.get('effective_lookback_hours')}시간 / 카드뉴스 기준 이슈 {len(issues)}개",
        "",
    ]

    for issue in issues:
        lines.append(f"{issue.get('rank')}. [{issue.get('category')}] {issue.get('headline')}")
        if issue.get("anchor_title") and issue.get("anchor_title") != issue.get("headline"):
            lines.append(f"   Daily 기준 키워드: {issue.get('anchor_title')}")
        for idx, link in enumerate(issue.get("links") or [], start=1):
            title = link.get("title") or link.get("domain") or "원문"
            url = link.get("url") or ""
            if url:
                lines.append(f"   {idx}) {title}\n      {url}")
        lines.append("")

    return "\n".join(lines).strip()


def main():
    payload = build_daily_hotissue_payload()
    hot_items = payload.get("hot_items") or []

    if not hot_items:
        send_text_message("💛 아침 헤드라인 뉴스\n\nDaily HOT Issue 기준 항목이 없어 카드뉴스를 생성하지 못했습니다.")
        return

    max_issues = int(env("HEADLINE_CARDNEWS_ISSUES", "5"))
    anchor_groups = hot_items_to_anchor_groups(hot_items, max_issues=max_issues)
    issues = summarize_anchor_groups_with_gemini(anchor_groups)

    out_dir = Path("tmp/headline_cardnews")
    image_paths = build_cardnews_pages(issues, output_dir=out_dir)

    caption = "💛 아침 헤드라인 뉴스\nDaily HOT Issue 기준으로 유사 기사 3건씩 묶어 정리했습니다."
    send_media_group(image_paths, caption=caption)

    if env("HEADLINE_SEND_LINK_DIGEST", "true").lower() == "true":
        send_text_message(build_link_digest(issues, payload), disable_web_page_preview=True)

    print("[daily-hotissue-cardnews result]")
    print(json.dumps({
        "hot_items": len(hot_items),
        "cardnews_issues": len(issues),
        "pages": len(image_paths),
        "category_mix": [
            {"keyword": x.get("keyword"), "category": x.get("category_label"), "interest": x.get("interest_label")}
            for x in hot_items
        ],
        "issues_preview": [
            {
                "rank": x.get("rank"),
                "category": x.get("category"),
                "headline": x.get("headline"),
                "anchor_title": x.get("anchor_title"),
                "summary_lines": x.get("summary_lines"),
                "links": x.get("links"),
            }
            for x in issues
        ],
    }, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
