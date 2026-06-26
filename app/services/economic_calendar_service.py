from app.db.supabase_client import get_supabase


class EconomicCalendarService:
    def __init__(self):
        self.client = get_supabase()

    def list_events(self, start_date: str | None = None, end_date: str | None = None, country: str | None = None, importance: str | None = None):
        query = self.client.table("economic_events").select("*").order("event_date")

        if start_date:
            query = query.gte("event_date", start_date)
        if end_date:
            query = query.lte("event_date", end_date)
        if country and country != "all":
            query = query.eq("country", country)
        if importance and importance != "all":
            query = query.eq("importance", importance)

        return query.execute().data

    def create_event(self, payload: dict):
        return self.client.table("economic_events").insert(payload).execute().data

    def update_event(self, event_id: str, payload: dict):
        clean = {k: v for k, v in payload.items() if v is not None}
        return self.client.table("economic_events").update(clean).eq("id", event_id).execute().data

    def convert_event(self, event_id: str, user_id: str | None = None, idea_type: str = "article"):
        rows = self.client.table("economic_events").select("*").eq("id", event_id).limit(1).execute().data
        if not rows:
            return None

        event = rows[0]
        payload = {
            "user_id": user_id,
            "economic_event_id": event_id,
            "idea_type": idea_type,
            "title": f"{event['event_name']} 발표 전후 시장 영향 정리",
            "hook_point": f"{event['event_name']}이 금리·환율·증시에 미치는 영향",
            "writing_angle": "발표 전 전망과 발표 후 실제치 해설을 나누어 작성",
            "category": "economy",
            "priority": 1,
            "status": "candidate",
        }
        return self.client.table("content_ideas").insert(payload).execute().data
