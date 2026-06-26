from fastapi import APIRouter, Query
from app.schemas.content import GenerateArticleRequest, SeoCheckRequest
from app.services.content_service import ContentService

router = APIRouter(prefix="/api/content", tags=["content"])


@router.get("/ideas")
def list_ideas(user_id: str | None = None, limit: int = 50):
    return {"ok": True, "items": ContentService().list_ideas(user_id=user_id, limit=limit)}


@router.post("/articles/generate")
def generate_article(payload: GenerateArticleRequest):
    data = ContentService().generate_article(
        idea_id=payload.idea_id,
        user_id=payload.user_id,
        tone=payload.tone,
    )
    return {"ok": bool(data), "data": data}


@router.post("/cardnews/generate")
def generate_cardnews(idea_id: str, user_id: str | None = None):
    data = ContentService().generate_cardnews(idea_id=idea_id, user_id=user_id)
    return {"ok": bool(data), "data": data}


@router.post("/seo/check")
def seo_check(payload: SeoCheckRequest):
    data = ContentService().seo_check(
        title=payload.title,
        html=payload.html,
        category=payload.category,
        article_id=payload.article_id,
    )
    return {"ok": True, "data": data}
