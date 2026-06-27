from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from dotenv import load_dotenv


def env_true(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "y", "on"}


def env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except Exception:
        return default


def build_daily_hotissue_payload() -> dict[str, Any]:
    """Daily AdSense SEO Hot Issue Report와 같은 로직으로 HOT Issue payload를 생성합니다.

    Morning Headline News가 별도로 뉴스를 다시 뽑지 않도록, main.py의 Daily 수집/점수/카테고리 균형 로직을 그대로 호출합니다.
    """
    load_dotenv()

    import main as daily_main

    args = SimpleNamespace(
        geo=os.getenv("GOOGLE_TRENDS_GEO", "KR"),
        max_keywords=env_int("MAX_KEYWORDS", 30),
        max_posts=env_int("MAX_POSTS_PER_RUN", 10),
        topics=os.getenv("SELECTED_TOPICS", ""),
        category_filter=os.getenv("CATEGORY_FILTER", "all"),
        lookback_hours=env_int("LOOKBACK_HOURS", 24),
        include_seed_keywords=env_true("INCLUDE_SEED_KEYWORDS", "false"),
    )

    if not daily_main._env_true("ALLOW_SMALLER_LIMITS"):
        args.max_keywords = max(args.max_keywords, 30)
        args.max_posts = max(args.max_posts, 10)

    hot_issue_count = max(1, daily_main._safe_int_env("HOT_ISSUE_COUNT", args.max_posts))
    card_news_count = max(0, daily_main._safe_int_env("CARD_NEWS_COUNT", 3))
    article_count = max(0, daily_main._safe_int_env("ARTICLE_COUNT", 3))
    links_per_topic = max(1, daily_main._safe_int_env("NEWS_LINKS_PER_TOPIC", 5))
    fallback_lookback_hours = daily_main._safe_int_env("FALLBACK_LOOKBACK_HOURS", 48)
    auto_fallback = daily_main._env_true("AUTO_FALLBACK", "true")

    topics = daily_main._parse_topics(args.topics)
    allowed_categories = daily_main._parse_category_filter(args.category_filter)
    include_seed_keywords = daily_main._env_true("INCLUDE_SEED_KEYWORDS", "false") or args.include_seed_keywords

    digest_item_count = max(args.max_posts, hot_issue_count, card_news_count, article_count)
    items, raw_keywords, keywords, effective_categories, effective_lookback_hours, fallback_info = daily_main._build_idea_digest_with_fallback(
        args=args,
        topics=topics,
        initial_categories=allowed_categories,
        include_seed_keywords=include_seed_keywords,
        max_items=digest_item_count,
        links_per_topic=links_per_topic,
        base_lookback_hours=args.lookback_hours,
        auto_fallback=auto_fallback,
        fallback_lookback_hours=fallback_lookback_hours,
    )

    hot_items = daily_main._select_hot_issue_items(items, hot_issue_count)
    card_items = daily_main._select_card_news_items(hot_items, card_news_count)
    article_items = daily_main._select_article_items(hot_items, article_count)

    return {
        "items": items,
        "hot_items": hot_items,
        "card_items": card_items,
        "article_items": article_items,
        "raw_keywords": raw_keywords,
        "keywords": keywords,
        "effective_categories": effective_categories,
        "effective_lookback_hours": effective_lookback_hours,
        "fallback_info": fallback_info,
        "hot_issue_count": hot_issue_count,
        "card_news_count": card_news_count,
        "article_count": article_count,
    }


def hot_items_to_anchor_groups(hot_items: list[dict[str, Any]], *, max_issues: int = 5) -> list[dict[str, Any]]:
    """Daily HOT Issue TOP items를 카드뉴스 anchor group으로 변환합니다."""
    groups = []
    for idx, item in enumerate(hot_items[:max_issues], start=1):
        news = item.get("news") or []
        articles = []
        for article in news[:3]:
            articles.append({
                "category": item.get("category_label") or item.get("category_id") or "주요",
                "title": article.get("title") or item.get("keyword") or "",
                "description": article.get("description") or article.get("summary") or article.get("title") or "",
                "url": article.get("url") or "",
                "published_at": article.get("published_at") or article.get("published") or "",
                "source": article.get("source") or article.get("provider") or "",
                "query": item.get("keyword") or "",
            })

        if not articles:
            articles.append({
                "category": item.get("category_label") or item.get("category_id") or "주요",
                "title": item.get("keyword") or "",
                "description": item.get("angle") or "",
                "url": "",
                "published_at": item.get("published_at") or "",
                "source": item.get("source") or "",
                "query": item.get("keyword") or "",
            })

        groups.append({
            "rank": idx,
            "daily_rank": item.get("rank") or idx,
            "category": item.get("category_label") or item.get("category_id") or "주요",
            "category_id": item.get("category_id") or "other",
            "anchor_title": item.get("keyword") or "",
            "anchor": item,
            "articles": articles[:3],
            "keywords": [item.get("keyword") or ""] + [str(k) for k in (item.get("category_label"), item.get("traffic_label")) if k],
            "interest_label": item.get("interest_label") or "",
            "traffic_label": item.get("traffic_label") or "",
        })
    return groups
