from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date, timedelta
from typing import Any

from app.db.supabase_client import get_supabase


IMPORTANCE_RANK = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}

EVENT_TYPE_KEYWORDS = {
    "inflation": ["물가", "CPI", "PCE", "PPI", "금리", "환율", "국채금리", "연준", "달러", "나스닥", "미국증시"],
    "employment": ["고용", "실업률", "비농업고용", "임금", "금리인하", "달러", "미국증시"],
    "rate": ["기준금리", "FOMC", "금통위", "연준", "달러", "채권금리", "환율", "증시"],
    "growth": ["GDP", "경기침체", "성장률", "기업실적", "증시"],
    "housing": ["주택", "부동산", "전세", "월세", "금리", "대출"],
    "manufacturing": ["PMI", "제조업", "서비스업", "경기선행", "반도체"],
    "sentiment": ["소비자심리", "소비자신뢰", "소비", "경기전망", "소매판매"],
    "macro": ["금리", "환율", "증시", "채권", "경기"],
}


@dataclass
class EventBoostConfig:
    enabled: bool
    level: str
    max_keywords: int
    news_links_per_topic: int
    lookback_hours: int
    event_keywords: list[str]
    reason: str
    event_count: int
    events: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_event_name(name: str | None) -> str:
    value = (name or "").lower().strip()
    replacements = {
        "소비자물가지수": "cpi",
        "consumer price index": "cpi",
        "personal consumption expenditures": "pce",
        "비농업 고용": "비농업고용",
        "nonfarm payrolls": "비농업고용",
    }

    for old, new in replacements.items():
        value = value.replace(old, new)

    for ch in [" ", "\t", "\n", "(", ")", "[", "]", "{", "}", "·", "ㆍ", ",", ".", ":", ";", "|", "/", "\\", "_", "-"]:
        value = value.replace(ch, "")

    return value


def _event_key(event: dict[str, Any]) -> str:
    return "|".join([
        str(event.get("event_date") or "")[:10],
        str(event.get("country") or "").strip().lower(),
        str(event.get("currency") or "").strip().lower(),
        _normalize_event_name(event.get("event_name")),
    ])


def _score_event(event: dict[str, Any]) -> float:
    importance = str(event.get("importance") or "").lower()
    status = str(event.get("status") or "").lower()

    status_score = {
        "released": 40,
        "followup_needed": 35,
        "scheduled": 20,
        "done": 10,
    }.get(status, 0)

    return (
        IMPORTANCE_RANK.get(importance, 0) * 1000
        + (500 if event.get("actual_value") else 0)
        + (120 if event.get("forecast_value") else 0)
        + (80 if event.get("previous_value") else 0)
        + status_score
    )


def dedupe_economic_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """같은 날짜/국가/통화/지표명 이벤트를 하나로 병합합니다."""
    grouped: dict[str, dict[str, Any]] = {}

    for event in events or []:
        key = _event_key(event)
        if not key.replace("|", ""):
            continue

        if key not in grouped:
            grouped[key] = {**event, "_merged_count": int(event.get("_merged_count") or 1)}
            continue

        current = grouped[key]
        winner = event if _score_event(event) > _score_event(current) else current
        loser = current if winner is event else event

        grouped[key] = {
            **loser,
            **winner,
            "previous_value": winner.get("previous_value") or loser.get("previous_value"),
            "forecast_value": winner.get("forecast_value") or loser.get("forecast_value"),
            "actual_value": winner.get("actual_value") or loser.get("actual_value"),
            "note": winner.get("note") or loser.get("note"),
            "_merged_count": int(current.get("_merged_count") or 1) + 1,
        }

    return sorted(grouped.values(), key=lambda x: (str(x.get("event_date") or ""), str(x.get("event_time") or "")))


def build_event_keywords(events: list[dict[str, Any]]) -> list[str]:
    keywords: list[str] = []

    for event in dedupe_economic_events(events):
        importance = str(event.get("importance") or "").lower()
        content_usage = str(event.get("content_usage") or "").lower()

        if importance not in ["critical", "high"] and content_usage not in ["article", "cardnews", "telegram", "followup"]:
            continue

        event_type = str(event.get("event_type") or "macro").lower()
        base = [
            event.get("event_name"),
            event.get("country"),
            event.get("currency"),
        ]

        for item in base + EVENT_TYPE_KEYWORDS.get(event_type, EVENT_TYPE_KEYWORDS["macro"]):
            text = str(item or "").strip()
            if text and text not in keywords:
                keywords.append(text)

    return keywords[:30]


def get_event_boost_config(events: list[dict[str, Any]]) -> EventBoostConfig:
    deduped = dedupe_economic_events(events)
    event_keywords = build_event_keywords(deduped)

    has_critical = any(str(e.get("importance") or "").lower() == "critical" for e in deduped)
    has_high = any(str(e.get("importance") or "").lower() == "high" for e in deduped)

    if has_critical:
        return EventBoostConfig(
            enabled=True,
            level="critical",
            max_keywords=80,
            news_links_per_topic=15,
            lookback_hours=24,
            event_keywords=event_keywords,
            reason="critical economic event detected",
            event_count=len(deduped),
            events=deduped,
        )

    if has_high:
        return EventBoostConfig(
            enabled=True,
            level="high",
            max_keywords=60,
            news_links_per_topic=10,
            lookback_hours=24,
            event_keywords=event_keywords,
            reason="high importance economic event detected",
            event_count=len(deduped),
            events=deduped,
        )

    return EventBoostConfig(
        enabled=False,
        level="normal",
        max_keywords=30,
        news_links_per_topic=5,
        lookback_hours=24,
        event_keywords=[],
        reason="no major economic event",
        event_count=len(deduped),
        events=deduped,
    )


def fetch_economic_events_for_boost(days_before: int = 0, days_after: int = 1) -> list[dict[str, Any]]:
    """오늘~내일 경제지표를 읽어서 이벤트일 검색 강화 판단에 사용합니다."""
    client = get_supabase()
    start = date.today() - timedelta(days=days_before)
    end = date.today() + timedelta(days=days_after)

    return (
        client.table("economic_events")
        .select("*")
        .gte("event_date", start.isoformat())
        .lte("event_date", end.isoformat())
        .execute()
        .data
    )


def get_today_event_boost_config(days_before: int = 0, days_after: int = 1) -> EventBoostConfig:
    events = fetch_economic_events_for_boost(days_before=days_before, days_after=days_after)
    return get_event_boost_config(events)
