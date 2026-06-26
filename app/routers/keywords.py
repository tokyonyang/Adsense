from fastapi import APIRouter, Query
from app.schemas.keyword import KeywordCollectRequest, ConvertKeywordRequest
from app.services.keyword_service import KeywordService

router = APIRouter(prefix="/api/keywords", tags=["keywords"])


@router.get("")
def list_keywords(user_id: str | None = None, category: str | None = None, limit: int = 50):
    items = KeywordService().list_keywords(user_id=user_id, category=category, limit=limit)
    return {"ok": True, "items": items}


@router.post("/collect")
def collect_keywords(payload: KeywordCollectRequest):
    data = KeywordService().collect_keywords(
        user_id=payload.user_id,
        category_filter=payload.category_filter,
        lookback_hours=payload.lookback_hours,
        max_keywords=payload.max_keywords,
    )
    return {"ok": True, "data": data}


@router.post("/{keyword_id}/convert")
def convert_keyword(keyword_id: str, payload: ConvertKeywordRequest):
    data = KeywordService().convert_keyword(keyword_id, user_id=payload.user_id, idea_type=payload.idea_type)
    return {"ok": bool(data), "data": data}
