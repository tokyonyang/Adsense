from __future__ import annotations

import json
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta

from app.services.headline_anchor_service import build_anchor_groups
from app.services.headline_cardnews_render_service import build_cardnews_pages
from app.services.headline_cardnews_summary_service import summarize_anchor_groups_with_gemini
from app.services.telegram_album_service import send_media_group, send_text_message

KST = timezone(timedelta(hours=9))


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def weekday_ko(dt: datetime) -> str:
    return "월화수목금토일"[dt.weekday()]


def build_link_digest(issues: list[dict]) -> str:
    now = datetime.now(KST)
    lines = [
        f"{now:%Y년 %m월%d일}({weekday_ko(now)})☀️☀️🌤",
        "💛 아침 헤드라인 뉴스 · 원문 링크",
        "",
        "※ 아래 목록은 카드뉴스 생성 기준이 된 헤드라인 List입니다.",
        "",
    ]

    for issue in issues:
        lines.append(f"{issue.get('rank')}. {issue.get('headline')}")
        if issue.get("anchor_title") and issue.get("anchor_title") != issue.get("headline"):
            lines.append(f"   기준 헤드라인: {issue.get('anchor_title')}")
        for idx, link in enumerate(issue.get("links") or [], start=1):
            title = link.get("title") or link.get("domain") or "원문"
            url = link.get("url") or ""
            if url:
                lines.append(f"   {idx}) {title}\n      {url}")
        lines.append("")

    return "\n".join(lines).strip()


def main():
    max_anchors = int(env("HEADLINE_CARDNEWS_ISSUES", "5"))
    lookback_hours = int(env("HEADLINE_LOOKBACK_HOURS", "48"))
    similar_lookback_hours = int(env("HEADLINE_SIMILAR_LOOKBACK_HOURS", "72"))

    anchor_groups = build_anchor_groups(
        max_anchors=max_anchors,
        lookback_hours=lookback_hours,
        similar_lookback_hours=similar_lookback_hours,
    )

    if not anchor_groups:
        send_text_message("💛 아침 헤드라인 뉴스\n\n헤드라인 뉴스 List를 생성하지 못해 카드뉴스를 만들지 못했습니다.")
        return

    issues = summarize_anchor_groups_with_gemini(anchor_groups)

    out_dir = Path("tmp/headline_cardnews")
    image_paths = build_cardnews_pages(issues, output_dir=out_dir)

    caption = "💛 아침 헤드라인 뉴스\n헤드라인 List 기준으로 유사 기사 3건씩 묶어 정리했습니다."
    send_media_group(image_paths, caption=caption)

    if env("HEADLINE_SEND_LINK_DIGEST", "true").lower() == "true":
        send_text_message(build_link_digest(issues), disable_web_page_preview=True)

    print("[anchor-cardnews result]")
    print(json.dumps({
        "anchor_groups": len(anchor_groups),
        "issues": len(issues),
        "pages": len(image_paths),
        "anchor_preview": [
            {
                "rank": g.get("rank"),
                "category": g.get("category"),
                "anchor_title": g.get("anchor_title"),
                "related_articles": len(g.get("articles") or []),
                "related_titles": [a.get("title") for a in (g.get("articles") or [])],
            }
            for g in anchor_groups
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
