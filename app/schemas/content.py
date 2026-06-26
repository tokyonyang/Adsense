from pydantic import BaseModel


class GenerateArticleRequest(BaseModel):
    user_id: str | None = None
    idea_id: str
    tone: str | None = None


class SeoCheckRequest(BaseModel):
    user_id: str | None = None
    article_id: str | None = None
    title: str | None = None
    html: str | None = None
    category: str | None = None
