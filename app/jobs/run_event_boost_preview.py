from __future__ import annotations

import json

from app.services.event_boost_service import get_today_event_boost_config
from app.services.telegram_report_service import format_event_boost_section


def main():
    boost = get_today_event_boost_config(days_before=0, days_after=1)
    result = boost.to_dict()

    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("\n--- Telegram Preview ---")
    print(format_event_boost_section(result))


if __name__ == "__main__":
    main()
