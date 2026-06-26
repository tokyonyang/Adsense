from app.repositories.base_repository import BaseRepository


class KeywordRepository(BaseRepository):
    table_name = "trend_keywords"

    def list_recent(self, user_id: str | None = None, category: str | None = None, limit: int = 50):
        query = self.client.table(self.table_name).select("*").order("created_at", desc=True)
        if user_id:
            query = query.eq("user_id", user_id)
        if category and category != "all":
            query = query.eq("category", category)
        return query.limit(limit).execute().data
