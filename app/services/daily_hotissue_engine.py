from __future__ import annotations

import html
import json
import os
import re
import time
from collections import Counter
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus, urlparse

import requests

try:
    import feedparser
except Exception:
    feedparser = None


KST = timezone(timedelta(hours=9))

NAVER_NEWS_URL = "https://openapi.naver.com/v1/search/news.json"
GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
GOOGLE_TRENDS_RSS = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=KR"

TELEGRAM_API_BASE = "https://api.telegram.org/bot"

DEFAULT_TOP_N = 10


# ============================================================
# 환경변수
# ============================================================

def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def env_int(name: str, default: int) -> int:
    try:
        return int(env(name, str(default)))
    except Exception:
        return default


def env_float(name: str, default: float) -> float:
    try:
        return float(env(name, str(default)))
    except Exception:
        return default


def parse_csv(value: str, fallback: list[str]) -> list[str]:
    if not value:
        return fallback[:]
    parsed = [x.strip() for x in value.split(",") if x.strip()]
    return parsed or fallback[:]


# ============================================================
# 카테고리 정책
# ============================================================

DEFAULT_PRIORITY_CATEGORIES = [
    "경제·금융",
    "증권·투자",
    "산업·기업",
    "정책·지원금",
    "부동산·주거금융",
    "생활·제도",
    "국제",
]

DEFAULT_SECONDARY_CATEGORIES = [
    "시사·정치",
    "사회·사건",
    "날씨·안전",
    "건강·의료",
    "교육·입시",
]

DEFAULT_LOW_PRIORITY_CATEGORIES = [
    "연예·문화",
    "스포츠",
    "기타",
]


def category_policy_from_env() -> dict[str, Any]:
    return {
        "mode": env("HOT_ISSUE_CATEGORY_MODE", "finance_first").lower(),
        "priority_categories": parse_csv(
            env("HOT_ISSUE_PRIORITY_CATEGORIES"),
            DEFAULT_PRIORITY_CATEGORIES,
        ),
        "secondary_categories": parse_csv(
            env("HOT_ISSUE_SECONDARY_CATEGORIES"),
            DEFAULT_SECONDARY_CATEGORIES,
        ),
        "low_priority_categories": parse_csv(
            env("HOT_ISSUE_LOW_PRIORITY_CATEGORIES"),
            DEFAULT_LOW_PRIORITY_CATEGORIES,
        ),
        "top_n": env_int("HOT_ISSUE_TOP_N", DEFAULT_TOP_N),
        "priority_min": env_int("HOT_ISSUE_PRIORITY_MIN", 6),
        "priority_max": env_int("HOT_ISSUE_PRIORITY_MAX", 8),
        "secondary_max": env_int("HOT_ISSUE_SECONDARY_MAX", 3),
        "low_priority_max": env_int("HOT_ISSUE_LOW_PRIORITY_MAX", 2),
        "other_max": env_int("HOT_ISSUE_OTHER_MAX", 1),
        "per_category_max": env_int("HOT_ISSUE_PER_CATEGORY_MAX", 2),
        "priority_per_category_max": env_int("HOT_ISSUE_PRIORITY_PER_CATEGORY_MAX", 3),
    }


def item_category(item: dict[str, Any]) -> str:
    return str(item.get("category") or "기타").strip() or "기타"


def item_score(item: dict[str, Any]) -> float:
    try:
        return float(item.get("score") or 0)
    except Exception:
        return 0.0


def sort_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(items, key=lambda x: item_score(x), reverse=True)


def select_all_score(items: list[dict[str, Any]], policy: dict[str, Any]) -> list[dict[str, Any]]:
    return sort_items(items)[: policy["top_n"]]


def select_balanced_items(items: list[dict[str, Any]], policy: dict[str, Any]) -> list[dict[str, Any]]:
    top_n = policy["top_n"]
    per_category_max = policy["per_category_max"]
    other_max = policy["other_max"]

    selected = []
    used_ids = set()
    category_count: dict[str, int] = {}

    for item in sort_items(items):
        if len(selected) >= top_n:
            break

        category = item_category(item)
        if id(item) in used_ids:
            continue
        if category == "기타" and category_count.get("기타", 0) >= other_max:
            continue
        if category_count.get(category, 0) >= per_category_max:
            continue

        selected.append(item)
        used_ids.add(id(item))
        category_count[category] = category_count.get(category, 0) + 1

    if len(selected) < top_n:
        for item in sort_items(items):
            if len(selected) >= top_n:
                break
            if id(item) in used_ids:
                continue
            selected.append(item)
            used_ids.add(id(item))

    return selected[:top_n]


def select_finance_first_items(items: list[dict[str, Any]], policy: dict[str, Any]) -> list[dict[str, Any]]:
    top_n = policy["top_n"]
    priority_min = min(policy["priority_min"], top_n)
    priority_max = min(policy["priority_max"], top_n)
    secondary_max = policy["secondary_max"]
    low_priority_max = policy["low_priority_max"]
    other_max = policy["other_max"]
    priority_per_category_max = policy["priority_per_category_max"]
    per_category_max = policy["per_category_max"]

    priority_set = set(policy["priority_categories"])
    secondary_set = set(policy["secondary_categories"])
    low_set = set(policy["low_priority_categories"])

    selected = []
    used_ids = set()
    category_count: dict[str, int] = {}
    group_count = {"priority": 0, "secondary": 0, "low": 0}

    def can_add(item: dict[str, Any], stage: str) -> bool:
        category = item_category(item)

        if id(item) in used_ids:
            return False

        if category == "기타" and category_count.get("기타", 0) >= other_max:
            return False

        max_for_cat = priority_per_category_max if category in priority_set else per_category_max
        if category_count.get(category, 0) >= max_for_cat:
            return False

        if stage == "priority":
            return category in priority_set and group_count["priority"] < priority_max

        if stage == "secondary":
            return category in secondary_set and group_count["secondary"] < secondary_max

        if stage == "low":
            return category in low_set and group_count["low"] < low_priority_max

        return True

    def add(item: dict[str, Any]):
        category = item_category(item)
        selected.append(item)
        used_ids.add(id(item))
        category_count[category] = category_count.get(category, 0) + 1

        if category in priority_set:
            group_count["priority"] += 1
        elif category in secondary_set:
            group_count["secondary"] += 1
        else:
            group_count["low"] += 1

    sorted_all = sort_items(items)

    # 1) 경제/금융 우선 카테고리 최소 확보
    for item in sorted_all:
        if len(selected) >= top_n or group_count["priority"] >= priority_min:
            break
        if can_add(item, "priority"):
            add(item)

    # 2) 경제/금융 우선 카테고리 추가 확보
    for item in sorted_all:
        if len(selected) >= top_n or group_count["priority"] >= priority_max:
            break
        if can_add(item, "priority"):
            add(item)

    # 3) 보조 카테고리 보충
    for item in sorted_all:
        if len(selected) >= top_n:
            break
        if can_add(item, "secondary"):
            add(item)

    # 4) 저우선 카테고리 제한 보충
    for item in sorted_all:
        if len(selected) >= top_n:
            break
        if can_add(item, "low"):
            add(item)

    # 5) 그래도 부족하면 전체 점수순 보충
    for item in sorted_all:
        if len(selected) >= top_n:
            break
        if can_add(item, "any"):
            add(item)

    return selected[:top_n]


def apply_hotissue_category_policy(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    policy = category_policy_from_env()
    mode = policy["mode"]

    if mode == "all_score":
        return select_all_score(items, policy)

    if mode == "balanced":
        return select_balanced_items(items, policy)

    return select_finance_first_items(items, policy)


def category_mix_text(items: list[dict[str, Any]]) -> str:
    counts: dict[str, int] = {}
    for item in items:
        category = item_category(item)
        counts[category] = counts.get(category, 0) + 1

    return " / ".join(
        f"{category} {count}개"
        for category, count in sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    )


def policy_debug_text() -> str:
    p = category_policy_from_env()
    return (
        f"모드={p['mode']} · "
        f"우선={','.join(p['priority_categories'])} · "
        f"우선최소={p['priority_min']} · "
        f"저우선최대={p['low_priority_max']} · "
        f"기타최대={p['other_max']}"
    )


# ============================================================
# 텍스트 정리
# ============================================================

def clean_html(text: str) -> str:
    text = html.unescape(text or "")
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_keyword(text: str) -> str:
    text = clean_html(text)
    text = re.sub(r"[\[\]\(\)\{\}]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" -·ㆍ|")


def short_text(text: str, limit: int = 80) -> str:
    text = clean_html(text)
    text = text.replace("...", "…").replace("⋯", "…")
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def domain_of(url: str | None) -> str:
    if not url:
        return "news"
    try:
        host = urlparse(url).netloc or urlparse(url).path
        return host.replace("www.", "")[:40] or "news"
    except Exception:
        return "news"


def parse_date(value: str | None):
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).astimezone(KST)
    except Exception:
        return None


def fmt_date(dt: Any) -> str:
    if isinstance(dt, datetime):
        return dt.strftime("%m-%d %H:%M")
    return "시간불명"


# ============================================================
# 카테고리 분류
# ============================================================

CATEGORY_RULES: list[tuple[str, list[str]]] = [
    ("경제·금융", [
        "환율", "달러", "원화", "엔화", "금리", "기준금리", "대출", "예금", "은행",
        "금융", "물가", "인플레이션", "소비자물가", "유가", "국제유가", "전기요금",
        "가스요금", "공공요금", "세금", "관세", "수출", "수입", "무역수지",
    ]),
    ("증권·투자", [
        "코스피", "코스닥", "나스닥", "다우", "s&p", "주가", "증시", "상장",
        "하락", "상승", "급등", "급락", "시가총액", "반도체주", "외국인", "기관",
        "투자", "ETF", "채권", "비트코인", "가상자산", "암호화폐",
    ]),
    ("산업·기업", [
        "삼성전자", "sk하이닉스", "하이닉스", "엔비디아", "테슬라", "현대차", "기아",
        "LG", "네이버", "카카오", "비야디", "BYD", "반도체", "HBM", "AI", "인공지능",
        "배터리", "전기차", "조선", "자동차", "공장", "기업", "산업", "수주", "실적",
    ]),
    ("정책·지원금", [
        "정부", "지원금", "보조금", "소상공인", "민생", "대책", "정책", "국회",
        "예산", "추경", "복지", "지원", "제도", "개편", "규제", "감세", "청년",
    ]),
    ("부동산·주거금융", [
        "부동산", "아파트", "전세", "월세", "분양", "청약", "주택", "집값",
        "매매", "임대차", "대출규제", "DSR", "LTV", "재건축", "재개발",
    ]),
    ("생활·제도", [
        "생활", "요금", "할인", "소비자", "교통", "보험", "연금", "국민연금",
        "전기", "가스", "택배", "통신비", "통신", "휴대폰", "마트", "장바구니",
    ]),
    ("시사·정치", [
        "대통령", "총리", "청문회", "장관", "선관위", "국정", "여당", "야당",
        "국민의힘", "민주당", "선거", "정치", "의혹", "특검", "탄핵", "신상진",
    ]),
    ("사회·사건", [
        "경찰", "검찰", "법원", "구속", "수사", "재판", "사건", "사고", "범죄",
        "압수수색", "체포", "시위", "논란", "교사", "학교폭력", "아동학대",
    ]),
    ("날씨·안전", [
        "날씨", "폭염", "호우", "태풍", "지진", "화산", "후지산", "분화", "안전",
        "재난", "오존", "미세먼지", "기상청",
    ]),
    ("건강·의료", [
        "건강", "의료", "병원", "의사", "간호사", "약", "감염", "백신", "암",
        "혈액암", "다이어트", "비만", "수술", "질병",
    ]),
    ("교육·입시", [
        "교육", "입시", "수능", "대학", "학교", "교권", "교사", "학생", "학부모",
        "학원", "내신", "의대", "초등", "중등", "고등",
    ]),
    ("국제", [
        "미국", "중국", "일본", "러시아", "이스라엘", "이란", "중동", "호르무즈",
        "트럼프", "바이든", "관세", "전쟁", "외교", "G7", "EU", "캐나다",
    ]),
    ("스포츠", [
        "야구", "축구", "농구", "배구", "KBO", "MLB", "월드컵", "올림픽", "선수",
        "LG", "롯데", "두산", "KIA", "키움", "NC", "오스틴", "이승우", "류승민",
        "여서정", "금메달", "도마",
    ]),
    ("연예·문화", [
        "배우", "가수", "드라마", "영화", "예능", "방송", "연예", "아이돌", "종영",
        "신하균", "오정세", "박영진", "유재석", "허경환", "오십프로", "아형", "놀뭐",
    ]),
    ("기타", []),
]


def classify_category(keyword: str, articles: list[dict[str, Any]] | None = None) -> str:
    text_parts = [keyword]
    for article in (articles or [])[:5]:
        text_parts.append(article.get("title", ""))
        text_parts.append(article.get("description", ""))

    text = " ".join(text_parts).lower()

    scores: dict[str, int] = {}
    for category, words in CATEGORY_RULES:
        score = 0
        for word in words:
            if word.lower() in text:
                score += 1
        if score:
            scores[category] = score

    if not scores:
        return "기타"

    # 경제/금융 관련 키워드는 동점일 때 우선
    priority_order = [
        "경제·금융", "증권·투자", "산업·기업", "정책·지원금", "부동산·주거금융",
        "생활·제도", "국제", "시사·정치", "사회·사건", "날씨·안전", "건강·의료",
        "교육·입시", "스포츠", "연예·문화", "기타",
    ]

    return sorted(
        scores.items(),
        key=lambda x: (-x[1], priority_order.index(x[0]) if x[0] in priority_order else 999),
    )[0][0]


# ============================================================
# 뉴스 수집
# ============================================================

FINANCE_PRIORITY_SEEDS = [
    "환율",
    "코스피",
    "코스닥",
    "금리",
    "물가",
    "유가",
    "전기요금",
    "가스요금",
    "부동산",
    "전세",
    "삼성전자",
    "SK하이닉스",
    "반도체",
    "엔비디아",
    "테슬라",
    "전기차",
    "정부 지원금",
    "소상공인 지원",
    "민생 대책",
    "국민연금",
    "주택담보대출",
]

BALANCED_SEEDS = [
    "정치",
    "사회",
    "날씨",
    "건강",
    "교육",
    "국제",
    "스포츠",
    "연예",
]


def fetch_google_trends_keywords(limit: int = 30) -> list[str]:
    if feedparser is None:
        return []

    try:
        feed = feedparser.parse(GOOGLE_TRENDS_RSS)
    except Exception as exc:
        print("[trends] failed:", exc)
        return []

    keywords = []
    for entry in feed.entries[:limit]:
        title = normalize_keyword(getattr(entry, "title", ""))
        if title and title not in keywords:
            keywords.append(title)

    return keywords


def fetch_naver_news(query: str, display: int = 10) -> list[dict[str, Any]]:
    client_id = env("NAVER_CLIENT_ID")
    client_secret = env("NAVER_CLIENT_SECRET")

    if not client_id or not client_secret:
        return []

    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
    }
    params = {
        "query": query,
        "display": display,
        "start": 1,
        "sort": "date",
    }

    try:
        response = requests.get(NAVER_NEWS_URL, headers=headers, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        print(f"[naver] failed query={query}: {exc}")
        return []

    rows = []
    for item in data.get("items", []):
        title = short_text(clean_html(item.get("title", "")), 120)
        description = short_text(clean_html(item.get("description", "")), 160)
        url = item.get("originallink") or item.get("link") or ""
        published_at = parse_date(item.get("pubDate"))

        if not title:
            continue

        rows.append({
            "title": title,
            "description": description,
            "url": url,
            "domain": domain_of(url),
            "published_at": published_at,
            "source": "naver",
        })

    return rows


def fetch_google_news(query: str, limit: int = 10) -> list[dict[str, Any]]:
    if feedparser is None:
        return []

    rss = GOOGLE_NEWS_RSS.format(query=quote_plus(query))

    try:
        feed = feedparser.parse(rss)
    except Exception as exc:
        print(f"[google-news] failed query={query}: {exc}")
        return []

    rows = []
    for entry in feed.entries[:limit]:
        title = short_text(clean_html(getattr(entry, "title", "")), 120)
        # Google News RSS 제목 뒤의 언론사 제거
        title = re.sub(r"\s+-\s+[^-]{1,35}$", "", title).strip()
        description = short_text(clean_html(getattr(entry, "summary", "")), 160)
        url = getattr(entry, "link", "") or ""
        published_at = parse_date(getattr(entry, "published", ""))

        if not title:
            continue

        rows.append({
            "title": title,
            "description": description,
            "url": url,
            "domain": domain_of(url),
            "published_at": published_at,
            "source": "google",
        })

    return rows


def fetch_news_for_keyword(keyword: str, max_articles: int = 5) -> list[dict[str, Any]]:
    rows = []
    rows.extend(fetch_naver_news(keyword, display=max_articles))
    if len(rows) < max_articles:
        rows.extend(fetch_google_news(keyword, limit=max_articles))

    # 중복 제거
    seen = set()
    unique = []
    for row in rows:
        key = (row.get("title") or "").lower()
        key = re.sub(r"[^0-9a-zA-Z가-힣]", "", key)[:100]
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append(row)

    unique.sort(
        key=lambda x: (
            0 if x.get("source") == "naver" else 1,
            -(x.get("published_at").timestamp() if isinstance(x.get("published_at"), datetime) else 0),
        )
    )

    return unique[:max_articles]


# ============================================================
# 후보 생성/스코어링
# ============================================================

def collect_candidate_keywords() -> list[dict[str, Any]]:
    mode = category_policy_from_env()["mode"]

    candidates: list[dict[str, Any]] = []

    # 1) 경제/금융 우선 seed
    if mode == "finance_first":
        for seed in FINANCE_PRIORITY_SEEDS:
            candidates.append({
                "keyword": seed,
                "source": "finance_seed",
                "seed_priority": 1.0,
            })

    # 2) Google Trends
    trend_limit = env_int("HOT_ISSUE_TREND_LIMIT", 35)
    for kw in fetch_google_trends_keywords(limit=trend_limit):
        candidates.append({
            "keyword": kw,
            "source": "google_trends",
            "seed_priority": 0.0,
        })

    # 3) 균형 seed 보조
    for seed in BALANCED_SEEDS:
        candidates.append({
            "keyword": seed,
            "source": "balanced_seed",
            "seed_priority": 0.2,
        })

    # 중복 제거
    seen = set()
    unique = []
    for item in candidates:
        kw = normalize_keyword(item["keyword"])
        key = kw.lower().replace(" ", "")
        if not kw or key in seen:
            continue
        seen.add(key)
        item["keyword"] = kw
        unique.append(item)

    return unique


def article_recency_score(article: dict[str, Any]) -> float:
    published = article.get("published_at")
    if not isinstance(published, datetime):
        return 0.0

    now = datetime.now(KST)
    hours = max(0.0, (now - published).total_seconds() / 3600)
    if hours <= 6:
        return 18
    if hours <= 12:
        return 14
    if hours <= 24:
        return 10
    if hours <= 48:
        return 6
    return 2


def score_candidate(keyword: str, source: str, seed_priority: float, articles: list[dict[str, Any]]) -> dict[str, Any]:
    category = classify_category(keyword, articles)
    policy = category_policy_from_env()

    news_count = len(articles)
    recency = sum(article_recency_score(a) for a in articles[:5])
    source_bonus = 18 if source == "google_trends" else 0
    seed_bonus = 35 * float(seed_priority or 0)

    category_bonus = 0
    if category in policy["priority_categories"]:
        category_bonus = 55 if policy["mode"] == "finance_first" else 18
    elif category in policy["secondary_categories"]:
        category_bonus = 14
    elif category in policy["low_priority_categories"]:
        category_bonus = -10 if policy["mode"] == "finance_first" else 0

    # 뉴스 근거가 거의 없는 후보는 감점
    evidence_penalty = -35 if news_count == 0 else 0

    score = news_count * 16 + recency + source_bonus + seed_bonus + category_bonus + evidence_penalty

    return {
        "keyword": keyword,
        "category": category,
        "score": round(score, 2),
        "source": source,
        "articles": articles,
        "article_count": news_count,
    }


def build_scored_items() -> list[dict[str, Any]]:
    max_articles = env_int("HOT_ISSUE_NEWS_PER_KEYWORD", 5)
    candidates = collect_candidate_keywords()

    print(f"[candidates] {len(candidates)}")

    scored = []
    for idx, candidate in enumerate(candidates, start=1):
        keyword = candidate["keyword"]
        articles = fetch_news_for_keyword(keyword, max_articles=max_articles)

        item = score_candidate(
            keyword=keyword,
            source=candidate.get("source", ""),
            seed_priority=float(candidate.get("seed_priority") or 0),
            articles=articles,
        )

        if item["article_count"] > 0:
            scored.append(item)

        print(
            f"[{idx}/{len(candidates)}] {keyword} "
            f"category={item['category']} score={item['score']} articles={item['article_count']}"
        )

        time.sleep(env_float("HOT_ISSUE_REQUEST_SLEEP", 0.12))

    return sort_items(scored)


# ============================================================
# 리포트 생성
# ============================================================

def weekday_ko(dt: datetime) -> str:
    return "월화수목금토일"[dt.weekday()]


def build_telegram_report(items: list[dict[str, Any]]) -> str:
    lines = []
    lines.append("🔥 오늘의 핫이슈 TOP 10")
    lines.append("")
    lines.append("📊 카테고리 정책")
    lines.append(policy_debug_text())
    lines.append(f"카테고리 구성: {category_mix_text(items)}")
    lines.append("")

    for idx, item in enumerate(items, start=1):
        lines.append(f"{idx}. [{item['category']}] {item['keyword']}")
        lines.append("근거자료:")

        for article_idx, article in enumerate(item.get("articles", [])[:5], start=1):
            title = short_text(article.get("title", ""), 76)
            url = article.get("url", "")
            domain = article.get("domain") or domain_of(url)
            date = fmt_date(article.get("published_at"))
            lines.append(f"  {article_idx}) {title} ({url}) ({domain} · {date})")

        if not item.get("articles"):
            lines.append("  - 근거자료 부족")

        lines.append("")

    card_items = items[:3]
    lines.append("🃏 오늘의 카드뉴스 추천")
    lines.append("")
    for idx, item in enumerate(card_items, start=1):
        lines.append(f"{idx}. #{idx} {item['keyword']}")
        lines.append("구성방향: 핵심 원인 → 영향받는 사람 → 확인할 자료 → 대응 체크리스트 카드 구성")
        lines.append("")

    lines.append("✍️ 오늘의 작성글 추천")
    lines.append("")
    for idx, item in enumerate(card_items, start=1):
        lines.append(f"{idx}. #{idx} {item['keyword']}")
        lines.append(f"글방향: {item['keyword']} 핵심 배경과 독자가 확인할 체크포인트를 정리하는 글")
        lines.append("")

    lines.append("📌 확인 메모")
    lines.append("각 근거자료는 원문 확인용입니다.")
    lines.append("금융·정책 이슈는 발행 전 공식 자료를 한 번 더 확인하세요.")

    return "\n".join(lines).strip()


# ============================================================
# 텔레그램/저장
# ============================================================

def send_telegram_message(text: str) -> None:
    token = env("TELEGRAM_BOT_TOKEN")
    chat_id = env("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("[telegram] TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID가 없어 전송 생략")
        return

    url = f"{TELEGRAM_API_BASE}{token}/sendMessage"

    chunks = []
    current = ""
    for block in text.split("\n\n"):
        candidate = f"{current}\n\n{block}".strip() if current else block
        if len(candidate) > 3900:
            if current:
                chunks.append(current)
            current = block
        else:
            current = candidate

    if current:
        chunks.append(current)

    for i, chunk in enumerate(chunks, start=1):
        response = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": chunk,
                "disable_web_page_preview": True,
            },
            timeout=30,
        )
        try:
            data = response.json()
        except Exception:
            data = {"ok": False, "description": response.text}

        if not response.ok or not data.get("ok"):
            raise RuntimeError(f"Telegram 전송 실패 part={i}: {data}")

        print(f"[telegram] sent part {i}/{len(chunks)}")


def json_safe(obj: Any):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)


def save_reports(items: list[dict[str, Any]], report_text: str) -> None:
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    now = datetime.now(KST)
    ymd = now.strftime("%Y%m%d")

    payload = {
        "generated_at": now.isoformat(),
        "category_policy": category_policy_from_env(),
        "category_mix": category_mix_text(items),
        "items": items,
    }

    paths = [
        reports_dir / f"daily_hotissue_items_{ymd}.json",
        reports_dir / f"idea_items_{ymd}.json",
        reports_dir / "latest_hotissue_items.json",
        reports_dir / "latest_daily_hotissue.json",
    ]

    for path in paths:
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, default=json_safe),
            encoding="utf-8",
        )

    (reports_dir / f"daily_hotissue_report_{ymd}.txt").write_text(report_text, encoding="utf-8")
    (reports_dir / "latest_daily_hotissue_report.txt").write_text(report_text, encoding="utf-8")

    print("[reports] saved")
    for path in paths:
        print(f"- {path}")


# ============================================================
# 실행
# ============================================================

def main() -> None:
    print("[Daily AdSense SEO Hot Issue Report]")
    print("KST now:", datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S"))
    print("Policy:", policy_debug_text())

    scored_items = build_scored_items()
    if not scored_items:
        message = "🔥 오늘의 핫이슈 TOP 10\n\n수집된 이슈 후보가 없습니다."
        send_telegram_message(message)
        return

    top_items = apply_hotissue_category_policy(scored_items)

    print("[selected category mix]", category_mix_text(top_items))
    for idx, item in enumerate(top_items, start=1):
        print(f"{idx}. [{item['category']}] {item['keyword']} score={item['score']}")

    report_text = build_telegram_report(top_items)
    save_reports(top_items, report_text)
    send_telegram_message(report_text)


# ============================================================
# 외부 호출용 Payload Builder
# ============================================================

def build_daily_hotissue_payload(*, send_report: bool = False, save_report: bool = False) -> dict[str, Any]:
    """Daily와 Morning이 함께 쓰는 단일 마스터 HOT Issue payload를 생성합니다.

    - Daily workflow: main()이 이 함수를 이용해 텔레그램 전송/저장까지 수행합니다.
    - Morning workflow: 이 함수를 호출해 같은 로직으로 TOP Item을 얻고 카드뉴스를 만듭니다.

    반환 구조는 기존 Morning cardnews 변환기가 이해할 수 있도록 hot_items/items 키를 제공합니다.
    """
    scored_items = build_scored_items()
    top_items = apply_hotissue_category_policy(scored_items) if scored_items else []
    report_text = build_telegram_report(top_items) if top_items else "🔥 오늘의 핫이슈 TOP 10\n\n수집된 이슈 후보가 없습니다."

    if save_report and top_items:
        save_reports(top_items, report_text)

    if send_report:
        send_telegram_message(report_text)

    return {
        "items": scored_items,
        "hot_items": top_items,
        "card_items": top_items[:3],
        "article_items": top_items[:3],
        "report_text": report_text,
        "category_policy": category_policy_from_env(),
        "category_mix": category_mix_text(top_items),
        "effective_lookback_hours": env_int("LOOKBACK_HOURS", env_int("HOT_ISSUE_LOOKBACK_HOURS", 48)),
        "hot_issue_count": len(top_items),
    }


if __name__ == "__main__":
    main()
