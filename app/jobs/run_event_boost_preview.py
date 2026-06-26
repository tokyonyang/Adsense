from __future__ import annotations

import json

from app.services.event_boost_service import get_today_event_boost_config


def main():
    boost = get_today_event_boost_config(days_before=0, days_after=1)
    print(json.dumps(boost.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
