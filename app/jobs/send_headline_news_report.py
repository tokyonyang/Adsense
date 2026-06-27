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

# v1.17: “오늘 주요뉴스” 같은 종합기사 유입을 줄이기 위해 더 구체적인 이슈형 쿼리로 변경
HEADLINE_QUERIES = [
    ("경제", "경제 정책 물가 유가 환율 최신뉴스"),
    ("증시", "코스피 코스닥 환율 증시 최신뉴스"),
    ("정치", "정부 국회 대통령 선관위 정치 최신뉴스"),
    ("사회", "사건 사고 법원 경찰 사회 최신뉴스"),
    ("국제", "국제 외교 중동 미국 중국 최신뉴스"),
    ("산업", "반도체 조선 자동차 배터리 산업 최신뉴스"),
    ("IT", "AI 네이버 카카오 통신 스마트폰 최신뉴스"),
    ("생활", "날씨 폭염 오존 교통 소비자 최신뉴스"),
    ("스포츠", "축구 야구 월드컵 스포츠 최신뉴스"),
]

ROUNDUP_TITLE_PATTERNS = [
    r"^오늘의?\s*주요뉴스$",
    r"^\d+\s*부\s*오늘의?\s*주요뉴스",
    r"^오늘의?\s*뉴스$",
    r"^주요뉴스$",
    r"뉴스\s*브리핑",
    r"헤드라인\s*뉴스",
    r"한눈에\s*보는",
    r"뉴스\s*모음",
    r"外\s*$",
    r"외\s*$",
    r"\s外\s*\[",
    r"\s외\s*\[",
]

LOW_VALUE_KEYWORDS = [
    "포토뉴스",
    "카드뉴스",
    "오늘의 운세",
    "연예",
    "열애설",
    "별자리",
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
    title = title.replace("⋯", "…")
    title = re.sub(r"\[[^\]]{1,20}\]", "", title)
    title = re.sub(r"\([^)]{1,20}\)$", "", title)
    title = re.sub(r"\s+", " ", title).strip(" -·ㆍ|")
    return title.strip()


def is_roundup_or_low_value_title(title: str) -> bool:
    clean = normalize_title(title)
    compact = re.sub(r"\s+", "", clean)

    if len(clean) < 8:
        return True

    for pattern in ROUNDUP_TITLE_PATTERNS:
        if re.search(pattern, clean, flags=re.IGNORECASE):
            return True

    for keyword in LOW_VALUE_KEYWORDS:
        if keyword in clean:
            return True

    # 여러 이슈를 억지로 이어붙인 제목은 카드 헤드라인으로 부적합
    if clean.count("·") >= 4 or clean.count("…") >= 3 or clean.count("ㆍ") >= 4:
        return True

    # “오늘의주요뉴스”처럼 공백 제거 후 잡히는 경우
    if compact in ["오늘의주요뉴스", "오늘주요뉴스", "주요뉴스", "오늘뉴스"]:
        return True

    return False


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
        if not title or is_roundup_or_low_value_title(title):
            continue
        rows.append({
            "category": category,
            "title": title,
            "description": normalize_title(item.get("description", "")),
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
        if not title or is_roundup_or_low_value_title(title):
            continue
        rows.append({
            "category": category,
            "title": title,
            "description": normalize_title(getattr(entry, "summary", "")),
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

    # 카테고리별로 조금 넉넉하게 수집
    for category, query in HEADLINE_QUERIES:
        candidates.extend(fetch_naver_news(category, query, display=20))
        time.sleep(0.15)

    if len(candidates) < 25:
        for category, query in HEADLINE_QUERIES:
            candidates.extend(fetch_google_news(category, query, limit=12))
            time.sleep(0.1)

    fresh = [item for item in candidates if item.get("published_at", now) >= cutoff]
    if len(fresh) < max_items:
        fresh = candidates

    deduped = []
    seen = set()

    # 같은 카테고리만 몰리지 않게 1차로 카테고리별 최신 2건 제한
    category_count: dict[str, int] = {}

    for item in sorted(fresh, key=lambda x: x.get("published_at", now), reverse=True):
        title = item["title"]
        if is_roundup_or_low_value_title(title):
            continue

        tkey = title_key(title)
        if not tkey or tkey in seen:
            continue

        category = item.get("category", "주요")
        if category_count.get(category, 0) >= 2 and len(deduped) < max_items - 2:
            continue

        seen.add(tkey)
        deduped.append(item)
        category_count[category] = category_count.get(category, 0) + 1

        if len(deduped) >= max_items:
            break

    # 부족하면 카테고리 제한 없이 채움
    if len(deduped) < max_items:
        for item in sorted(fresh, key=lambda x: x.get("published_at", now), reverse=True):
            title = item["title"]
            tkey = title_key(title)
            if is_roundup_or_low_value_title(title) or not tkey or tkey in seen:
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


def clean_text_for_message(title: str, max_len: int = 92) -> str:
    """
    텍스트 메시지용 제목.
    v1.17: 기존처럼 짧게 자르지 않고 최대한 원 제목을 유지합니다.
    다만 텔레그램 가독성을 위해 매우 긴 제목만 제한합니다.
    """
    title = normalize_title(title)
    title = re.sub(r"\s+", " ", title).strip()

    if len(title) <= max_len:
        return title

    # 문장 단위로 끊을 수 있으면 그 지점에서 마무리
    for sep in ["…", "·", " - ", " | ", ":"]:
        pos = title.find(sep, 35)
        if 40 <= pos <= max_len:
            return title[:pos].strip()

    return title[: max_len - 1].rstrip() + "…"


def build_fallback_brief(headlines: list[dict[str, Any]]) -> list[dict[str, Any]]:
    briefs = []
    for item in headlines:
        title = item["title"]
        category = item.get("category", "주요")
        desc = item.get("description") or ""
        short_title = title if len(title) <= 24 else title[:24].rstrip() + "…"

        summaries = []
        if desc:
            summaries.append(desc[:24].rstrip() + ("…" if len(desc) > 24 else ""))
        else:
            summaries.append(title[:24].rstrip() + ("…" if len(title) > 24 else ""))
        summaries.append(f"{category} 분야 주요 이슈")
        summaries.append("세부 내용 확인 필요")

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
            {
                "index": i + 1,
                "category": h.get("category", "주요"),
                "title": h["title"],
                "description": h.get("description", ""),
            }
            for i, h in enumerate(headlines)
        ]
        prompt = f"""
다음 한국 뉴스 헤드라인 10개를 카드형 뉴스 이미지에 넣을 수 있게 요약해줘.
반드시 JSON 배열만 반환해.
각 원소는 index, short_title, highlight, summaries, keywords, icon 키를 포함해야 해.

규칙:
- short_title: 18자 이내
- highlight: 16자 이내, 없으면 빈 문자열
- summaries: 3개 배열, 각 18자 이내
- keywords: 2~3개 배열
- icon: 2자 이내
- 한국어만 사용
- 사실 왜곡 금지
- 마크다운 금지
- “오늘의 주요뉴스”, “외”, “브리핑” 같은 표현으로 뭉뚱그리지 말 것
- 제목이 여러 이슈 묶음이면 가장 중요한 단일 이슈만 뽑아 요약할 것

입력:
{json.dumps(payload, ensure_ascii=False)}
"""
        resp = model.generate_content(prompt)
        text = resp.text.strip()
        m = re.search(r"\[.*\]", text, re.S)
        if not m:
            return build_fallback_brief(headlines)

        arr = json.loads(m.group(0))
        by_index = {i+1: h for i, h in enumerate(headlines)}
        mapped = []
        for row in arr:
            src = by_index.get(int(row.get("index", 0)))
            if not src:
                continue
            mapped.append({
                **src,
                "short_title": str(row.get("short_title") or src["title"])[:28],
                "highlight": str(row.get("highlight") or "")[:20],
                "summaries": [str(x)[:24] for x in (row.get("summaries") or [])][:3],
                "keywords": [str(x)[:12] for x in (row.get("keywords") or [])][:3],
                "icon": str(row.get("icon") or _default_icon(src.get("category", "주요")))[:3],
            })
        if mapped:
            order = {h["title"]: i for i, h in enumerate(headlines)}
            mapped.sort(key=lambda x: order.get(x["title"], 999))
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
        lines.append(f"{idx}. {clean_text_for_message(item.get('title',''))}")

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
        json={"chat_id": chat_id, "text": text[:3900], "disable_web_page_preview": True},
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

    render_headline_news_image(briefs, output_path=image_path, title="오늘의 헤드라인 뉴스")

    caption = "💛 아침 헤드라인 뉴스\n오늘 주요 이슈를 카드형 이미지로 정리했습니다."
    send_telegram_photo(image_path, caption=caption)
    print("[telegram photo sent] ok")

    if send_text_too:
        text_message = build_text_message(briefs)
        print("[headline text preview]")
        print(text_message)
        send_telegram_message(text_message)
        print("[telegram text sent] ok")

    print("[output image]", image_path.resolve())


if __name__ == "__main__":
    main()
