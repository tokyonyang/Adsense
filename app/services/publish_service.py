from app.db.supabase_client import get_supabase


class PublishService:
    def __init__(self):
        self.client = get_supabase()

    def list_calendar(self, user_id: str | None = None):
        query = self.client.table("content_calendar").select("*").order("scheduled_at")
        if user_id:
            query = query.eq("user_id", user_id)
        return query.limit(100).execute().data

    def add_calendar_item(self, payload: dict):
        return self.client.table("content_calendar").insert(payload).execute().data

    def publish_wordpress(self, article_id: str, user_id: str | None = None, status: str = "draft"):
        # TODO: 기존 wp_publisher.py와 연결
        payload = {
            "user_id": user_id,
            "article_id": article_id,
            "target": "wordpress",
            "status": "pending",
        }
        return self.client.table("publish_logs").insert(payload).execute().data

    def send_telegram(self, message: str, user_id: str | None = None):
        # TODO: 기존 telegram_notify.py와 연결
        payload = {
            "user_id": user_id,
            "target": "telegram",
            "status": "pending",
            "error_message": None,
        }
        return self.client.table("publish_logs").insert(payload).execute().data
