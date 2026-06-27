from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


def _load_latest_report_payload() -> dict[str, Any] | None:
    """로컬 reports/latest_daily_hotissue.json이 있으면 우선 사용합니다.

    GitHub Actions 워크플로우는 실행마다 새 환경이라 reports 파일이 항상 존재하지는 않습니다.
    존재하지 않으면 동일 엔진으로 새 payload를 생성합니다.
    """
    path = Path("reports/latest_daily_hotissue.json")
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def build_daily_hotissue_payload(*, prefer_saved: bool = True) -> dict[str, Any]:
    load_dotenv()

    if prefer_saved:
        saved = _load_latest_report_payload()
        if saved and (saved.get("hot_items") or saved.get("items")):
            if "hot_items" not in saved and "items" in saved:
                saved["hot_items"] = saved.get("items") or []
            return saved

    from app.services.daily_hotissue_engine import build_daily_hotissue_payload as build_payload

    return build_payload(send_report=False, save_report=False)


def _article_from_daily_item(item: dict[str, Any], article: dict[str, Any]) -> dict[str, Any]:
    category = item.get("category") or item.get("category_label") or item.get("category_id") or "주요"
    return {
        "category": category,
        "title": article.get("title") or item.get("keyword") or "",
        "description": article.get("description") or article.get("summary") or article.get("title") or "",
        "url": article.get("url") or "",
        "published_at": article.get("published_at") or article.get("published") or "",
        "source": article.get("source") or article.get("provider") or article.get("domain") or "",
        "query": item.get("keyword") or "",
    }


def _simple_issue_key(item: dict[str, Any]) -> str:
    text = f"{item.get('keyword','')} {item.get('category','')} " + " ".join(
        a.get("title", "") for a in (item.get("articles") or item.get("news") or [])[:2]
    )
    text = text.lower()
    tokens = re.findall(r"[가-힣A-Za-z0-9]{2,}", text)
    generic = {"경제", "금융", "증권", "투자", "사회", "국제", "정부", "시장", "관련", "상승", "하락"}
    tokens = [t for t in tokens if t not in generic][:5]
    return "|".join(tokens)


def _dedupe_hot_items(hot_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    result = []
    for item in hot_items:
        key = _simple_issue_key(item)
        if key and key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def hot_items_to_anchor_groups(hot_items: list[dict[str, Any]], *, max_issues: int = 5) -> list[dict[str, Any]]:
    groups = []
    deduped_items = _dedupe_hot_items(hot_items)
    for idx, item in enumerate(deduped_items[:max_issues], start=1):
        raw_articles = item.get("articles") or item.get("news") or []
        articles = [_article_from_daily_item(item, article) for article in raw_articles[:3]]

        category = item.get("category") or item.get("category_label") or item.get("category_id") or "주요"
        keyword = item.get("keyword") or item.get("title") or ""

        if not articles:
            articles.append({
                "category": category,
                "title": keyword,
                "description": item.get("why_important") or item.get("angle") or item.get("description") or keyword,
                "url": "",
                "published_at": item.get("published_at") or "",
                "source": item.get("source") or "",
                "query": keyword,
            })

        groups.append({
            "rank": idx,
            "daily_rank": item.get("rank") or idx,
            "category": category,
            "slot": item.get("slot") or "",
            "category_id": item.get("category_id") or category,
            "anchor_title": keyword,
            "anchor": item,
            "articles": articles[:3],
            "keywords": [
                x for x in [
                    keyword,
                    category,
                    item.get("slot"),
                    item.get("why_important"),
                    item.get("blog_angle"),
                ] if x
            ],
            "interest_label": item.get("interest_label") or "",
            "traffic_label": item.get("traffic_label") or "",
            "score": item.get("score"),
            "editorial_score": item.get("editorial_score"),
            "adsense_score": item.get("adsense_score"),
            "why_important": item.get("why_important"),
            "card_angle": item.get("card_angle"),
        })
    return groups
