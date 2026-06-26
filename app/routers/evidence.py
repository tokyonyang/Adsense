from fastapi import APIRouter, Query
from app.db.supabase_client import get_supabase

router = APIRouter(prefix="/api/evidence", tags=["evidence"])


@router.get("")
def list_evidence(keyword_id: str | None = None, limit: int = 50):
    client = get_supabase()
    query = client.table("news_evidence").select("*").order("created_at", desc=True)
    if keyword_id:
        query = query.eq("keyword_id", keyword_id)
    return {"ok": True, "items": query.limit(limit).execute().data}


@router.post("/refresh")
def refresh_evidence(keyword_id: str):
    # TODO: 기존 news_sources.py / naver_sources.py 근거자료 수집 연결
    return {"ok": True, "message": "근거자료 재수집 기능은 기존 뉴스 수집 로직 연결 후 활성화됩니다."}
