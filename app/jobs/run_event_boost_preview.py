from __future__ import annotations

from datetime import date, timedelta

from app.db.supabase_client import get_supabase
from app.services.event_boost_service import get_event_boost_config


def fetch_event_window(days_before: int = 0, days_after: int = 1):
    client = get_supabase()
    start = date.today() - timedelta(days=days_before)
    end = date.today() + timedelta(days=days_after)

    return (
        client.table("economic_events")
        .select("*")
        .gte("event_date", start.isoformat())
        .lte("event_date", end.isoformat())
        .execute()
        .data
    )


def main():
    events = fetch_event_window()
    config = get_event_boost_config(events)

    print({
        "event_boost_enabled": config.enabled,
        "reason": config.reason,
        "max_keywords": config.max_keywords,
        "news_links_per_topic": config.news_links_per_topic,
        "lookback_hours": config.lookback_hours,
        "event_keywords": config.event_keywords,
    })

    # 다음 연결 단계:
    # KeywordService().collect_keywords(
    #     category_filter="all",
    #     lookback_hours=config.lookback_hours,
    #     max_keywords=config.max_keywords,
    #     seed_keywords=config.event_keywords,
    #     news_links_per_topic=config.news_links_per_topic,
    # )


if __name__ == "__main__":
    main()
