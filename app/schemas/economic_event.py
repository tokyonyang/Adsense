from pydantic import BaseModel
from datetime import date, time


class EconomicEventCreate(BaseModel):
    user_id: str | None = None
    event_date: date
    event_time: time | None = None
    country: str | None = None
    currency: str | None = None
    event_name: str
    event_type: str = "macro"
    importance: str = "medium"
    previous_value: str | None = None
    forecast_value: str | None = None
    actual_value: str | None = None
    content_usage: str = "watch"
    note: str | None = None


class EconomicEventUpdate(BaseModel):
    actual_value: str | None = None
    content_usage: str | None = None
    status: str | None = None
    note: str | None = None
