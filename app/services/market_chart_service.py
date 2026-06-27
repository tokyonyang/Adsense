from __future__ import annotations

import math
import os
import re
from datetime import datetime
from typing import Any

import requests


YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"


CHART_RULES = [
    {
        "name": "원·달러 환율",
        "symbol": "USDKRW=X",
        "keywords": ["환율", "원달러", "원·달러", "달러", "원화"],
        "unit": "원",
        "category": ["경제·금융"],
        "interpret_up": "원화 약세가 수입물가와 외국인 자금 흐름에 부담을 줄 수 있습니다.",
        "interpret_down": "원화 강세는 수입물가 부담 완화에 도움이 될 수 있습니다.",
    },
    {
        "name": "코스피",
        "symbol": "^KS11",
        "keywords": ["코스피", "국내 증시", "증시", "주식시장"],
        "unit": "pt",
        "category": ["증권·투자"],
        "interpret_up": "위험자산 선호가 살아나며 투자심리가 개선되는 흐름입니다.",
        "interpret_down": "차익실현과 위험 회피가 겹치면 변동성이 커질 수 있습니다.",
    },
    {
        "name": "코스닥",
        "symbol": "^KQ11",
        "keywords": ["코스닥"],
        "unit": "pt",
        "category": ["증권·투자"],
        "interpret_up": "성장주와 중소형주 투자심리가 개선되는 흐름입니다.",
        "interpret_down": "성장주 부담이 커지면 개인투자자 체감 변동성이 확대될 수 있습니다.",
    },
    {
        "name": "국제유가 WTI",
        "symbol": "CL=F",
        "keywords": ["유가", "국제유가", "WTI", "원유", "석유"],
        "unit": "$",
        "category": ["경제·금융", "국제", "국제·안전"],
        "interpret_up": "유가 상승은 운송비와 에너지 비용을 통해 물가 부담으로 번질 수 있습니다.",
        "interpret_down": "유가 안정은 물가와 에너지 비용 부담 완화에 긍정적입니다.",
    },
    {
        "name": "나스닥",
        "symbol": "^IXIC",
        "keywords": ["나스닥", "기술주", "AI주", "엔비디아", "테슬라"],
        "unit": "pt",
        "category": ["증권·투자", "산업·기업"],
        "interpret_up": "기술주 선호가 이어지면 국내 AI·반도체주에도 온기가 번질 수 있습니다.",
        "interpret_down": "미 기술주 조정은 국내 성장주와 반도체주 투자심리에 부담입니다.",
    },
]


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _keyword_text(issue: dict[str, Any]) -> str:
    parts = [
        issue.get("headline"),
        issue.get("anchor_title"),
        issue.get("category"),
        issue.get("slot"),
        issue.get("insight"),
    ]
    for line in issue.get("summary_lines") or []:
        parts.append(line)
    for k in issue.get("keywords") or []:
        parts.append(str(k))
    return " ".join(str(x or "") for x in parts).lower()


def detect_chart_rule(issue: dict[str, Any]) -> dict[str, Any] | None:
    if env("HEADLINE_ENABLE_MARKET_CHARTS", "true").lower() not in {"1", "true", "yes", "y", "on"}:
        return None

    text = _keyword_text(issue)
    category = str(issue.get("category") or "")

    for rule in CHART_RULES:
        if any(k.lower() in text for k in rule["keywords"]):
            return rule
        if category in rule.get("category", []):
            # 카테고리만으로는 환율/유가 등 너무 넓기 때문에 키워드 없는 경우는 일부 제외
            if rule["name"] in {"코스피", "나스닥"}:
                continue
    return None


def fetch_yahoo_chart(symbol: str, *, range_: str = "3mo", interval: str = "1d") -> list[dict[str, Any]]:
    url = YAHOO_CHART_URL.format(symbol=symbol)
    params = {"range": range_, "interval": interval}
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        result = data["chart"]["result"][0]
        timestamps = result.get("timestamp") or []
        quote = result.get("indicators", {}).get("quote", [{}])[0]
        closes = quote.get("close") or []
    except Exception as exc:
        print(f"[market chart] fetch failed symbol={symbol}: {exc}")
        return []

    rows = []
    for ts, close in zip(timestamps, closes):
        if close is None:
            continue
        rows.append({
            "date": datetime.fromtimestamp(ts).strftime("%m.%d"),
            "value": float(close),
        })
    return rows


def make_svg_sparkline(points: list[float], *, width: int = 420, height: int = 150) -> str:
    if len(points) < 2:
        return ""

    min_v, max_v = min(points), max(points)
    span = max(max_v - min_v, 1e-9)
    coords = []

    for i, value in enumerate(points):
        x = (i / max(1, len(points) - 1)) * width
        y = height - ((value - min_v) / span) * height
        coords.append(f"{x:.1f},{y:.1f}")

    polyline = " ".join(coords)
    last_x, last_y = coords[-1].split(",")

    return f"""
<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#f4c542" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#ff7a45" stop-opacity="0.95"/>
    </linearGradient>
  </defs>
  <line x1="0" y1="{height-1}" x2="{width}" y2="{height-1}" stroke="rgba(246,197,66,.24)" stroke-width="1"/>
  <line x1="0" y1="{height/2:.1f}" x2="{width}" y2="{height/2:.1f}" stroke="rgba(255,255,255,.10)" stroke-width="1"/>
  <polyline points="{polyline}" fill="none" stroke="url(#g)" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="{last_x}" cy="{last_y}" r="8" fill="#f4c542"/>
</svg>
""".strip()


def build_market_chart_for_issue(issue: dict[str, Any]) -> dict[str, Any] | None:
    rule = detect_chart_rule(issue)
    if not rule:
        return None

    rows = fetch_yahoo_chart(rule["symbol"], range_=env("HEADLINE_CHART_RANGE", "3mo"), interval=env("HEADLINE_CHART_INTERVAL", "1d"))

    if len(rows) < 2:
        return {
            "title": rule["name"],
            "symbol": rule["symbol"],
            "available": False,
            "caption": "시장 데이터 연결 대기",
            "insight_hint": "",
            "svg": "",
        }

    values = [x["value"] for x in rows]
    start, end = values[0], values[-1]
    change_pct = ((end - start) / start) * 100 if start else 0
    direction = "상승" if change_pct >= 0 else "하락"
    interpret = rule["interpret_up"] if change_pct >= 0 else rule["interpret_down"]

    caption = f"최근 {rule['name']} {direction} {abs(change_pct):.1f}%"
    insight_hint = f"{caption}. {interpret}"

    return {
        "title": rule["name"],
        "symbol": rule["symbol"],
        "available": True,
        "unit": rule["unit"],
        "start": round(start, 2),
        "end": round(end, 2),
        "change_pct": round(change_pct, 2),
        "direction": direction,
        "caption": caption,
        "insight_hint": insight_hint,
        "svg": make_svg_sparkline(values[-45:]),
        "latest_date": rows[-1]["date"],
    }


def attach_market_charts(issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for issue in issues:
        chart = build_market_chart_for_issue(issue)
        if chart:
            issue["chart"] = chart

            # Gemini insight가 약하거나 fallback이면 차트 기반 insight로 보강
            current = str(issue.get("insight") or "")
            weak_patterns = [
                "헤드라인 목록",
                "관련 기사",
                "묶었습니다",
                "확인 필요",
                "정리했습니다",
            ]
            if chart.get("insight_hint") and (not current or any(p in current for p in weak_patterns)):
                issue["insight"] = chart["insight_hint"]

    return issues
