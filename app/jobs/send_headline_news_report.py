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

DATELESS_FALLBACK_QUERIES = [
    ("경제", "경제 뉴스"),
    ("증시", "증시 뉴스"),
    ("정치", "정치 뉴스"),
    ("사회", "사회 뉴스"),
    ("국제", "국제 뉴스"),
    ("산업", "산업 뉴스"),
    ("IT", "IT 뉴스"),
    ("생활", "날씨 뉴스"),
    ("스포츠", "스포츠 뉴스"),
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
    "별자리",
]

PLACEHOLDER_PHRASES = [
    "세부 내용 확인 필요",
    "분야 주요 이슈",
    "후속 기사 확인 필요",
    "상세 내용은 본문 기사 확인 필요",
]


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def strip_tags(text: str) -> str:
    text = html.unescape(text or "")
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_text(text: str) -> str:
    text = strip_tags(text)
    text = text.replace("...", "…").replace("⋯", "…")
    text = re.sub(r"\s+", " ", text)
    return text.strip(" -·ㆍ|")


def normalize_title(title: str) -> str:
    title = normalize_text(title)
    title = re.sub(r"\[[^\]]{1,20}\]", "", title)
    title = re.sub(r"\([^)]{1,20}\)$", "", title)
    title = re.sub(r"\s+", " ", title)
    return title.strip(" -·ㆍ|")


def is_truncated_text(text: str) -> bool:
    text = normalize_text(text)
    return text.endswith("…") or "…" in text or "..." in text or "⋯" in text


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

    if clean.count("·") >= 4 or clean.count("ㆍ") >= 4:
        return True

    if compact in ["오늘의주요뉴스", "오늘주요뉴스", "주요뉴스", "오늘뉴스"]:
        return True

    return False


def title_key(title: str) -> str:
    value = normalize_title(title).lower()
    value = re.sub(r"[^0-9a-z가-힣]", "", value)
    value = value.replace("종합", "").replace("속보", "")
    return value[:100]


def parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).astimezone(KST)
    except Exception:
        return None


def is_fresh(published_at: datetime | None, cutoff: datetime) -> bool:
    if published_at is None:
        return False
    return published_at >= cutoff


def is_obviously_old(published_at: datetime | None, hard_cutoff: datetime) -> bool:
    if published_at is None:
        return False
    return published_at < hard_cutoff


def with_today_query(query: str) -> str:
    now = datetime.now(KST)
    return f'{now:%Y년 %-m월 %-d일} {query}' if os.name != "nt" else f'{now.year}년 {now.month}월 {now.day}일 {query}'


def fetch_naver_news(category: str, query: str, display: int = 30) -> list[dict[str, Any]]:
    client_id = env("NAVER_CLIENT_ID")
    client_secret = env("NAVER_CLIENT_SECRET")
    if not client_id or not client_secret:
        print("[naver] missing NAVER_CLIENT_ID/NAVER_CLIENT_SECRET")
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
        desc = normalize_text(item.get("description", ""))
        published_at = parse_date(item.get("pubDate"))

        if not title or is_roundup_or_low_value_title(title):
            continue

        rows.append({
            "category": category,
            "title": title,
            "description": desc,
            "url": item.get("originallink") or item.get("link"),
            "published_at": published_at,
            "source": "naver",
            "query": query,
            "needs_rewrite": is_truncated_text(title),
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
        desc = normalize_text(getattr(entry, "summary", ""))
        published_at = parse_date(getattr(entry, "published", ""))

        if not title or is_roundup_or_low_value_title(title):
            continue

        rows.append({
            "category": category,
            "title": title,
            "description": desc,
            "url": getattr(entry, "link", ""),
            "published_at": published_at,
            "source": "google",
            "query": query,
            "needs_rewrite": is_truncated_text(title),
        })
    return rows


def _dedupe_and_rank(items: list[dict[str, Any]], max_items: int) -> list[dict[str, Any]]:
    seen = set()
    deduped = []
    category_count: dict[str, int] = {}

    def score(item: dict[str, Any]):
        published = item.get("published_at") or datetime(1970, 1, 1, tzinfo=KST)
        return (
            1 if item.get("needs_rewrite") else 0,
            0 if item.get("description") else 1,
            0 if item.get("source") == "naver" else 1,
            -published.timestamp(),
        )

    for item in sorted(items, key=score):
        title = item["title"]
        if is_roundup_or_low_value_title(title):
            continue

        key = title_key(title)
        if not key or key in seen:
            continue

        cat = item.get("category", "주요")
        if category_count.get(cat, 0) >= 2 and len(deduped) < max_items - 2:
            continue

        seen.add(key)
        deduped.append(item)
        category_count[cat] = category_count.get(cat, 0) + 1

        if len(deduped) >= max_items:
            break

    if len(deduped) < max_items:
        for item in sorted(items, key=score):
            key = title_key(item.get("title", ""))
            if not key or key in seen:
                continue
            seen.add(key)
            deduped.append(item)
            if len(deduped) >= max_items:
                break

    return deduped[:max_items]


def collect_candidates(query_set: list[tuple[str, str]], *, dated: bool = False) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []

    for category, query in query_set:
        q = with_today_query(query) if dated else query
        candidates.extend(fetch_naver_news(category, q, display=30))
        time.sleep(0.15)

    if len(candidates) < 20:
        for category, query in query_set:
            q = with_today_query(query) if dated else query
            candidates.extend(fetch_google_news(category, q, limit=12))
            time.sleep(0.1)

    return candidates


def collect_headlines(max_items: int = 10, lookback_hours: int = 24, fallback_hours: int = 48, relaxed_hours: int = 72) -> list[dict[str, Any]]:
    """
    v1.21:
    - 24h → 48h → 날짜포함 재검색 → 72h relaxed 순서로 시도
    - 그래도 없으면 날짜 불명 최신 상단 후보를 제한적으로 사용
    - 명백히 오래된 날짜는 제외
    - workflow 자체는 실패시키지 않음
    """
    now = datetime.now(KST)
    primary_cutoff = now - timedelta(hours=lookback_hours)
    fallback_cutoff = now - timedelta(hours=fallback_hours)
    relaxed_cutoff = now - timedelta(hours=relaxed_hours)

    candidates = collect_candidates(HEADLINE_QUERIES, dated=False)

    primary = [item for item in candidates if is_fresh(item.get("published_at"), primary_cutoff)]
    print(f"[headline freshness] primary {lookback_hours}h candidates:", len(primary))
    selected = _dedupe_and_rank(primary, max_items=max_items)

    if len(selected) < max_items:
        fallback = [
            item for item in candidates
            if is_fresh(item.get("published_at"), fallback_cutoff)
            and title_key(item.get("title", "")) not in {title_key(x.get("title", "")) for x in selected}
        ]
        print(f"[headline freshness] fallback {fallback_hours}h candidates:", len(fallback))
        selected += _dedupe_and_rank(fallback, max_items=max_items - len(selected))

    if len(selected) < max_items:
        dated_candidates = collect_candidates(DATELESS_FALLBACK_QUERIES, dated=True)
        dated_fresh = [
            item for item in dated_candidates
            if is_fresh(item.get("published_at"), relaxed_cutoff)
            and title_key(item.get("title", "")) not in {title_key(x.get("title", "")) for x in selected}
        ]
        print("[headline freshness] dated-query relaxed candidates:", len(dated_fresh))
        selected += _dedupe_and_rank(dated_fresh, max_items=max_items - len(selected))

    if len(selected) < max_items:
        relaxed = [
            item for item in candidates
            if is_fresh(item.get("published_at"), relaxed_cutoff)
            and title_key(item.get("title", "")) not in {title_key(x.get("title", "")) for x in selected}
        ]
        print(f"[headline freshness] relaxed {relaxed_hours}h candidates:", len(relaxed))
        selected += _dedupe_and_rank(relaxed, max_items=max_items - len(selected))

    if len(selected) < max_items:
        # 마지막 안전망: 날짜가 없는 후보만 제한 사용. 명백히 오래된 날짜 후보는 사용 금지.
        undated = [
            item for item in candidates
            if item.get("published_at") is None
            and title_key(item.get("title", "")) not in {title_key(x.get("title", "")) for x in selected}
        ]
        print("[headline freshness] undated fallback candidates:", len(undated))
        selected += _dedupe_and_rank(undated, max_items=max_items - len(selected))

    # 최종 필터: 날짜가 있으면서 72시간보다 오래된 것은 무조건 제외
    selected = [
        item for item in selected
        if not is_obviously_old(item.get("published_at"), relaxed_cutoff)
    ]

    print("[headline selected]", len(selected))

    return selected[:max_items]


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


def _extract_keywords(text: str, limit: int = 3) -> list[str]:
    words = []
    for token in re.findall(r"[가-힣A-Za-z0-9]{2,}", text or ""):
        if token not in words and len(token) <= 10:
            words.append(token)
        if len(words) >= limit:
            break
    return words


def clean_sentence(text: str, max_len: int = 52) -> str:
    text = normalize_text(text)
    text = text.replace("…", " ").replace("...", " ").replace("⋯", " ")
    text = re.sub(r"\s+", " ", text).strip(" -·ㆍ|")

    for phrase in PLACEHOLDER_PHRASES:
        text = text.replace(phrase, "")

    if len(text) <= max_len:
        return text

    for sep in ["다.", "요.", "임.", "·", " - ", " | ", ":"]:
        pos = text.find(sep, 24)
        if 28 <= pos <= max_len:
            return text[: pos + len(sep)].strip()

    return text[: max_len - 1].rstrip() + "…"


def safe_headline_from_title(title: str, description: str = "", max_len: int = 52) -> str:
    title = normalize_title(title)
    description = normalize_text(description)
    candidate = description if (is_truncated_text(title) and description) else title
    return clean_sentence(candidate, max_len=max_len)


def build_grounded_summaries(item: dict[str, Any]) -> list[str]:
    title = item.get("title", "")
    desc = item.get("description", "")
    category = item.get("category", "주요")
    published_at = item.get("published_at")
    source = item.get("source", "")

    lines = []

    if desc:
        lines.append(clean_sentence(desc, max_len=32))

    keywords = _extract_keywords(title + " " + desc, limit=3)
    if keywords:
        lines.append("핵심: " + ", ".join(keywords))

    if published_at:
        try:
            lines.append(f"{category} · {published_at.strftime('%m/%d %H:%M')}")
        except Exception:
            pass
    elif source:
        lines.append(f"{category} · {source}")

    result = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if any(p in line for p in PLACEHOLDER_PHRASES):
            continue
        if line not in result:
            result.append(line)

    return result[:3]


def build_fallback_brief(headlines: list[dict[str, Any]]) -> list[dict[str, Any]]:
    briefs = []
    for item in headlines:
        title = item.get("title", "")
        desc = item.get("description", "")
        category = item.get("category", "주요")
        headline_text = safe_headline_from_title(title, desc, max_len=52)
        summaries = build_grounded_summaries(item)
        keywords = _extract_keywords(headline_text + " " + desc, limit=3)

        briefs.append({
            **item,
            "headline_text": headline_text,
            "short_title": headline_text if len(headline_text) <= 20 else headline_text[:20].rstrip() + "…",
            "highlight": "",
            "summaries": summaries,
            "keywords": keywords,
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

    fallback_map = {h["title"]: build_fallback_brief([h])[0] for h in headlines}

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        payload = [
            {
                "index": i + 1,
                "category": h.get("category", "주요"),
                "title": h["title"],
                "description": h.get("description", ""),
                "published_at": h.get("published_at").strftime("%Y-%m-%d %H:%M") if h.get("published_at") else "",
                "source": h.get("source", ""),
            }
            for i, h in enumerate(headlines)
        ]

        prompt = f"""
다음 한국 뉴스 후보를 아침 헤드라인 카드와 텔레그램 텍스트용으로 정리해줘.
반드시 JSON 배열만 반환해.
각 원소는 index, headline_text, short_title, highlight, summaries, keywords, icon 키를 포함해야 해.

절대 규칙:
- headline_text는 46자 이내 완성형 헤드라인.
- headline_text와 summaries는 반드시 입력 title/description 내용과 일치해야 한다.
- 입력에 없는 사실을 새로 만들지 마.
- summaries는 기사 내용에 직접 근거한 bullet 2~3개.
- summaries에 "세부 내용 확인 필요", "분야 주요 이슈", "후속 기사 확인 필요" 금지.
- headline_text에 "...", "…", "⋯", "오늘의 주요뉴스", "1부 주요뉴스", "外" 금지.
- short_title은 18자 이내.
- keywords는 2~3개.
- icon은 2자 이내.
- 한국어만 사용.
- 마크다운 금지.

입력:
{json.dumps(payload, ensure_ascii=False)}
"""
        response = model.generate_content(prompt)
        text = response.text.strip()
        match = re.search(r"\[.*\]", text, re.S)
        if not match:
            return build_fallback_brief(headlines)

        rows = json.loads(match.group(0))
        by_index = {i + 1: h for i, h in enumerate(headlines)}
        mapped = []

        for row in rows:
            src = by_index.get(int(row.get("index", 0)))
            if not src:
                continue

            fb = fallback_map[src["title"]]
            headline_text = clean_sentence(str(row.get("headline_text") or fb["headline_text"]), max_len=58)

            if is_truncated_text(headline_text) or is_roundup_or_low_value_title(headline_text):
                headline_text = fb["headline_text"]

            raw_summaries = row.get("summaries") or []
            summaries = []
            for s in raw_summaries:
                s = clean_sentence(str(s), max_len=32)
                if not s:
                    continue
                if any(p in s for p in PLACEHOLDER_PHRASES):
                    continue
                if s not in summaries:
                    summaries.append(s)

            if not summaries:
                summaries = fb["summaries"]

            keywords = [str(k)[:12] for k in (row.get("keywords") or fb["keywords"])][:3]

            mapped.append({
                **src,
                "headline_text": headline_text,
                "short_title": str(row.get("short_title") or headline_text)[:28],
                "highlight": str(row.get("highlight") or "")[:20],
                "summaries": summaries[:3],
                "keywords": keywords,
                "icon": str(row.get("icon") or fb["icon"])[:3],
            })

        if mapped:
            order = {h["title"]: i for i, h in enumerate(headlines)}
            mapped.sort(key=lambda x: order.get(x["title"], 999))
            have = {x["title"] for x in mapped}
            for h in headlines:
                if h["title"] not in have:
                    mapped.append(fallback_map[h["title"]])
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

    if not briefs:
        lines.append("최근 헤드라인 후보가 부족해 이미지 리포트를 생성하지 못했습니다.")
        return "\n".join(lines)

    for idx, item in enumerate(briefs, start=1):
        headline = item.get("headline_text") or safe_headline_from_title(item.get("title", ""), item.get("description", ""))
        headline = headline.replace("…", "").replace("...", "").strip()
        lines.append(f"{idx}. {headline}")

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
    fallback_hours = int(env("HEADLINE_FALLBACK_LOOKBACK_HOURS", "48"))
    relaxed_hours = int(env("HEADLINE_RELAXED_LOOKBACK_HOURS", "72"))
    send_text_too = env("HEADLINE_SEND_TEXT", "true").lower() == "true"

    headlines = collect_headlines(
        max_items=max_items,
        lookback_hours=lookback_hours,
        fallback_hours=fallback_hours,
        relaxed_hours=relaxed_hours,
    )

    if not headlines:
        msg = build_text_message([])
        print("[headline empty]")
        print(msg)
        send_telegram_message(msg)
        return

    briefs = summarize_with_gemini(headlines)

    output_dir = Path("tmp")
    output_dir.mkdir(exist_ok=True)
    image_path = output_dir / "morning_headline_news.png"

    render_headline_news_image(briefs, output_path=image_path, title="오늘의 헤드라인 뉴스")

    caption = "💛 아침 헤드라인 뉴스\n최근 주요 이슈를 카드형 이미지로 정리했습니다."
    send_telegram_photo(image_path, caption=caption)
    print("[telegram photo sent] ok")

    if send_text_too:
        text_message = build_text_message(briefs)
        print("[headline text preview]")
        print(text_message)
        send_telegram_message(text_message)
        print("[telegram text sent] ok")

    print("[briefs preview]")
    print(json.dumps([
        {
            "category": b.get("category"),
            "published_at": b.get("published_at").strftime("%Y-%m-%d %H:%M") if b.get("published_at") else "",
            "headline_text": b.get("headline_text"),
            "summaries": b.get("summaries"),
            "keywords": b.get("keywords"),
            "source": b.get("source"),
        } for b in briefs
    ], ensure_ascii=False, indent=2))

    print("[output image]", image_path.resolve())


if __name__ == "__main__":
    main()
