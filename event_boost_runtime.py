"""
기존 루트 main.py와 연결하기 위한 선택형 helper.

사용 목적:
- 기존 자동화가 app/jobs/run_daily_pipeline.py가 아니라 루트 main.py를 실행하는 경우
- main.py가 환경변수 MAX_KEYWORDS, NEWS_LINKS_PER_TOPIC, LOOKBACK_HOURS를 읽는 구조라면
  실행 전에 이 helper로 환경변수를 자동 상향할 수 있습니다.

사용 예:
    from event_boost_runtime import apply_event_boost_env
    apply_event_boost_env()

주의:
- main.py가 import 시점에 이미 환경변수를 읽는다면, main.py 최상단에서 최대한 빨리 호출해야 합니다.
"""

from __future__ import annotations

import os
from datetime import date, timedelta
from typing import Any

import requests


IMPORTANCE_RANK = {"critical": 4, "high": 3, "medium": 2, "low": 1}

EVENT_TYPE_KEYWORDS = {
    "inflation": ["물가", "CPI", "PCE", "PPI", "금리", "환율", "국채금리", "연준", "달러", "나스닥"],
    "employment": ["고용", "실업률", "비농업고용", "임금", "금리인하", "달러"],
    "rate": ["기준금리", "FOMC", "연준", "달러", "채권금리", "환율", "증시"],
    "macro": ["금리", "환율", "증시", "채권", "경기"],
}


def _supabase_headers() -> dict[str, str]:
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    if not key:
        raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY 또는 SUPABASE_ANON_KEY가 필요합니다.")

    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


def fetch_events() -> list[dict[str, Any]]:
    url = (os.getenv("SUPABASE_URL") or "").rstrip("/")
    if not url:
        return []

    start = date.today().isoformat()
    end = (date.today() + timedelta(days=1)).isoformat()

    endpoint = (
        f"{url}/rest/v1/economic_events"
        f"?select=*&event_date=gte.{start}&event_date=lte.{end}"
    )

    response = requests.get(endpoint, headers=_supabase_headers(), timeout=30)
    response.raise_for_status()
    return response.json()


def build_keywords(events: list[dict[str, Any]]) -> list[str]:
    keywords = []

    for event in events:
        importance = str(event.get("importance") or "").lower()
        if importance not in ["critical", "high"]:
            continue

        event_type = str(event.get("event_type") or "macro").lower()
        for item in [event.get("event_name"), event.get("country"), event.get("currency")] + EVENT_TYPE_KEYWORDS.get(event_type, EVENT_TYPE_KEYWORDS["macro"]):
            text = str(item or "").strip()
            if text and text not in keywords:
                keywords.append(text)

    return keywords[:30]


def apply_event_boost_env() -> dict[str, Any]:
    events = fetch_events()
    keywords = build_keywords(events)

    has_critical = any(str(e.get("importance") or "").lower() == "critical" for e in events)
    has_high = any(str(e.get("importance") or "").lower() == "high" for e in events)

    if has_critical:
        config = {
            "EVENT_BOOST_ENABLED": "true",
            "EVENT_BOOST_LEVEL": "critical",
            "MAX_KEYWORDS": "80",
            "NEWS_LINKS_PER_TOPIC": "15",
            "LOOKBACK_HOURS": "24",
            "EVENT_SEED_KEYWORDS": ",".join(keywords),
        }
    elif has_high:
        config = {
            "EVENT_BOOST_ENABLED": "true",
            "EVENT_BOOST_LEVEL": "high",
            "MAX_KEYWORDS": "60",
            "NEWS_LINKS_PER_TOPIC": "10",
            "LOOKBACK_HOURS": "24",
            "EVENT_SEED_KEYWORDS": ",".join(keywords),
        }
    else:
        config = {
            "EVENT_BOOST_ENABLED": "false",
            "EVENT_BOOST_LEVEL": "normal",
        }

    os.environ.update(config)
    print("[event_boost_runtime]", config)
    return config
