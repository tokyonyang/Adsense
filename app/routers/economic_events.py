from fastapi import APIRouter, Query
from app.schemas.economic_event import EconomicEventCreate, EconomicEventUpdate
from app.services.economic_calendar_service import EconomicCalendarService

router = APIRouter(prefix="/api/economic-events", tags=["economic-events"])


@router.get("")
def list_events(
    start_date: str | None = None,
    end_date: str | None = None,
    country: str | None = None,
    importance: str | None = None,
):
    items = EconomicCalendarService().list_events(
        start_date=start_date,
        end_date=end_date,
        country=country,
        importance=importance,
    )
    return {"ok": True, "items": items}


@router.post("")
def create_event(payload: EconomicEventCreate):
    data = EconomicCalendarService().create_event(payload.model_dump(mode="json"))
    return {"ok": True, "data": data}


@router.patch("/{event_id}")
def update_event(event_id: str, payload: EconomicEventUpdate):
    data = EconomicCalendarService().update_event(event_id, payload.model_dump())
    return {"ok": True, "data": data}


@router.post("/{event_id}/convert")
def convert_event(event_id: str, user_id: str | None = None, idea_type: str = "article"):
    data = EconomicCalendarService().convert_event(event_id, user_id=user_id, idea_type=idea_type)
    return {"ok": bool(data), "data": data}
