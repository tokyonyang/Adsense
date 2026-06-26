from pydantic import BaseModel


class SnsCollectRequest(BaseModel):
    user_id: str | None = None
    platforms: list[str] = ["google", "youtube", "naver"]
    category_filter: str = "all"
    limit: int = 30


class ConvertSnsTrendRequest(BaseModel):
    user_id: str | None = None
    idea_type: str = "article"
