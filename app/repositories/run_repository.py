from datetime import datetime, timezone
from app.repositories.base_repository import BaseRepository


class RunRepository(BaseRepository):
    table_name = "dashboard_runs"

    def start_run(self, run_type: str, user_id: str | None = None, **extra):
        payload = {
            "run_type": run_type,
            "user_id": user_id,
            "status": "running",
            **extra,
        }
        rows = self.create(payload)
        return rows[0] if rows else None

    def finish_run(self, run_id: str, status: str = "success", summary: dict | None = None, error_message: str | None = None):
        return self.update(run_id, {
            "status": status,
            "summary": summary or {},
            "error_message": error_message,
            "finished_at": datetime.now(timezone.utc).isoformat(),
        })
