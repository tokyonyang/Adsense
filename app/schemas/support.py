from pydantic import BaseModel


class SupportTicketCreate(BaseModel):
    user_id: str | None = None
    email: str | None = None
    ticket_type: str = "오류 제보"
    title: str
    message: str
