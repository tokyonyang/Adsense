from __future__ import annotations

import json

from app.services.event_boost_service import get_today_event_boost_config
from app.services.keyword_service import KeywordService
from app.services.sns_trend_service import SnsTrendService


def main():
    """
    v1.9 자동 파이프라인.

    흐름:
    1. economic_events에서 오늘~내일 주요 경제지표 확인
    2. high/critical 이벤트가 있으면 키워드 수집량과 근거자료 수집량 상향
    3. 이벤트 관련 seed keywords를 키워드 수집에 추가
    4. 기존 SNS 트렌드 수집도 함께 실행
    """
    boost = get_today_event_boost_config(days_before=0, days_after=1)

    keyword_result = KeywordService().collect_keywords(
        category_filter="all",
        lookback_hours=boost.lookback_hours,
        max_keywords=boost.max_keywords,
        seed_keywords=boost.event_keywords,
        news_links_per_topic=boost.news_links_per_topic,
        run_source="daily_pipeline_v1_9",
        boost_summary=boost.to_dict(),
    )

    sns_result = SnsTrendService().collect_trends(
        platforms=["google", "youtube", "naver", "tiktok"],
        category_filter="all",
        limit=30 if not boost.enabled else 50,
    )

    result = {
        "event_boost": boost.to_dict(),
        "keyword_result": {
            "inserted": keyword_result.get("inserted"),
            "max_keywords": keyword_result.get("max_keywords"),
            "news_links_per_topic": keyword_result.get("news_links_per_topic"),
            "seed_keywords_count": len(keyword_result.get("seed_keywords") or []),
        },
        "sns_result": {
            "inserted": sns_result.get("inserted"),
        },
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
