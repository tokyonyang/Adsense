from __future__ import annotations

import html
import os
import re
import time
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.parse import quote_plus

import requests

KST = timezone(timedelta(hours=9))

NAVER_NEWS_URL = "https://openapi.naver.com/v1/search/news.json"
GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"

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

LOW_VALUE_KEYWORDS = ["포토뉴스", "카드뉴스", "오늘의 운세", "별자리"]

STOPWORDS = {
    "오늘", "뉴스", "속보", "종합", "단독", "기자", "관련", "주요", "오전", "오후",
    "있는", "없는", "한다", "했다", "위해", "대한", "이번", "최근", "연합뉴스",
    "네이트", "중소기업신문", "기준", "통해", "위한", "있는", "없는",
}


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
    title = re.sub(r"\[[^\]]{1,25}\]", "", title)
    title = re.sub(r"\([^)]{1,25}\)$", "", title)
    title = re.sub(r"\s+", " ", title)
    return title.strip(" -·ㆍ|")


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

    if clean.count("·") >= 5 or clean.count("ㆍ") >= 5:
        return True

    if compact in ["오늘의주요뉴스", "오늘주요뉴스", "주요뉴스", "오늘뉴스"]:
        return True

    return False


def parse_date(value: str | None):
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).astimezone(KST)
    except Exception:
        return None


def title_key(title: str) -> str:
    value = normalize_title(title).lower()
    value = re.sub(r"[^0-9a-zA-Z가-힣]", "", value)
    value = value.replace("종합", "").replace("속보", "")
    return value[:120]


def tokenize(text: str) -> set[str]:
    text = normalize_title(text).lower()
    tokens = []
    for token in re.findall(r"[가-힣A-Za-z0-9]{2,}", text):
        if token in STOPWORDS:
            continue
        if len(token) > 16:
            continue
        tokens.append(token)
    return set(tokens)


def keyword_query_from_title(title: str, max_terms: int = 5) -> str:
    tokens = list(tokenize(title))
    # 긴 고유명사 우선
    tokens.sort(key=lambda x: (-len(x), x))
    selected = tokens[:max_terms]
    return " ".join(selected) or normalize_title(title)[:30]


def similarity(a: str, b: str) -> float:
    ta = tokenize(a)
    tb = tokenize(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / max(1, len(ta | tb))


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
        desc = normalize_text(item.get("description", ""))
        if not title or is_roundup_or_low_value_title(title):
            continue

        rows.append({
            "category": category,
            "title": title,
            "description": desc,
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
        title = re.sub(r"\s+-\s+[^-]{1,35}$", "", title).strip()
        desc = normalize_text(getattr(entry, "summary", ""))
        if not title or is_roundup_or_low_value_title(title):
            continue

        rows.append({
            "category": category,
            "title": title,
            "description": desc,
            "url": getattr(entry, "link", ""),
            "published_at": parse_date(getattr(entry, "published", "")),
            "source": "google",
            "query": query,
        })
    return rows


def collect_anchor_headlines(
    *,
    max_anchors: int = 8,
    lookback_hours: int = 48,
) -> list[dict[str, Any]]:
    """
    v1.24 핵심:
    카드뉴스의 기준이 되는 '헤드라인 뉴스 List'를 먼저 생성합니다.
    이후 카드뉴스는 이 anchor 목록에서만 출발합니다.
    """
    now = datetime.now(KST)
    cutoff = now - timedelta(hours=lookback_hours)

    rows: list[dict[str, Any]] = []

    for category, query in HEADLINE_QUERIES:
        rows.extend(fetch_naver_news(category, query, display=20))
        time.sleep(0.12)

    if len(rows) < 25:
        for category, query in HEADLINE_QUERIES:
            rows.extend(fetch_google_news(category, query, limit=12))
            time.sleep(0.08)

    fresh = []
    for row in rows:
        published = row.get("published_at")
        # 날짜가 명확하고 오래된 것은 제외. 날짜가 없는 후보는 fallback으로 허용.
        if published is not None and published < cutoff:
            continue
        fresh.append(row)

    seen = set()
    anchors = []
    cat_count: dict[str, int] = {}

    def score(item: dict[str, Any]):
        published = item.get("published_at")
        ts = published.timestamp() if published else 0
        return (
            0 if item.get("source") == "naver" else 1,
            0 if item.get("description") else 1,
            -ts,
        )

    for item in sorted(fresh, key=score):
        key = title_key(item.get("title", ""))
        if not key or key in seen:
            continue

        cat = item.get("category", "주요")
        if cat_count.get(cat, 0) >= 2 and len(anchors) < max_anchors - 2:
            continue

        seen.add(key)
        anchors.append({
            **item,
            "anchor_rank": len(anchors) + 1,
            "anchor_title": item.get("title", ""),
        })
        cat_count[cat] = cat_count.get(cat, 0) + 1

        if len(anchors) >= max_anchors:
            break

    print("[anchor headlines]")
    for a in anchors:
        published = a.get("published_at").strftime("%Y-%m-%d %H:%M") if a.get("published_at") else "undated"
        print(f"{a['anchor_rank']}. [{a.get('category')}] {a.get('anchor_title')} ({a.get('source')} · {published})")

    return anchors


def find_similar_articles_for_anchor(
    anchor: dict[str, Any],
    *,
    lookback_hours: int = 72,
    max_articles: int = 3,
) -> list[dict[str, Any]]:
    """
    anchor headline을 기준으로 비슷한 기사 3개를 찾습니다.
    기존 v1.23처럼 독립적으로 이슈를 다시 뽑지 않습니다.
    """
    now = datetime.now(KST)
    cutoff = now - timedelta(hours=lookback_hours)

    category = anchor.get("category", "주요")
    anchor_title = anchor.get("anchor_title") or anchor.get("title") or ""
    query = keyword_query_from_title(anchor_title, max_terms=5)

    candidates = []
    # 1차: 제목 핵심어 검색
    candidates.extend(fetch_naver_news(category, query, display=20))
    if len(candidates) < 3:
        candidates.extend(fetch_google_news(category, query, limit=10))

    # 2차: 원 제목 그대로 검색
    if len(candidates) < 3:
        candidates.extend(fetch_naver_news(category, anchor_title[:60], display=10))
        candidates.extend(fetch_google_news(category, anchor_title[:60], limit=8))

    # anchor 원문을 반드시 포함
    candidates.insert(0, anchor)

    seen = set()
    filtered = []
    for item in candidates:
        title = item.get("title", "")
        key = title_key(title)
        if not key or key in seen:
            continue
        seen.add(key)

        published = item.get("published_at")
        if published is not None and published < cutoff:
            continue

        sim = similarity(anchor_title, title + " " + item.get("description", ""))
        # anchor 자체는 무조건 포함, 나머지는 최소 유사도 적용
        if item is not anchor and sim < 0.12:
            continue

        filtered.append({
            **item,
            "similarity": sim if item is not anchor else 1.0,
        })

    filtered.sort(
        key=lambda x: (
            -float(x.get("similarity") or 0),
            0 if x.get("source") == "naver" else 1,
            -(x.get("published_at").timestamp() if x.get("published_at") else 0),
        )
    )

    return filtered[:max_articles]


def build_anchor_groups(
    *,
    max_anchors: int = 8,
    lookback_hours: int = 48,
    similar_lookback_hours: int = 72,
) -> list[dict[str, Any]]:
    anchors = collect_anchor_headlines(max_anchors=max_anchors, lookback_hours=lookback_hours)

    groups = []
    for anchor in anchors:
        articles = find_similar_articles_for_anchor(
            anchor,
            lookback_hours=similar_lookback_hours,
            max_articles=3,
        )
        groups.append({
            "rank": anchor["anchor_rank"],
            "category": anchor.get("category", "주요"),
            "anchor_title": anchor.get("anchor_title") or anchor.get("title"),
            "anchor": anchor,
            "articles": articles,
            "keywords": list(tokenize(anchor.get("anchor_title") or anchor.get("title")))[:5],
        })

    print("[anchor groups]")
    for g in groups:
        print(f"{g['rank']}. {g['anchor_title']} · related_articles={len(g['articles'])}")

    return groups
