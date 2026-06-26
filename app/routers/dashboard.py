from fastapi import APIRouter, Query
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
def get_summary(user_id: str | None = Query(default=None)):
    return {"ok": True, "data": DashboardService().summary(user_id=user_id)}
