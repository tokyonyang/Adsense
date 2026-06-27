from __future__ import annotations

import json

from app.services.event_boost_service import get_today_event_boost_config
from app.services.keyword_service import KeywordService
from app.services.sns_trend_service import SnsTrendService
from app.services.telegram_report_service import send_pipeline_summary_report, validate_telegram_env


def main():
    print("[telegram env]")
    print(json.dumps(validate_telegram_env(), ensure_ascii=False, indent=2))

    boost = get_today_event_boost_config(days_before=0, days_after=1)

    keyword_result = KeywordService().collect_keywords(
        category_filter="all",
        lookback_hours=boost.lookback_hours,
        max_keywords=boost.max_keywords,
        seed_keywords=boost.event_keywords,
        news_links_per_topic=boost.news_links_per_topic,
        run_source="daily_pipeline_v1_10_2",
        boost_summary=boost.to_dict(),
    )

    sns_result = SnsTrendService().collect_trends(
        platforms=["google", "youtube", "naver", "tiktok"],
        category_filter="all",
        limit=30 if not boost.enabled else 50,
    )

    keyword_summary = {
        "inserted": keyword_result.get("inserted"),
        "max_keywords": keyword_result.get("max_keywords"),
        "news_links_per_topic": keyword_result.get("news_links_per_topic"),
        "seed_keywords_count": len(keyword_result.get("seed_keywords") or []),
    }

    sns_summary = {
        "inserted": sns_result.get("inserted"),
    }

    telegram_result = send_pipeline_summary_report(
        boost=boost.to_dict(),
        keyword_result=keyword_summary,
        sns_result=sns_summary,
        fail_silently=False,
    )

    result = {
        "event_boost": boost.to_dict(),
        "keyword_result": keyword_summary,
        "sns_result": sns_summary,
        "telegram_result": {
            "ok": telegram_result.get("ok"),
            "sent_parts": telegram_result.get("sent_parts", 0),
            "chat_id_masked": telegram_result.get("chat_id_masked"),
        },
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
