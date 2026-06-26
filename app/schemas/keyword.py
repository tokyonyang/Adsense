from pydantic import BaseModel


class KeywordCollectRequest(BaseModel):
    user_id: str | None = None
    category_filter: str = "all"
    lookback_hours: int = 24
    max_keywords: int = 30


class ConvertKeywordRequest(BaseModel):
    user_id: str | None = None
    idea_type: str = "article"
