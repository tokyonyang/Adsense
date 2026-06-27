from __future__ import annotations

import html
import json
import os
import re
import time
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

import requests

from app.services.headline_news_image_service import render_headline_news_image
from app.services.telegram_photo_service import send_telegram_photo


KST = timezone(timedelta(hours=9))
NAVER_NEWS_URL = "https://openapi.naver.com/v1/search/news.json"
GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
TELEGRAM_API_BASE = "https://api.telegram.org/bot"

HEADLINE_QUERIES = [
    ("경제", "오늘 경제 주요 뉴스"),
    ("정치", "오늘 정치 주요 뉴스"),
    ("사회", "오늘 사회 주요 뉴스"),
    ("국제", "오늘 국제 주요 뉴스"),
    ("산업", "오늘 산업 주요 뉴스"),
    ("증시", "오늘 증시 환율 주요 뉴스"),
    ("IT", "오늘 IT 기업 주요 뉴스"),
    ("생활", "오늘 생활 날씨 주요 뉴스"),
    ("스포츠", "오늘 스포츠 주요 뉴스"),
]


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def strip_tags(text: str) -> str:
    text = html.unescape(text or "")
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_title(title: str) -> str:
    title = strip_tags(title)
    title = title.replace("...", "…")
    title = re.sub(r"\[[^\]]{1,20}\]", "", title)
    title = re.sub(r"\([^)]{1,20}\)$", "", title)
    title = re.sub(r"\s+", " ", title).strip(" -·ㆍ|")
    return title.strip()


def title_key(title: str) -> str:
    value = normalize_title(title).lower()
    value = re.sub(r"[^0-9a-z가-힣]", "", value)
    value = value.replace("종합", "").replace("속보", "")
    return value[:100]


def parse_date(value: str | None) -> datetime:
    if not value:
        return datetime.now(KST)
    try:
        return parsedate_to_datetime(value).astimezone(KST)
    except Exception:
        return datetime.now(KST)


def fetch_naver_news(category: str, query: str, display: int = 20) -> list[dict[str, Any]]:
    client_id = env("NAVER_CLIENT_ID")
    client_secret = env("NAVER_CLIENT_SECRET")
    if not client_id or not client_secret:
        return []

    headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
    params = {"query": query, "display": display, "start": 1, "sort": "date"}

    try:
        response = requests.get(NAVER_NEWS_URL, headers=headers, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        print(f"[naver] failed {query}: {exc}")
        return []

    rows = []
    for item in data.get("items", []):
        title = normalize_title(item.get("title", ""))
        if not title:
            continue
        rows.append({
            "category": category,
            "title": title,
            "url": item.get("originallink") or item.get("link"),
            "published_at": parse_date(item.get("pubDate")),
            "source": "naver",
            "query": query,
        })
    return rows


def fetch_google_news(category: str, query: str, limit: int = 15) -> list[dict[str, Any]]:
    try:
        import feedparser
    except Exception:
        return []

    url = GOOGLE_NEWS_RSS.format(query=quote_plus(query))
    try:
        feed = feedparser.parse(url)
    except Exception as exc:
        print(f"[google] failed {query}: {exc}")
        return []

    rows = []
    for entry in feed.entries[:limit]:
        title = normalize_title(getattr(entry, "title", ""))
        title = re.sub(r"\s+-\s+[^-]{1,30}$", "", title).strip()
        if not title:
            continue
        rows.append({
            "category": category,
            "title": title,
            "url": getattr(entry, "link", ""),
            "published_at": parse_date(getattr(entry, "published", "")),
            "source": "google",
            "query": query,
        })
    return rows


def collect_headlines(max_items: int = 10, lookback_hours: int = 24) -> list[dict[str, Any]]:
    now = datetime.now(KST)
    cutoff = now - timedelta(hours=lookback_hours)
    candidates: list[dict[str, Any]] = []

    for category, query in HEADLINE_QUERIES:
        candidates.extend(fetch_naver_news(category, query, display=14))
        time.sleep(0.15)

    if len(candidates) < 25:
        for category, query in HEADLINE_QUERIES:
            candidates.extend(fetch_google_news(category, query, limit=10))
            time.sleep(0.1)

    fresh = [item for item in candidates if item.get("published_at", now) >= cutoff]
    if len(fresh) < max_items:
        fresh = candidates

    deduped = []
    seen = set()
    for item in sorted(fresh, key=lambda x: x.get("published_at", now), reverse=True):
        tkey = title_key(item["title"])
        if len(item["title"]) < 8 or not tkey or tkey in seen:
            continue
        seen.add(tkey)
        deduped.append(item)
        if len(deduped) >= max_items:
            break

    return deduped[:max_items]


def _default_icon(category: str) -> str:
    return {
        "경제": "₩",
        "증시": "📉",
        "정치": "🏛",
        "사회": "📰",
        "국제": "🌍",
        "산업": "🏭",
        "생활": "☀",
        "IT": "AI",
        "스포츠": "⚽",
    }.get(category, "•")


def build_fallback_brief(headlines: list[dict[str, Any]]) -> list[dict[str, Any]]:
    briefs = []
    for item in headlines:
        title = item["title"]
        category = item.get("category", "주요")
        short_title = title if len(title) <= 24 else title[:24].rstrip() + "…"
        summaries = []
        summaries.append(title if len(title) <= 30 else title[:30].rstrip() + "…")
        summaries.append(f"{category} 분야 주요 이슈로 관심 확대")
        summaries.append("상세 내용은 본문 기사 확인 필요")

        keywords = []
        for token in re.findall(r"[가-힣A-Za-z0-9]{2,}", title):
            if token not in keywords and len(token) <= 10:
                keywords.append(token)
            if len(keywords) >= 3:
                break

        briefs.append({
            **item,
            "short_title": short_title,
            "highlight": "",
            "summaries": summaries[:3],
            "keywords": keywords[:3],
            "icon": _default_icon(category),
        })
    return briefs


def summarize_with_gemini(headlines: list[dict[str, Any]]) -> list[dict[str, Any]]:
    api_key = env("GEMINI_API_KEY")
    if not api_key:
        return build_fallback_brief(headlines)

    try:
        import google.generativeai as genai
    except Exception:
        return build_fallback_brief(headlines)

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        payload = [
            {"index": idx + 1, "category": h.get("category", "주요"), "title": h["title"]}
            for idx, h in enumerate(headlines)
        ]
        prompt = f"""
다음 한국 뉴스 헤드라인 10개를 카드형 뉴스 이미지에 넣을 수 있게 요약해줘.
반드시 JSON 배열만 반환해.
각 원소는 아래 키를 반드시 포함해:
index, short_title, highlight, summaries, keywords, icon

규칙:
- short_title: 18자 이내, 짧은 제목
- highlight: 강조 문구 1개, 16자 이내, 없으면 빈 문자열
- summaries: 3개 배열, 각 항목 18자 이내
- keywords: 2~3개 배열
- icon: 2자 이내 이모지 또는 짧은 텍스트
- 한국어만 사용
- 원문 헤드라인의 사실을 벗어나지 말 것
- 마크다운 금지

입력:
{json.dumps(payload, ensure_ascii=False)}
"""
        resp = model.generate_content(prompt)
        text = resp.text.strip()
        m = re.search(r"\[.*\]", text, re.S)
        if not m:
            return build_fallback_brief(headlines)
        arr = json.loads(m.group(0))
        mapped = []
        by_index = {i+1: h for i, h in enumerate(headlines)}
        for row in arr:
            source = by_index.get(int(row.get("index", 0)))
            if not source:
                continue
            mapped.append({
                **source,
                "short_title": str(row.get("short_title") or source["title"])[:28],
                "highlight": str(row.get("highlight") or "")[:20],
                "summaries": [str(x)[:24] for x in (row.get("summaries") or [])][:3],
                "keywords": [str(x)[:12] for x in (row.get("keywords") or [])][:3],
                "icon": str(row.get("icon") or _default_icon(source.get("category", "주요")))[:3],
            })
        if len(mapped) >= max(6, len(headlines) // 2):
            # preserve original order by title list
            order = {h["title"]: i for i, h in enumerate(headlines)}
            mapped.sort(key=lambda x: order.get(x["title"], 999))
            # fill missing
            have = {x["title"] for x in mapped}
            for h in headlines:
                if h["title"] not in have:
                    mapped.append(build_fallback_brief([h])[0])
            return mapped[:len(headlines)]
    except Exception as exc:
        print("[gemini summarize failed]", exc)

    return build_fallback_brief(headlines)


def weekday_ko(dt: datetime) -> str:
    return "월화수목금토일"[dt.weekday()]


def build_text_message(briefs: list[dict[str, Any]]) -> str:
    now = datetime.now(KST)
    header = f"{now:%Y년 %m월%d일}({weekday_ko(now)})☀️☀️🌤\n💛 아침 헤드라인 뉴스"
    lines = [header, ""]
    for idx, item in enumerate(briefs, start=1):
        lines.append(f"{idx}. {item.get('title','')}")
    return "\n".join(lines)


def send_telegram_message(text: str) -> dict[str, Any]:
    bot_token = env("TELEGRAM_BOT_TOKEN")
    chat_id = env("TELEGRAM_CHAT_ID")

    if not bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN이 설정되지 않았습니다.")
    if not chat_id:
        raise RuntimeError("TELEGRAM_CHAT_ID가 설정되지 않았습니다.")

    url = f"{TELEGRAM_API_BASE}{bot_token}/sendMessage"
    response = requests.post(
        url,
        json={
            "chat_id": chat_id,
            "text": text[:3900],
            "disable_web_page_preview": True,
        },
        timeout=30,
    )
    try:
        data = response.json()
    except Exception:
        data = {"ok": False, "description": response.text}

    if not response.ok or not data.get("ok"):
        raise RuntimeError(f"Telegram 텍스트 전송 실패: {data}")

    return data


def main():
    max_items = int(env("HEADLINE_NEWS_COUNT", "10"))
    lookback_hours = int(env("HEADLINE_LOOKBACK_HOURS", "24"))
    send_text_too = env("HEADLINE_SEND_TEXT", "true").lower() == "true"

    headlines = collect_headlines(max_items=max_items, lookback_hours=lookback_hours)
    briefs = summarize_with_gemini(headlines)

    output_dir = Path("tmp")
    output_dir.mkdir(exist_ok=True)
    image_path = output_dir / "morning_headline_news.png"

    render_headline_news_image(
        briefs,
        output_path=image_path,
        title="오늘의 헤드라인 뉴스",
    )

    caption = "💛 아침 헤드라인 뉴스\n오늘 주요 이슈를 카드형 이미지로 정리했습니다."
    photo_result = send_telegram_photo(image_path, caption=caption)
    print("[telegram photo sent]", photo_result.get("ok"))

    if send_text_too:
        text_message = build_text_message(briefs)
        msg_result = send_telegram_message(text_message)
        print("[telegram text sent]", msg_result.get("ok"))

    print("[output image]", image_path.resolve())


if __name__ == "__main__":
    main()
