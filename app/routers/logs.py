from fastapi import APIRouter
from app.db.supabase_client import get_supabase

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.get("")
def list_logs(user_id: str | None = None, limit: int = 50):
    client = get_supabase()
    query = client.table("dashboard_runs").select("*").order("started_at", desc=True)
    if user_id:
        query = query.eq("user_id", user_id)
    return {"ok": True, "items": query.limit(limit).execute().data}
