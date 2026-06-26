import html
import re
from datetime import datetime
from urllib.parse import quote_plus

import feedparser

from seo_utils import clean_text


GOOGLE_NEWS_SEARCH_RSS = "https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"


def _source_name(entry) -> str:
    source = getattr(entry, "source", None)
    if isinstance(source, dict):
        return clean_text(source.get("title", ""))
    title = getattr(source, "title", "") if source else ""
    return clean_text(title)


def _published(entry) -> str:
    raw = getattr(entry, "published", "") or getattr(entry, "updated", "") or ""
    raw = clean_text(raw)
    if not raw:
        return ""
    # 예: Thu, 25 Jun 2026 01:20:00 GMT -> 2026-06-25 형태로 짧게 표시
    try:
        parsed = datetime.strptime(raw[:25], "%a, %d %b %Y %H:%M:%S")
        return parsed.strftime("%Y-%m-%d")
    except Exception:
        return raw[:16]


def fetch_related_news(keyword: str, limit: int = 5, geo: str = "KR") -> list[dict]:
    """키워드와 관련된 한국어 뉴스 링크를 Google News RSS에서 가져옵니다.

    무료/무키 API 방식이라 네이버 뉴스 API 키 없이도 GitHub Actions에서 동작합니다.
    Google News 링크가 반환될 수 있으나, 텔레그램에서는 기사 제목과 함께 바로 열 수 있습니다.
    """
    keyword = clean_text(keyword)
    if not keyword:
        return []

    # 너무 넓은 검색을 줄이기 위해 한국어 뉴스 쪽으로 힌트를 줍니다.
    query = quote_plus(f'{keyword} when:7d')
    url = GOOGLE_NEWS_SEARCH_RSS.format(query=query)

    try:
        feed = feedparser.parse(url)
    except Exception as exc:
        print(f"[WARN] Google News RSS fetch failed for {keyword}: {exc}")
        return []

    rows: list[dict] = []
    seen = set()
    for entry in getattr(feed, "entries", [])[: max(limit * 3, limit)]:
        title = clean_text(html.unescape(getattr(entry, "title", "")))
        link = clean_text(getattr(entry, "link", ""))
        source = _source_name(entry)
        published = _published(entry)

        # Google News RSS 제목은 "기사 제목 - 매체명" 형태인 경우가 많아 중복 표시를 줄입니다.
        if source and title.endswith(f" - {source}"):
            title = title[: -(len(source) + 3)].strip()

        dedupe_key = re.sub(r"\s+", " ", title.lower())
        if not title or not link or dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        rows.append({
            "title": title,
            "url": link,
            "source": source,
            "published": published,
        })
        if len(rows) >= limit:
            break

    return rows
