from pydantic import BaseModel


class ProfileUpdate(BaseModel):
    email: str | None = None
    nickname: str | None = None
    plan: str | None = None
    preferred_categories: list[str] | None = None
    content_goal: str | None = None
    writing_tone: str | None = None
    publish_channel: str | None = None
    daily_idea_count: int | None = None
    site_memo: str | None = None
