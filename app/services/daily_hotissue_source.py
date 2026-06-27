from __future__ import annotations

from typing import Any

from dotenv import load_dotenv


def build_daily_hotissue_payload() -> dict[str, Any]:
    """Daily HOT Issue와 Morning 카드뉴스가 공유하는 마스터 payload를 생성합니다.

    기존 구현은 과거 main.py 내부 함수(_env_true, _build_idea_digest_with_fallback 등)에
    의존했기 때문에 v1.26.2 main.py 구조에서는 Morning workflow가 깨질 수 있었습니다.

    v1.27부터는 `app.services.daily_hotissue_engine`을 단일 엔진으로 사용합니다.
    """
    load_dotenv()
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


def hot_items_to_anchor_groups(hot_items: list[dict[str, Any]], *, max_issues: int = 5) -> list[dict[str, Any]]:
    """Daily HOT Issue TOP items를 카드뉴스 anchor group으로 변환합니다.

    지원하는 Daily item 형태:
    - v1.26.2: {keyword, category, articles: [...]}
    - 구버전: {keyword, category_label, news: [...]}
    """
    groups = []
    for idx, item in enumerate(hot_items[:max_issues], start=1):
        raw_articles = item.get("articles") or item.get("news") or []
        articles = [_article_from_daily_item(item, article) for article in raw_articles[:3]]

        category = item.get("category") or item.get("category_label") or item.get("category_id") or "주요"
        keyword = item.get("keyword") or item.get("title") or ""

        if not articles:
            articles.append({
                "category": category,
                "title": keyword,
                "description": item.get("angle") or item.get("description") or keyword,
                "url": "",
                "published_at": item.get("published_at") or "",
                "source": item.get("source") or "",
                "query": keyword,
            })

        groups.append({
            "rank": idx,
            "daily_rank": item.get("rank") or idx,
            "category": category,
            "category_id": item.get("category_id") or category,
            "anchor_title": keyword,
            "anchor": item,
            "articles": articles[:3],
            "keywords": [x for x in [keyword, category, item.get("traffic_label"), item.get("interest_label")] if x],
            "interest_label": item.get("interest_label") or "",
            "traffic_label": item.get("traffic_label") or "",
            "score": item.get("score"),
        })
    return groups
