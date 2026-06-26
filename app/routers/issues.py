from fastapi import APIRouter, Query
from app.services.keyword_service import KeywordService

router = APIRouter(prefix="/api/issues", tags=["issues"])


@router.get("/top")
def top_issues(user_id: str | None = None, category: str | None = None, limit: int = 10):
    items = KeywordService().list_keywords(user_id=user_id, category=category, limit=limit)
    items = sorted(items, key=lambda x: float(x.get("interest_score") or 0), reverse=True)
    return {"ok": True, "items": items[:limit]}
