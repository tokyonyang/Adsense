import html
import math
import re
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
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


def _parse_entry_datetime(entry) -> datetime | None:
    for attr in ("published_parsed", "updated_parsed"):
        value = getattr(entry, attr, None)
        if value:
            try:
                return datetime(*value[:6], tzinfo=timezone.utc)
            except Exception:
                pass

    raw = getattr(entry, "published", "") or getattr(entry, "updated", "") or ""
    raw = clean_text(raw)
    if not raw:
        return None
    try:
        dt = parsedate_to_datetime(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def _published_display(entry_dt: datetime | None, entry) -> str:
    if entry_dt is not None:
        # 최근 24시간 운영에서 보기 쉽게 월일/시분까지 표시합니다. UTC 기준이므로 KST로 변환합니다.
        kst = entry_dt.astimezone(timezone(timedelta(hours=9)))
        return kst.strftime("%m-%d %H:%M")
    raw = getattr(entry, "published", "") or getattr(entry, "updated", "") or ""
    raw = clean_text(raw)
    return raw[:16] if raw else ""


def _age_hours(entry_dt: datetime | None) -> float | None:
    if entry_dt is None:
        return None
    return max(0.0, (datetime.now(timezone.utc) - entry_dt).total_seconds() / 3600)


def fetch_related_news(
    keyword: str,
    limit: int = 5,
    geo: str = "KR",
    category_hint: str = "",
    lookback_hours: int = 24,
) -> list[dict]:
    """키워드와 관련된 한국어 뉴스 링크를 Google News RSS에서 가져옵니다.

    기본값은 최근 24시간 이내 기사입니다. Google News 검색 연산자 `when:1d`를 사용하고,
    RSS의 published 시간이 파싱되는 경우 로컬에서도 24시간 초과 기사를 걸러냅니다.
    """
    keyword = clean_text(keyword)
    if not keyword:
        return []

    hours = max(1, int(lookback_hours or 24))
    days = max(1, math.ceil(hours / 24))
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    # 너무 넓은 검색을 줄이기 위해 카테고리 힌트를 함께 넣습니다.
    # 예: "기준금리 경제 금융 물가 금리 환율 when:1d"
    hint = clean_text(category_hint)
    search_text = f"{keyword} {hint} when:{days}d" if hint else f"{keyword} when:{days}d"
    query = quote_plus(search_text)
    url = GOOGLE_NEWS_SEARCH_RSS.format(query=query)

    try:
        feed = feedparser.parse(url)
    except Exception as exc:
        print(f"[WARN] Google News RSS fetch failed for {keyword}: {exc}")
        return []

    rows: list[dict] = []
    seen = set()
    for entry in getattr(feed, "entries", [])[: max(limit * 4, limit)]:
        entry_dt = _parse_entry_datetime(entry)
        # published 시간이 확인되는 경우, 최근 lookback_hours 초과 기사는 제외합니다.
        if entry_dt is not None and entry_dt < cutoff:
            continue

        title = clean_text(html.unescape(getattr(entry, "title", "")))
        link = clean_text(getattr(entry, "link", ""))
        source = _source_name(entry)
        published = _published_display(entry_dt, entry)
        age = _age_hours(entry_dt)

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
            "published_at": entry_dt.isoformat() if entry_dt else "",
            "age_hours": round(age, 2) if age is not None else "",
        })
        if len(rows) >= limit:
            break

    return rows
