from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any


IMPORTANCE_RANK = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}

EVENT_TYPE_KEYWORDS = {
    "inflation": ["물가", "CPI", "PCE", "PPI", "금리", "환율", "국채금리", "연준", "달러", "나스닥"],
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
    max_keywords: int
    news_links_per_topic: int
    lookback_hours: int
    event_keywords: list[str]
    reason: str


def _normalize_event_name(name: str | None) -> str:
    return (name or "").lower().replace(" ", "").strip()


def dedupe_economic_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """같은 날짜/국가/통화/지표명 이벤트를 하나로 병합합니다."""
    grouped: dict[str, dict[str, Any]] = {}

    def key(event: dict[str, Any]) -> str:
        return "|".join([
            str(event.get("event_date") or "")[:10],
            str(event.get("country") or "").strip().lower(),
            str(event.get("currency") or "").strip().lower(),
            _normalize_event_name(event.get("event_name")),
        ])

    def score(event: dict[str, Any]) -> float:
        return (
            IMPORTANCE_RANK.get(str(event.get("importance") or "").lower(), 0) * 1000
            + (500 if event.get("actual_value") else 0)
            + (120 if event.get("forecast_value") else 0)
            + (80 if event.get("previous_value") else 0)
        )

    for event in events:
        k = key(event)
        if not k.replace("|", ""):
            continue

        if k not in grouped:
            grouped[k] = {**event, "_merged_count": 1}
            continue

        current = grouped[k]
        winner = event if score(event) > score(current) else current
        loser = current if winner is event else event

        grouped[k] = {
            **loser,
            **winner,
            "previous_value": winner.get("previous_value") or loser.get("previous_value"),
            "forecast_value": winner.get("forecast_value") or loser.get("forecast_value"),
            "actual_value": winner.get("actual_value") or loser.get("actual_value"),
            "note": winner.get("note") or loser.get("note"),
            "_merged_count": int(current.get("_merged_count", 1)) + 1,
        }

    return sorted(grouped.values(), key=lambda x: (str(x.get("event_date") or ""), str(x.get("event_time") or "")))


def build_event_keywords(events: list[dict[str, Any]]) -> list[str]:
    deduped = dedupe_economic_events(events)
    keywords: list[str] = []

    for event in deduped:
        importance = str(event.get("importance") or "").lower()
        content_usage = str(event.get("content_usage") or "").lower()

        if importance not in ["critical", "high"] and content_usage not in ["article", "cardnews", "telegram", "followup"]:
            continue

        event_type = str(event.get("event_type") or "macro")
        base = [
            event.get("event_name"),
            event.get("country"),
            event.get("currency"),
        ]

        for item in base + EVENT_TYPE_KEYWORDS.get(event_type, EVENT_TYPE_KEYWORDS["macro"]):
            if item and str(item).strip() not in keywords:
                keywords.append(str(item).strip())

    return keywords[:30]


def get_event_boost_config(events: list[dict[str, Any]]) -> EventBoostConfig:
    deduped = dedupe_economic_events(events)
    event_keywords = build_event_keywords(deduped)

    has_critical = any(str(e.get("importance") or "").lower() == "critical" for e in deduped)
    has_high = any(str(e.get("importance") or "").lower() == "high" for e in deduped)

    if has_critical:
        return EventBoostConfig(
            enabled=True,
            max_keywords=80,
            news_links_per_topic=15,
            lookback_hours=24,
            event_keywords=event_keywords,
            reason="critical economic event detected",
        )

    if has_high:
        return EventBoostConfig(
            enabled=True,
            max_keywords=60,
            news_links_per_topic=10,
            lookback_hours=24,
            event_keywords=event_keywords,
            reason="high importance economic event detected",
        )

    return EventBoostConfig(
        enabled=False,
        max_keywords=30,
        news_links_per_topic=5,
        lookback_hours=24,
        event_keywords=[],
        reason="no major economic event",
    )
