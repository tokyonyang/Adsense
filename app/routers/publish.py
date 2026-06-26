from fastapi import APIRouter
from pydantic import BaseModel
from app.services.publish_service import PublishService

router = APIRouter(prefix="/api/publish", tags=["publish"])


class CalendarCreate(BaseModel):
    user_id: str | None = None
    title: str
    calendar_type: str = "publish"
    scheduled_at: str
    category: str | None = None
    note: str | None = None


class WordpressPublishRequest(BaseModel):
    user_id: str | None = None
    article_id: str
    status: str = "draft"


class TelegramSendRequest(BaseModel):
    user_id: str | None = None
    message: str


@router.get("/calendar")
def list_calendar(user_id: str | None = None):
    return {"ok": True, "items": PublishService().list_calendar(user_id=user_id)}


@router.post("/calendar")
def add_calendar_item(payload: CalendarCreate):
    return {"ok": True, "data": PublishService().add_calendar_item(payload.model_dump())}


@router.post("/wordpress")
def publish_wordpress(payload: WordpressPublishRequest):
    data = PublishService().publish_wordpress(
        article_id=payload.article_id,
        user_id=payload.user_id,
        status=payload.status,
    )
    return {"ok": True, "data": data}


@router.post("/telegram")
def send_telegram(payload: TelegramSendRequest):
    data = PublishService().send_telegram(message=payload.message, user_id=payload.user_id)
    return {"ok": True, "data": data}
