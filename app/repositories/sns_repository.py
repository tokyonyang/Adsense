from app.repositories.base_repository import BaseRepository


class SnsTrendRepository(BaseRepository):
    table_name = "sns_trends"

    def list_recent(self, user_id: str | None = None, platform: str | None = None, category: str | None = None, limit: int = 50):
        query = self.client.table(self.table_name).select("*").order("collected_at", desc=True)
        if user_id:
            query = query.eq("user_id", user_id)
        if platform and platform != "all":
            query = query.eq("platform", platform)
        if category and category != "all":
            query = query.eq("category", category)
        return query.limit(limit).execute().data
