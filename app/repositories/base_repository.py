from app.db.supabase_client import get_supabase


class BaseRepository:
    table_name: str

    def __init__(self):
        self.client = get_supabase()

    def list(self, limit: int = 50, **filters):
        query = self.client.table(self.table_name).select("*")
        for key, value in filters.items():
            if value is not None:
                query = query.eq(key, value)
        return query.limit(limit).execute().data

    def create(self, data: dict):
        return self.client.table(self.table_name).insert(data).execute().data

    def update(self, row_id: str, data: dict):
        return self.client.table(self.table_name).update(data).eq("id", row_id).execute().data

    def get(self, row_id: str):
        data = self.client.table(self.table_name).select("*").eq("id", row_id).limit(1).execute().data
        return data[0] if data else None
