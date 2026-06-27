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

from app.services.headline_cardnews_render_service import build_cardnews_pages
from app.services.headline_cardnews_summary_service import summarize_clusters_with_gemini
from app.services.headline_cluster_service import cluster_articles
from app.services.telegram_album_service import send_media_group, send_text_message

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
    return re.sub(r"\s+", " ", title).strip(" -·ㆍ|")


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


def parse_date(value: str | None):
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).astimezone(KST)
    except Exception:
        return None


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
        })

    return rows


def collect_articles(*, lookback_hours: int = 48) -> list[dict[str, Any]]:
    now = datetime.now(KST)
    cutoff = now - timedelta(hours=lookback_hours)
    rows: list[dict[str, Any]] = []

    for category, query in HEADLINE_QUERIES:
        rows.extend(fetch_naver_news(category, query, display=30))
        time.sleep(0.15)

    if len(rows) < 30:
        for category, query in HEADLINE_QUERIES:
            rows.extend(fetch_google_news(category, query, limit=12))
            time.sleep(0.1)

    fresh = []
    for row in rows:
        published = row.get("published_at")
        if published is not None and published < cutoff:
            continue
        fresh.append(row)

    print(f"[cardnews articles] collected={len(rows)} fresh={len(fresh)} lookback={lookback_hours}h")
    return fresh


def weekday_ko(dt: datetime) -> str:
    return "월화수목금토일"[dt.weekday()]


def build_link_digest(issues: list[dict[str, Any]]) -> str:
    now = datetime.now(KST)
    lines = [
        f"{now:%Y년 %m월%d일}({weekday_ko(now)})☀️☀️🌤",
        "💛 아침 헤드라인 뉴스 · 원문 링크",
        "",
    ]

    for issue in issues:
        lines.append(f"{issue.get('rank')}. {issue.get('headline')}")
        for idx, link in enumerate(issue.get("links") or [], start=1):
            title = link.get("title") or link.get("domain") or "원문"
            url = link.get("url") or ""
            if url:
                lines.append(f"   {idx}) {title}\n      {url}")
        lines.append("")

    return "\n".join(lines).strip()


def main():
    lookback_hours = int(env("HEADLINE_LOOKBACK_HOURS", "48"))
    max_clusters = int(env("HEADLINE_CARDNEWS_ISSUES", "5"))
    min_cluster_size = int(env("HEADLINE_MIN_CLUSTER_SIZE", "2"))

    articles = collect_articles(lookback_hours=lookback_hours)

    if not articles:
        send_text_message("💛 아침 헤드라인 뉴스\n\n최근 헤드라인 후보가 부족해 카드뉴스를 생성하지 못했습니다.")
        return

    clusters = cluster_articles(
        articles,
        max_clusters=max_clusters,
        min_cluster_size=min_cluster_size,
        similarity_threshold=float(env("HEADLINE_CLUSTER_THRESHOLD", "0.24")),
    )

    if not clusters:
        send_text_message("💛 아침 헤드라인 뉴스\n\n유사 기사 묶음을 만들지 못했습니다.")
        return

    issues = summarize_clusters_with_gemini(clusters)
    out_dir = Path("tmp/headline_cardnews")
    image_paths = build_cardnews_pages(issues, output_dir=out_dir)

    caption = "💛 아침 헤드라인 뉴스\n유사 기사 3건씩 묶어 카드뉴스로 정리했습니다."
    send_media_group(image_paths, caption=caption)

    if env("HEADLINE_SEND_LINK_DIGEST", "true").lower() == "true":
        send_text_message(build_link_digest(issues), disable_web_page_preview=True)

    print("[cardnews result]")
    print(json.dumps({
        "articles": len(articles),
        "clusters": len(clusters),
        "issues": len(issues),
        "pages": len(image_paths),
        "image_paths": image_paths,
        "issues_preview": [
            {
                "rank": x.get("rank"),
                "category": x.get("category"),
                "headline": x.get("headline"),
                "summary_lines": x.get("summary_lines"),
                "links": x.get("links"),
            }
            for x in issues
        ],
    }, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
