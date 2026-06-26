from app.repositories.base_repository import BaseRepository


class ContentIdeaRepository(BaseRepository):
    table_name = "content_ideas"


class ArticleRepository(BaseRepository):
    table_name = "generated_articles"


class CardnewsRepository(BaseRepository):
    table_name = "cardnews_drafts"
