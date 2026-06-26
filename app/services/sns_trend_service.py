from app.repositories.sns_repository import SnsTrendRepository
from app.repositories.run_repository import RunRepository


class SnsTrendService:
    def __init__(self):
        self.repo = SnsTrendRepository()
        self.runs = RunRepository()

    def list_trends(self, user_id: str | None = None, platform: str | None = None, category: str | None = None, limit: int = 50):
        return self.repo.list_recent(user_id=user_id, platform=platform, category=category, limit=limit)

    def collect_trends(self, user_id: str | None = None, platforms: list[str] | None = None, category_filter: str = "all", limit: int = 30):
        platforms = platforms or ["google", "youtube", "naver"]
        run = self.runs.start_run("collect_sns_trends", user_id=user_id, category_filter=category_filter)

        # TODO: Google Trends / YouTube Data API / Naver API 실제 연결
        sample = [
            {
                "user_id": user_id,
                "run_id": run["id"] if run else None,
                "platform": "youtube",
                "keyword": "원달러 환율",
                "category": "economy",
                "rank": 1,
                "trend_score": 91,
                "spread_signal": "hot",
                "content_usage": "article",
                "commerce_score": 20,
                "adsense_safety": "caution",
            },
            {
                "user_id": user_id,
                "run_id": run["id"] if run else None,
                "platform": "tiktok",
                "keyword": "여름쿨링템",
                "hashtag": "#여름쿨링템",
                "category": "commerce",
                "rank": 2,
                "trend_score": 88,
                "spread_signal": "hot",
                "content_usage": "commerce",
                "commerce_score": 95,
                "adsense_safety": "safe",
            },
            {
                "user_id": user_id,
                "run_id": run["id"] if run else None,
                "platform": "naver",
                "keyword": "전기요금 절약",
                "category": "living",
                "rank": 3,
                "trend_score": 84,
                "spread_signal": "rising",
                "content_usage": "article",
                "commerce_score": 55,
                "adsense_safety": "safe",
            },
        ]

        inserted = 0
        for item in sample[:limit]:
            if item["platform"] in platforms or item["platform"] in ["tiktok"]:
                self.repo.create(item)
                inserted += 1

        if run:
            self.runs.finish_run(run["id"], summary={"inserted": inserted})

        return {"inserted": inserted, "items": sample[:limit]}

    def convert_trend(self, trend_id: str, user_id: str | None = None, idea_type: str = "article"):
        trend = self.repo.get(trend_id)
        if not trend:
            return None

        from app.repositories.content_repository import ContentIdeaRepository
        ideas = ContentIdeaRepository()

        title_map = {
            "article": f"{trend['keyword']} 이슈 정리",
            "cardnews": f"{trend['keyword']} 카드뉴스 구성안",
            "commerce": f"{trend['keyword']} 상품 소싱 후보",
        }

        payload = {
            "user_id": user_id,
            "sns_trend_id": trend_id,
            "idea_type": idea_type,
            "title": title_map.get(idea_type, f"{trend['keyword']} 콘텐츠 후보"),
            "hook_point": f"{trend['keyword']} 트렌드를 활용한 콘텐츠",
            "writing_angle": "SNS 확산도와 검색 수요를 함께 고려한 콘텐츠 방향",
            "category": trend.get("category"),
            "priority": int(trend.get("trend_score") or 0),
            "status": "candidate",
        }
        return ideas.create(payload)
