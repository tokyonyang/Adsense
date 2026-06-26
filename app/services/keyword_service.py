from __future__ import annotations

from app.repositories.keyword_repository import KeywordRepository
from app.repositories.run_repository import RunRepository


class KeywordService:
    def __init__(self):
        self.repo = KeywordRepository()
        self.runs = RunRepository()

    def list_keywords(self, user_id: str | None = None, category: str | None = None, limit: int = 50):
        return self.repo.list_recent(user_id=user_id, category=category, limit=limit)

    def collect_keywords(
        self,
        user_id: str | None = None,
        category_filter: str = "all",
        lookback_hours: int = 24,
        max_keywords: int = 30,
        seed_keywords: list[str] | None = None,
        news_links_per_topic: int = 5,
        run_source: str = "manual_or_cron",
        boost_summary: dict | None = None,
    ):
        """
        키워드 수집 실행.

        v1.9 변경:
        - 경제지표 이벤트일에는 seed_keywords, max_keywords, news_links_per_topic을 외부에서 주입받을 수 있게 확장
        - 기존 호출부와 호환되도록 기본값 유지
        """
        seed_keywords = seed_keywords or []

        run = self.runs.start_run(
            "collect_keywords",
            user_id=user_id,
            category_filter=category_filter,
            lookback_hours=lookback_hours,
            summary={
                "run_source": run_source,
                "max_keywords": max_keywords,
                "news_links_per_topic": news_links_per_topic,
                "seed_keywords": seed_keywords,
                "boost": boost_summary or {},
            },
        )

        # TODO:
        # 실제 기존 trend_sources.py / naver_sources.py 로직과 연결할 때 아래 값을 전달하세요.
        #
        # collect_trends(
        #   max_keywords=max_keywords,
        #   lookback_hours=lookback_hours,
        #   seed_keywords=seed_keywords,
        #   news_links_per_topic=news_links_per_topic
        # )

        sample_items = [
            {
                "user_id": user_id,
                "run_id": run["id"] if run else None,
                "keyword": "기준금리 전망",
                "category": "economy",
                "source": "sample",
                "approx_traffic": 5000,
                "naver_news_count": 18,
                "datalab_score": 83,
                "interest_score": 92,
                "evidence_count": news_links_per_topic,
                "adsense_safety": "caution",
                "content_score": 90,
                "status": "candidate",
            },
            {
                "user_id": user_id,
                "run_id": run["id"] if run else None,
                "keyword": "전기요금 절약",
                "category": "living",
                "source": "sample",
                "approx_traffic": 4200,
                "naver_news_count": 11,
                "datalab_score": 76,
                "interest_score": 84,
                "evidence_count": min(news_links_per_topic, 10),
                "adsense_safety": "safe",
                "content_score": 86,
                "status": "candidate",
            },
        ]

        # 경제지표 이벤트 키워드가 있으면 후보로 함께 저장합니다.
        for idx, keyword in enumerate(seed_keywords[: max(0, max_keywords - len(sample_items))], start=1):
            sample_items.append(
                {
                    "user_id": user_id,
                    "run_id": run["id"] if run else None,
                    "keyword": keyword,
                    "category": "economy",
                    "source": "economic_event_boost",
                    "approx_traffic": 0,
                    "naver_news_count": 0,
                    "datalab_score": 0,
                    "interest_score": max(75, 95 - idx),
                    "evidence_count": news_links_per_topic,
                    "adsense_safety": "caution",
                    "content_score": max(70, 95 - idx),
                    "status": "candidate",
                }
            )

        inserted = 0
        for item in sample_items[:max_keywords]:
            self.repo.create(item)
            inserted += 1

        if run:
            self.runs.finish_run(
                run["id"],
                summary={
                    "inserted": inserted,
                    "max_keywords": max_keywords,
                    "news_links_per_topic": news_links_per_topic,
                    "seed_keywords_count": len(seed_keywords),
                    "boost": boost_summary or {},
                },
            )

        return {
            "inserted": inserted,
            "max_keywords": max_keywords,
            "news_links_per_topic": news_links_per_topic,
            "seed_keywords": seed_keywords,
            "items": sample_items[:max_keywords],
        }

    def convert_keyword(self, keyword_id: str, user_id: str | None = None, idea_type: str = "article"):
        keyword = self.repo.get(keyword_id)
        if not keyword:
            return None

        from app.repositories.content_repository import ContentIdeaRepository

        ideas = ContentIdeaRepository()
        payload = {
            "user_id": user_id,
            "keyword_id": keyword_id,
            "idea_type": idea_type,
            "title": f"{keyword['keyword']} 관련 콘텐츠 후보",
            "hook_point": f"{keyword['keyword']} 이슈를 쉽게 정리",
            "writing_angle": "검색 수요와 뉴스 근거를 바탕으로 한 정보형 콘텐츠",
            "category": keyword.get("category"),
            "priority": 1,
            "status": "candidate",
        }
        return ideas.create(payload)
