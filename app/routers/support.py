from fastapi import APIRouter
from app.db.supabase_client import get_supabase
from app.schemas.support import SupportTicketCreate

router = APIRouter(prefix="/api/support", tags=["support"])


@router.post("")
def create_ticket(payload: SupportTicketCreate):
    client = get_supabase()
    data = client.table("support_tickets").insert(payload.model_dump()).execute().data
    return {"ok": True, "data": data}
