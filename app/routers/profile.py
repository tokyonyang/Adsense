from fastapi import APIRouter, Query
from app.db.supabase_client import get_supabase
from app.schemas.profile import ProfileUpdate

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("")
def get_profile(user_id: str | None = Query(default=None), email: str | None = Query(default=None)):
    client = get_supabase()
    query = client.table("user_profiles").select("*")
    if user_id:
        query = query.eq("user_id", user_id)
    elif email:
        query = query.eq("email", email)
    else:
        return {"ok": True, "data": None}

    data = query.limit(1).execute().data
    return {"ok": True, "data": data[0] if data else None}


@router.patch("")
def update_profile(payload: ProfileUpdate, user_id: str | None = Query(default=None)):
    client = get_supabase()
    clean = {k: v for k, v in payload.model_dump().items() if v is not None}

    if not user_id and not clean.get("email"):
        return {"ok": False, "message": "user_id 또는 email이 필요합니다."}

    if user_id:
        data = client.table("user_profiles").upsert({"user_id": user_id, **clean}, on_conflict="user_id").execute().data
    else:
        data = client.table("user_profiles").upsert(clean, on_conflict="email").execute().data

    return {"ok": True, "data": data}
