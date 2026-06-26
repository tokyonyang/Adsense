from app.repositories.keyword_repository import KeywordRepository
from app.repositories.sns_repository import SnsTrendRepository


class DashboardService:
    def __init__(self):
        self.keywords = KeywordRepository()
        self.sns = SnsTrendRepository()

    def summary(self, user_id: str | None = None) -> dict:
        recent_keywords = self.keywords.list_recent(user_id=user_id, limit=10)
        recent_sns = self.sns.list_recent(user_id=user_id, limit=10)

        return {
            "kpi": {
                "recent_keywords": len(recent_keywords),
                "recent_sns_trends": len(recent_sns),
                "hot_issues": min(len(recent_keywords), 10),
                "article_candidates": 3,
                "cardnews_candidates": 3,
                "automation_status": "normal",
            },
            "top_keywords": recent_keywords,
            "top_sns_trends": recent_sns,
            "recommended_actions": [
                "SEO 검수 대상 글 확인",
                "경제지표 발표 일정 확인",
                "SNS 트렌드 기반 상품 소싱 후보 확인",
            ],
        }
