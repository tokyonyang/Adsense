from fastapi import APIRouter, Query
from app.schemas.sns import SnsCollectRequest, ConvertSnsTrendRequest
from app.services.sns_trend_service import SnsTrendService

router = APIRouter(prefix="/api/sns", tags=["sns-trends"])


@router.get("/trends")
def list_sns_trends(
    user_id: str | None = None,
    platform: str | None = None,
    category: str | None = None,
    limit: int = 50,
):
    items = SnsTrendService().list_trends(user_id=user_id, platform=platform, category=category, limit=limit)
    return {"ok": True, "items": items}


@router.post("/collect")
def collect_sns_trends(payload: SnsCollectRequest):
    data = SnsTrendService().collect_trends(
        user_id=payload.user_id,
        platforms=payload.platforms,
        category_filter=payload.category_filter,
        limit=payload.limit,
    )
    return {"ok": True, "data": data}


@router.post("/trends/{trend_id}/convert")
def convert_sns_trend(trend_id: str, payload: ConvertSnsTrendRequest):
    data = SnsTrendService().convert_trend(trend_id, user_id=payload.user_id, idea_type=payload.idea_type)
    return {"ok": bool(data), "data": data}
