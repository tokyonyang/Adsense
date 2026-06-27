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


def env_bool(name: str, default: bool = False) -> bool:
    value = env(name, "true" if default else "false").lower()
    return value in {"1", "true", "yes", "y", "on"}


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


def short_text(text: str, limit: int = 84) -> str:
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


def compact_key(text: str) -> str:
    text = normalize_keyword(text).lower()
    return re.sub(r"[^0-9a-zA-Z가-힣]", "", text)[:80]


def tokenize(text: str) -> set[str]:
    text = normalize_keyword(text).lower()
    stop = {
        "오늘", "뉴스", "속보", "종합", "단독", "기자", "관련", "주요", "오전", "오후",
        "있는", "없는", "한다", "했다", "위해", "대한", "이번", "최근", "연합뉴스",
        "네이트", "기준", "통해", "위한", "발표", "확인", "논란",
    }
    tokens = []
    for token in re.findall(r"[가-힣A-Za-z0-9]{2,}", text):
        if token in stop:
            continue
        if len(token) > 16:
            continue
        tokens.append(token)
    return set(tokens)


def text_similarity(a: str, b: str) -> float:
    ta, tb = tokenize(a), tokenize(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / max(1, len(ta | tb))


# ============================================================
# 카테고리 / 슬롯
# ============================================================

CATEGORY_RULES: list[tuple[str, list[str]]] = [
    ("경제·금융", [
        "환율", "달러", "원화", "엔화", "금리", "기준금리", "대출", "예금", "은행",
        "금융", "물가", "인플레이션", "소비자물가", "유가", "국제유가", "전기요금",
        "가스요금", "공공요금", "세금", "관세", "수출", "수입", "무역수지", "원달러",
    ]),
    ("증권·투자", [
        "코스피", "코스닥", "나스닥", "다우", "s&p", "주가", "증시", "상장",
        "하락", "상승", "급등", "급락", "시가총액", "반도체주", "외국인", "기관",
        "투자", "ETF", "채권", "비트코인", "가상자산", "암호화폐", "차익실현",
    ]),
    ("산업·기업", [
        "삼성전자", "sk하이닉스", "하이닉스", "엔비디아", "테슬라", "현대차", "기아",
        "LG", "네이버", "카카오", "비야디", "BYD", "반도체", "HBM", "AI", "인공지능",
        "배터리", "전기차", "조선", "자동차", "공장", "기업", "산업", "수주", "실적",
        "앤트로픽", "오픈AI", "구글", "마이크로소프트",
    ]),
    ("정책·지원금", [
        "정부", "지원금", "보조금", "소상공인", "민생", "대책", "정책", "국회",
        "예산", "추경", "복지", "지원", "제도", "개편", "규제", "감세", "청년",
        "총리", "청문회", "공공요금", "할인", "농축수산",
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
        "지지율",
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
        "여서정", "금메달", "도마", "만루포",
    ]),
    ("연예·문화", [
        "배우", "가수", "드라마", "영화", "예능", "방송", "연예", "아이돌", "종영",
        "신하균", "오정세", "박영진", "유재석", "허경환", "오십프로", "아형", "놀뭐",
        "열애설", "결별", "송혜교", "대성",
    ]),
    ("기타", []),
]

CATEGORY_PRIORITY_ORDER = [
    "경제·금융",
    "증권·투자",
    "산업·기업",
    "정책·지원금",
    "부동산·주거금융",
    "생활·제도",
    "국제",
    "날씨·안전",
    "시사·정치",
    "사회·사건",
    "건강·의료",
    "교육·입시",
    "스포츠",
    "연예·문화",
    "기타",
]

SLOT_DEFINITIONS = {
    "경제·금융": ["경제·금융", "부동산·주거금융", "생활·제도"],
    "증권·투자": ["증권·투자"],
    "산업·기업": ["산업·기업"],
    "정책·생활": ["정책·지원금", "생활·제도", "부동산·주거금융"],
    "국제·안전": ["국제", "날씨·안전"],
    "사회·시사": ["시사·정치", "사회·사건", "건강·의료", "교육·입시"],
    "대중관심": ["연예·문화", "스포츠", "기타"],
}

DEFAULT_SLOT_PLAN = [
    ("경제·금융", 2),
    ("증권·투자", 2),
    ("산업·기업", 2),
    ("정책·생활", 1),
    ("국제·안전", 1),
    ("사회·시사", 1),
    ("대중관심", 1),
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

    return sorted(
        scores.items(),
        key=lambda x: (-x[1], CATEGORY_PRIORITY_ORDER.index(x[0]) if x[0] in CATEGORY_PRIORITY_ORDER else 999),
    )[0][0]


def parse_slot_plan(value: str) -> list[tuple[str, int]]:
    if not value:
        return DEFAULT_SLOT_PLAN[:]

    slots: list[tuple[str, int]] = []
    for part in value.split(","):
        if not part.strip():
            continue
        if ":" not in part:
            continue
        name, count = part.split(":", 1)
        try:
            n = int(count.strip())
        except Exception:
            continue
        name = name.strip()
        if name and n > 0:
            slots.append((name, n))

    return slots or DEFAULT_SLOT_PLAN[:]


def slot_plan_from_env() -> list[tuple[str, int]]:
    return parse_slot_plan(env("HOT_ISSUE_SLOT_PLAN", ""))


def item_slot(item: dict[str, Any]) -> str:
    category = item.get("category") or "기타"
    for slot, categories in SLOT_DEFINITIONS.items():
        if category in categories:
            return slot
    return "대중관심"


def category_mix_text(items: list[dict[str, Any]]) -> str:
    counts: dict[str, int] = {}
    for item in items:
        category = item.get("category") or "기타"
        counts[category] = counts.get(category, 0) + 1

    return " / ".join(
        f"{category} {count}개"
        for category, count in sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    )


def slot_mix_text(items: list[dict[str, Any]]) -> str:
    counts: dict[str, int] = {}
    for item in items:
        slot = item.get("slot") or item_slot(item)
        counts[slot] = counts.get(slot, 0) + 1

    return " / ".join(
        f"{slot} {count}개"
        for slot, count in sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    )


def editorial_policy_text() -> str:
    slot_plan = ", ".join(f"{slot}:{count}" for slot, count in slot_plan_from_env())
    return (
        f"모드={env('HOT_ISSUE_EDITORIAL_MODE', 'slot_editorial')} · "
        f"슬롯={slot_plan} · "
        f"노이즈제한={env_int('HOT_ISSUE_NOISE_MAX', 1)} · "
        f"Morning최소점수={env_float('HEADLINE_CARDNEWS_MIN_EDITORIAL_SCORE', 40.0)}"
    )


# ============================================================
# 뉴스 수집
# ============================================================

FINANCE_PRIORITY_SEEDS = [
    "환율",
    "원달러 환율",
    "코스피",
    "코스닥",
    "금리",
    "기준금리",
    "물가",
    "소비자물가",
    "유가",
    "전기요금",
    "가스요금",
    "공공요금",
    "부동산",
    "전세",
    "분양",
    "삼성전자",
    "SK하이닉스",
    "반도체",
    "HBM",
    "엔비디아",
    "테슬라",
    "전기차",
    "비야디",
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

NOISE_KEYWORDS = [
    "로또",
    "당첨번호",
    "1등",
    "포토",
    "포토뉴스",
    "오늘의 운세",
    "별자리",
    "열애설",
    "결별",
    "인스타",
    "셀카",
    "몸매",
    "키스",
    "종영",
    "만루포",
    "경기 결과",
]

ADSENSE_VALUE_KEYWORDS = [
    "환율",
    "금리",
    "물가",
    "대출",
    "전세",
    "월세",
    "부동산",
    "전기요금",
    "가스요금",
    "공공요금",
    "지원금",
    "소상공인",
    "청년",
    "정부",
    "정책",
    "세금",
    "보험",
    "연금",
    "건강",
    "의료",
    "입시",
    "교육",
    "주식",
    "코스피",
    "코스닥",
    "반도체",
    "전기차",
    "AI",
    "관세",
    "유가",
]

EDITORIAL_IMPORTANCE_KEYWORDS = [
    "정부",
    "대책",
    "동결",
    "인상",
    "하락",
    "상승",
    "급등",
    "급락",
    "위기",
    "규제",
    "개편",
    "청문회",
    "지진",
    "전쟁",
    "관세",
    "수출",
    "실적",
    "공급망",
    "부담",
    "영향",
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
        title = short_text(clean_html(item.get("title", "")), 130)
        description = short_text(clean_html(item.get("description", "")), 180)
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
        title = short_text(clean_html(getattr(entry, "title", "")), 130)
        title = re.sub(r"\s+-\s+[^-]{1,35}$", "", title).strip()
        description = short_text(clean_html(getattr(entry, "summary", "")), 180)
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


def filter_recent_articles(articles: list[dict[str, Any]], lookback_hours: int) -> list[dict[str, Any]]:
    cutoff = datetime.now(KST) - timedelta(hours=lookback_hours)
    filtered = []
    for article in articles:
        published = article.get("published_at")
        if isinstance(published, datetime) and published < cutoff:
            continue
        filtered.append(article)
    return filtered


def fetch_news_for_keyword(keyword: str, max_articles: int = 5) -> list[dict[str, Any]]:
    rows = []
    rows.extend(fetch_naver_news(keyword, display=max_articles))
    if len(rows) < max_articles:
        rows.extend(fetch_google_news(keyword, limit=max_articles))

    seen = set()
    unique = []
    for row in rows:
        key = compact_key(row.get("title", ""))
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append(row)

    lookback_hours = env_int("HOT_ISSUE_LOOKBACK_HOURS", 48)
    unique = filter_recent_articles(unique, lookback_hours)

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
    candidates: list[dict[str, Any]] = []

    for seed in FINANCE_PRIORITY_SEEDS:
        candidates.append({
            "keyword": seed,
            "source": "finance_seed",
            "trend_score": 8.0,
            "seed_priority": 1.0,
        })

    trend_limit = env_int("HOT_ISSUE_TREND_LIMIT", 35)
    for rank, kw in enumerate(fetch_google_trends_keywords(limit=trend_limit), start=1):
        candidates.append({
            "keyword": kw,
            "source": "google_trends",
            "trend_score": max(8.0, 42.0 - rank),
            "seed_priority": 0.0,
        })

    for seed in BALANCED_SEEDS:
        candidates.append({
            "keyword": seed,
            "source": "balanced_seed",
            "trend_score": 6.0,
            "seed_priority": 0.2,
        })

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
        return 2.0

    now = datetime.now(KST)
    hours = max(0.0, (now - published).total_seconds() / 3600)
    if hours <= 6:
        return 18.0
    if hours <= 12:
        return 14.0
    if hours <= 24:
        return 10.0
    if hours <= 48:
        return 6.0
    return 1.0


def count_keyword_hits(text: str, words: list[str]) -> int:
    lower = text.lower()
    return sum(1 for word in words if word.lower() in lower)


def noise_score(keyword: str, articles: list[dict[str, Any]], category: str) -> tuple[float, list[str]]:
    text = " ".join([keyword] + [a.get("title", "") + " " + a.get("description", "") for a in articles[:5]])
    hits = [word for word in NOISE_KEYWORDS if word.lower() in text.lower()]
    score = len(hits) * 18.0

    if category in {"연예·문화", "스포츠", "기타"}:
        score += 18.0

    # 근거자료가 전부 약한 도메인이거나 포토/방송 캡처성인 경우 감점
    if count_keyword_hits(text, ["포토", "캡처", "인스타", "열애설", "종영"]) >= 2:
        score += 14.0

    return score, hits[:6]


def adsense_value_score(keyword: str, articles: list[dict[str, Any]], category: str) -> float:
    text = " ".join([keyword] + [a.get("title", "") + " " + a.get("description", "") for a in articles[:5]])
    hits = count_keyword_hits(text, ADSENSE_VALUE_KEYWORDS)

    base_by_category = {
        "경제·금융": 34,
        "증권·투자": 32,
        "산업·기업": 30,
        "정책·지원금": 32,
        "부동산·주거금융": 34,
        "생활·제도": 28,
        "건강·의료": 24,
        "교육·입시": 22,
        "국제": 18,
        "날씨·안전": 18,
        "시사·정치": 15,
        "사회·사건": 14,
        "스포츠": 4,
        "연예·문화": 3,
        "기타": 2,
    }.get(category, 5)

    return base_by_category + min(hits * 3, 24)


def editorial_importance_score(keyword: str, articles: list[dict[str, Any]], category: str) -> float:
    text = " ".join([keyword] + [a.get("title", "") + " " + a.get("description", "") for a in articles[:5]])
    hits = count_keyword_hits(text, EDITORIAL_IMPORTANCE_KEYWORDS)

    category_weight = {
        "경제·금융": 22,
        "증권·투자": 20,
        "산업·기업": 18,
        "정책·지원금": 20,
        "부동산·주거금융": 18,
        "생활·제도": 18,
        "국제": 16,
        "날씨·안전": 16,
        "시사·정치": 14,
        "사회·사건": 12,
        "건강·의료": 12,
        "교육·입시": 10,
        "스포츠": 2,
        "연예·문화": 2,
        "기타": 1,
    }.get(category, 5)

    return category_weight + min(hits * 3, 21)


def evidence_score(articles: list[dict[str, Any]]) -> float:
    count = len(articles)
    if count <= 0:
        return -50
    domain_count = len({a.get("domain") for a in articles if a.get("domain")})
    return min(count * 9 + domain_count * 3, 55)


def make_why_important(keyword: str, category: str, noise: float) -> str:
    if category in {"경제·금융", "부동산·주거금융", "생활·제도"}:
        return "생활비·물가·금융 부담과 직접 연결되는 이슈입니다."
    if category == "증권·투자":
        return "증시 흐름과 투자심리 변화를 설명할 수 있는 이슈입니다."
    if category == "산업·기업":
        return "기업 실적·공급망·산업 경쟁력과 연결되는 이슈입니다."
    if category == "정책·지원금":
        return "정부 정책 변화와 독자 행동 체크포인트가 있는 이슈입니다."
    if category in {"국제", "날씨·안전"}:
        return "국내 경제·생활에 파급될 수 있는 외부 변수입니다."
    if category in {"시사·정치", "사회·사건", "건강·의료", "교육·입시"}:
        return "사회적 관심과 제도 변화 가능성이 있는 이슈입니다."
    if noise >= 25:
        return "검색 관심은 높지만 정보성 글감으로는 제한적입니다."
    return "대중 관심이 높아 보조 이슈로 활용할 수 있습니다."


def make_blog_angle(keyword: str, category: str, adsense_score_value: float) -> str:
    if adsense_score_value >= 45:
        return f"{keyword}의 배경, 영향, 확인할 체크포인트를 정리하는 정보형 글"
    if category in {"스포츠", "연예·문화"}:
        return f"{keyword} 관련 이슈 흐름과 대중 관심 포인트를 가볍게 정리하는 글"
    return f"{keyword} 핵심 내용과 후속 확인 포인트를 정리하는 글"


def make_card_angle(keyword: str, category: str) -> str:
    if category in {"경제·금융", "증권·투자", "산업·기업", "정책·지원금", "부동산·주거금융", "생활·제도"}:
        return "원인 → 생활/시장 영향 → 확인할 지표 → 대응 체크리스트"
    if category in {"국제", "날씨·안전"}:
        return "발생 상황 → 국내 영향 → 위험 요인 → 체크포인트"
    return "핵심 사건 → 쟁점 → 영향을 받는 사람 → 후속 확인"


def score_candidate(keyword: str, source: str, seed_priority: float, trend_score_value: float, articles: list[dict[str, Any]]) -> dict[str, Any]:
    category = classify_category(keyword, articles)
    recent_score = sum(article_recency_score(a) for a in articles[:5])
    evid_score = evidence_score(articles)
    adsense_score_value = adsense_value_score(keyword, articles, category)
    editorial_score_value = editorial_importance_score(keyword, articles, category)
    n_score, noise_flags = noise_score(keyword, articles, category)

    source_bonus = 12.0 if source == "google_trends" else 0.0
    seed_bonus = 18.0 * float(seed_priority or 0)
    category_boost = {
        "경제·금융": 25,
        "증권·투자": 23,
        "산업·기업": 22,
        "정책·지원금": 23,
        "부동산·주거금융": 22,
        "생활·제도": 18,
        "국제": 13,
        "날씨·안전": 12,
        "시사·정치": 10,
        "사회·사건": 8,
        "건강·의료": 10,
        "교육·입시": 8,
        "스포츠": -8,
        "연예·문화": -10,
        "기타": -14,
    }.get(category, 0)

    final_score = (
        trend_score_value * 0.9
        + evid_score
        + recent_score * 0.7
        + adsense_score_value
        + editorial_score_value
        + category_boost
        + source_bonus
        + seed_bonus
        - n_score
    )

    slot = item_slot({"category": category})
    return {
        "keyword": keyword,
        "category": category,
        "slot": slot,
        "score": round(final_score, 2),
        "editorial_score": round(editorial_score_value + adsense_score_value + evid_score - n_score, 2),
        "trend_score": round(trend_score_value, 2),
        "evidence_score": round(evid_score, 2),
        "adsense_score": round(adsense_score_value, 2),
        "freshness_score": round(recent_score, 2),
        "noise_score": round(n_score, 2),
        "noise_flags": noise_flags,
        "source": source,
        "articles": articles,
        "article_count": len(articles),
        "why_important": make_why_important(keyword, category, n_score),
        "blog_angle": make_blog_angle(keyword, category, adsense_score_value),
        "card_angle": make_card_angle(keyword, category),
        "score_breakdown": {
            "trend": round(trend_score_value * 0.9, 2),
            "evidence": round(evid_score, 2),
            "freshness": round(recent_score * 0.7, 2),
            "adsense": round(adsense_score_value, 2),
            "editorial": round(editorial_score_value, 2),
            "category_boost": round(category_boost, 2),
            "source_bonus": round(source_bonus, 2),
            "seed_bonus": round(seed_bonus, 2),
            "noise_penalty": round(n_score, 2),
        },
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
            trend_score_value=float(candidate.get("trend_score") or 0),
            articles=articles,
        )

        if item["article_count"] > 0:
            scored.append(item)

        print(
            f"[{idx}/{len(candidates)}] {keyword} "
            f"slot={item['slot']} category={item['category']} "
            f"score={item['score']} editorial={item['editorial_score']} noise={item['noise_score']} "
            f"articles={item['article_count']}"
        )

        time.sleep(env_float("HOT_ISSUE_REQUEST_SLEEP", 0.12))

    return sorted(scored, key=lambda x: x.get("score", 0), reverse=True)


# ============================================================
# 선발 엔진
# ============================================================

def is_duplicate_item(item: dict[str, Any], selected: list[dict[str, Any]], threshold: float = 0.42) -> bool:
    text = f"{item.get('keyword','')} " + " ".join(a.get("title", "") for a in item.get("articles", [])[:3])
    for chosen in selected:
        other = f"{chosen.get('keyword','')} " + " ".join(a.get("title", "") for a in chosen.get("articles", [])[:3])
        if compact_key(item.get("keyword", "")) == compact_key(chosen.get("keyword", "")):
            return True
        if text_similarity(text, other) >= threshold:
            return True
    return False


def select_slot_editorial_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    top_n = env_int("HOT_ISSUE_TOP_N", DEFAULT_TOP_N)
    slot_plan = slot_plan_from_env()
    noise_max = env_int("HOT_ISSUE_NOISE_MAX", 1)
    dedupe_threshold = env_float("HOT_ISSUE_DEDUPE_THRESHOLD", 0.42)

    sorted_items = sorted(items, key=lambda x: x.get("score", 0), reverse=True)
    selected: list[dict[str, Any]] = []

    def can_add(item: dict[str, Any]) -> bool:
        if len(selected) >= top_n:
            return False
        if is_duplicate_item(item, selected, threshold=dedupe_threshold):
            return False
        if item.get("slot") == "대중관심":
            current_noise = sum(1 for x in selected if x.get("slot") == "대중관심")
            if current_noise >= noise_max:
                return False
        return True

    # 1) 고정 슬롯 선발
    for slot_name, count in slot_plan:
        slot_categories = SLOT_DEFINITIONS.get(slot_name, [])
        pool = [
            item for item in sorted_items
            if (item.get("slot") == slot_name or item.get("category") in slot_categories)
        ]
        picked = 0
        for item in pool:
            if picked >= count:
                break
            if can_add(item):
                selected.append(item)
                picked += 1

    # 2) 부족하면 편집 점수순 보충. 단 대중관심은 제한 유지.
    if len(selected) < top_n:
        fallback = sorted(
            sorted_items,
            key=lambda x: (
                x.get("slot") == "대중관심",
                -float(x.get("editorial_score") or 0),
                -float(x.get("score") or 0),
            )
        )
        for item in fallback:
            if len(selected) >= top_n:
                break
            if can_add(item):
                selected.append(item)

    # 3) 그래도 부족하면 중복만 피하고 채움.
    if len(selected) < top_n:
        for item in sorted_items:
            if len(selected) >= top_n:
                break
            if is_duplicate_item(item, selected, threshold=dedupe_threshold):
                continue
            selected.append(item)

    # 최종 순서는 슬롯 계획 순서 → 점수
    slot_order = {slot: idx for idx, (slot, _) in enumerate(slot_plan)}
    selected.sort(key=lambda x: (slot_order.get(x.get("slot"), 999), -float(x.get("score") or 0)))

    for idx, item in enumerate(selected, start=1):
        item["rank"] = idx

    return selected[:top_n]


def apply_hotissue_editorial_policy(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    mode = env("HOT_ISSUE_EDITORIAL_MODE", "slot_editorial").lower()
    top_n = env_int("HOT_ISSUE_TOP_N", DEFAULT_TOP_N)

    if mode == "all_score":
        selected = sorted(items, key=lambda x: x.get("score", 0), reverse=True)[:top_n]
    else:
        selected = select_slot_editorial_items(items)

    for idx, item in enumerate(selected, start=1):
        item["rank"] = idx
    return selected


def select_morning_cardnews_items(hot_items: list[dict[str, Any]], max_issues: int = 5) -> list[dict[str, Any]]:
    """Daily TOP 10 중 Morning 카드뉴스로 설명하기 좋은 이슈를 고릅니다."""
    min_score = env_float("HEADLINE_CARDNEWS_MIN_EDITORIAL_SCORE", 40.0)
    avoid_slots = set(parse_csv(env("HEADLINE_AVOID_SLOTS"), ["대중관심"]))
    prefer_slots = parse_csv(
        env("HEADLINE_PREFER_SLOTS"),
        ["경제·금융", "증권·투자", "산업·기업", "정책·생활", "국제·안전", "사회·시사"],
    )

    preferred = [
        item for item in hot_items
        if item.get("slot") in prefer_slots
        and float(item.get("editorial_score") or 0) >= min_score
    ]

    selected: list[dict[str, Any]] = []
    for item in sorted(preferred, key=lambda x: (prefer_slots.index(x.get("slot")) if x.get("slot") in prefer_slots else 999, -float(x.get("editorial_score") or 0))):
        if len(selected) >= max_issues:
            break
        if not is_duplicate_item(item, selected):
            selected.append(item)

    if len(selected) < max_issues:
        fallback = [
            item for item in hot_items
            if item not in selected and item.get("slot") not in avoid_slots
        ]
        fallback.sort(key=lambda x: -float(x.get("editorial_score") or 0))
        for item in fallback:
            if len(selected) >= max_issues:
                break
            if not is_duplicate_item(item, selected):
                selected.append(item)

    if len(selected) < max_issues:
        for item in hot_items:
            if len(selected) >= max_issues:
                break
            if item not in selected and not is_duplicate_item(item, selected):
                selected.append(item)

    for idx, item in enumerate(selected, start=1):
        item["morning_rank"] = idx
    return selected[:max_issues]


# ============================================================
# 리포트 생성
# ============================================================

def build_telegram_report(items: list[dict[str, Any]]) -> str:
    lines = []
    lines.append("🔥 오늘의 핫이슈 TOP 10")
    lines.append("")
    lines.append("📊 오늘의 이슈 구성")
    lines.append(f"슬롯 구성: {slot_mix_text(items)}")
    lines.append(f"카테고리 구성: {category_mix_text(items)}")
    lines.append(f"편집 정책: {editorial_policy_text()}")
    lines.append("")

    for idx, item in enumerate(items, start=1):
        score_brief = (
            f"편집점수 {item.get('editorial_score')} / "
            f"글감 {item.get('adsense_score')} / "
            f"노이즈 {item.get('noise_score')}"
        )
        lines.append(f"{idx}. [{item.get('slot')}/{item.get('category')}] {item['keyword']}")
        lines.append(f"왜 중요함: {item.get('why_important')}")
        lines.append(f"글감 방향: {item.get('blog_angle')}")
        lines.append(f"점수: {score_brief}")

        if item.get("noise_flags"):
            lines.append(f"주의 신호: {', '.join(item.get('noise_flags')[:4])}")

        lines.append("근거자료:")
        for article_idx, article in enumerate(item.get("articles", [])[:5], start=1):
            title = short_text(article.get("title", ""), 78)
            url = article.get("url", "")
            domain = article.get("domain") or domain_of(url)
            date = fmt_date(article.get("published_at"))
            lines.append(f"  {article_idx}) {title} ({url}) ({domain} · {date})")

        if not item.get("articles"):
            lines.append("  - 근거자료 부족")

        lines.append("")

    card_items = select_morning_cardnews_items(items, max_issues=min(3, len(items)))
    lines.append("🃏 오늘의 카드뉴스 추천")
    lines.append("")
    for idx, item in enumerate(card_items, start=1):
        lines.append(f"{idx}. #{idx} {item['keyword']}")
        lines.append(f"구성방향: {item.get('card_angle')}")
        lines.append("")

    lines.append("✍️ 오늘의 작성글 추천")
    lines.append("")
    article_items = sorted(
        items,
        key=lambda x: (-float(x.get("adsense_score") or 0), -float(x.get("editorial_score") or 0)),
    )[:3]
    for idx, item in enumerate(article_items, start=1):
        lines.append(f"{idx}. #{idx} {item['keyword']}")
        lines.append(f"글방향: {item.get('blog_angle')}")
        lines.append("")

    lines.append("📌 확인 메모")
    lines.append("이 리포트는 단순 검색량보다 경제성·정보성·글감 가치를 우선 반영합니다.")
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


def save_reports(items: list[dict[str, Any]], report_text: str, scored_items: list[dict[str, Any]] | None = None) -> None:
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    now = datetime.now(KST)
    ymd = now.strftime("%Y%m%d")
    morning_items = select_morning_cardnews_items(items, max_issues=env_int("HEADLINE_CARDNEWS_ISSUES", 5))

    payload = {
        "generated_at": now.isoformat(),
        "editorial_policy": editorial_policy_text(),
        "slot_plan": [{"slot": s, "count": c} for s, c in slot_plan_from_env()],
        "slot_mix": slot_mix_text(items),
        "category_mix": category_mix_text(items),
        "items": scored_items or [],
        "hot_items": items,
        "morning_items": morning_items,
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
# 실행 / Payload
# ============================================================

def build_daily_hotissue_payload(*, send_report: bool = False, save_report: bool = False) -> dict[str, Any]:
    scored_items = build_scored_items()
    hot_items = apply_hotissue_editorial_policy(scored_items) if scored_items else []
    morning_items = select_morning_cardnews_items(hot_items, max_issues=env_int("HEADLINE_CARDNEWS_ISSUES", 5))
    report_text = build_telegram_report(hot_items) if hot_items else "🔥 오늘의 핫이슈 TOP 10\n\n수집된 이슈 후보가 없습니다."

    if save_report and hot_items:
        save_reports(hot_items, report_text, scored_items=scored_items)

    if send_report:
        send_telegram_message(report_text)

    return {
        "items": scored_items,
        "hot_items": hot_items,
        "morning_items": morning_items,
        "card_items": morning_items,
        "article_items": sorted(hot_items, key=lambda x: (-float(x.get("adsense_score") or 0), -float(x.get("editorial_score") or 0)))[:3],
        "report_text": report_text,
        "editorial_policy": editorial_policy_text(),
        "slot_mix": slot_mix_text(hot_items),
        "category_mix": category_mix_text(hot_items),
        "effective_lookback_hours": env_int("HOT_ISSUE_LOOKBACK_HOURS", 48),
        "hot_issue_count": len(hot_items),
    }


def main() -> None:
    print("[Daily AdSense SEO Hot Issue Report · Editorial Engine v1.28]")
    print("KST now:", datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S"))
    print("Policy:", editorial_policy_text())

    payload = build_daily_hotissue_payload(send_report=False, save_report=False)
    hot_items = payload.get("hot_items") or []

    if not hot_items:
        message = "🔥 오늘의 핫이슈 TOP 10\n\n수집된 이슈 후보가 없습니다."
        send_telegram_message(message)
        return

    print("[selected slot mix]", payload.get("slot_mix"))
    for idx, item in enumerate(hot_items, start=1):
        print(
            f"{idx}. [{item.get('slot')}/{item.get('category')}] {item.get('keyword')} "
            f"score={item.get('score')} editorial={item.get('editorial_score')} adsense={item.get('adsense_score')} noise={item.get('noise_score')}"
        )

    report_text = payload["report_text"]
    save_reports(hot_items, report_text, scored_items=payload.get("items") or [])
    send_telegram_message(report_text)


if __name__ == "__main__":
    main()
