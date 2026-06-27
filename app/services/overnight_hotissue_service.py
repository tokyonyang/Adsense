from __future__ import annotations

import html
import json
import os
import random
import re
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
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
GOOGLE_TRENDS_RSS_KR = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=KR"
GOOGLE_TRENDS_RSS_US = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"

YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"

WEATHER_REGIONS = [
    "서울", "인천", "수원", "춘천", "강릉", "대전", "청주",
    "대구", "부산", "울산", "광주", "전주", "제주"
]

WEATHER_COORDS = {
    "서울": (37.5665, 126.9780),
    "인천": (37.4563, 126.7052),
    "수원": (37.2636, 127.0286),
    "춘천": (37.8813, 127.7298),
    "강릉": (37.7519, 128.8761),
    "대전": (36.3504, 127.3845),
    "청주": (36.6424, 127.4890),
    "대구": (35.8714, 128.6014),
    "부산": (35.1796, 129.0756),
    "울산": (35.5384, 129.3114),
    "광주": (35.1595, 126.8526),
    "전주": (35.8242, 127.1480),
    "제주": (33.4996, 126.5312),
}

QUOTES = [
    ("성공은 최종 목적지가 아니고, 실패도 치명적이지 않다. 중요한 것은 계속 나아갈 용기다.", "윈스턴 처칠"),
    ("기회는 준비된 사람에게 온다.", "루이 파스퇴르"),
    ("미래는 오늘 무엇을 하느냐에 달려 있다.", "마하트마 간디"),
    ("작은 일을 완벽하게 해내는 것이 큰 일을 해내는 첫걸음이다.", "데일 카네기"),
    ("단순함은 궁극의 정교함이다.", "레오나르도 다빈치"),
    ("변화는 위협이 아니라 기회다.", "피터 드러커"),
    ("어제보다 나은 오늘이 가장 확실한 성장이다.", "gooddaynews.store"),
]

US_NEWS_QUERIES = [
    "US economy stock market inflation AI semiconductor",
    "Wall Street Federal Reserve interest rates tech stocks",
    "US politics economy global markets",
    "Nvidia Apple Microsoft Tesla stock market news",
    "oil dollar treasury yields global markets",
]

KOREA_NEWS_QUERIES = [
    "오늘 아침 뉴스 경제 금융",
    "오늘 아침 주요 뉴스 정치 사회 경제",
    "한국 증시 환율 부동산 오늘 뉴스",
    "정부 정책 지원금 생활물가 오늘 뉴스",
    "반도체 AI 기업 산업 오늘 뉴스",
]

REALTIME_KEYWORD_QUERIES = [
    "실시간 검색어",
    "급상승 키워드",
    "인기 검색어",
    "오늘의 키워드",
]


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def env_int(name: str, default: int) -> int:
    try:
        return int(env(name, str(default)))
    except Exception:
        return default


def env_bool(name: str, default: bool = False) -> bool:
    value = env(name, "true" if default else "false").lower()
    return value in {"1", "true", "yes", "y", "on"}


def clean_html(text: str) -> str:
    text = html.unescape(text or "")
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def short_text(text: str, limit: int = 88) -> str:
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
        return host.replace("www.", "")[:38] or "news"
    except Exception:
        return "news"


def parse_date(value: str | None):
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).astimezone(KST)
    except Exception:
        return None


def fmt_time(dt: Any) -> str:
    if isinstance(dt, datetime):
        return dt.strftime("%m-%d %H:%M")
    return "시간불명"


def normalize_keyword(text: str) -> str:
    text = clean_html(text)
    text = re.sub(r"[\[\]\(\)\{\}:|]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" -·ㆍ|")


def dedupe_articles(articles: list[dict[str, Any]], limit: int = 10) -> list[dict[str, Any]]:
    seen = set()
    result = []
    for a in articles:
        title_key = re.sub(r"[^0-9A-Za-z가-힣]", "", (a.get("title") or "").lower())[:80]
        if not title_key or title_key in seen:
            continue
        seen.add(title_key)
        result.append(a)
        if len(result) >= limit:
            break
    return result


def filter_recent_articles(articles: list[dict[str, Any]], hours: int) -> list[dict[str, Any]]:
    cutoff = datetime.now(KST) - timedelta(hours=hours)
    filtered = []
    for article in articles:
        published = article.get("published_at")
        if isinstance(published, datetime) and published < cutoff:
            continue
        filtered.append(article)
    return filtered


def fetch_google_news(query: str, limit: int = 10, hl: str = "ko", gl: str = "KR", ceid: str = "KR:ko") -> list[dict[str, Any]]:
    if feedparser is None:
        return []

    rss = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl={hl}&gl={gl}&ceid={ceid}"

    try:
        feed = feedparser.parse(rss)
    except Exception as exc:
        print(f"[google news] failed query={query}: {exc}")
        return []

    rows = []
    for entry in feed.entries[:limit]:
        title = clean_html(getattr(entry, "title", ""))
        title = re.sub(r"\s+-\s+[^-]{1,40}$", "", title).strip()
        url = getattr(entry, "link", "") or ""
        rows.append({
            "title": short_text(title, 120),
            "description": short_text(clean_html(getattr(entry, "summary", "")), 180),
            "url": url,
            "domain": domain_of(url),
            "published_at": parse_date(getattr(entry, "published", "")),
            "source": "google",
        })

    return rows


def fetch_naver_news(query: str, limit: int = 10) -> list[dict[str, Any]]:
    client_id = env("NAVER_CLIENT_ID")
    client_secret = env("NAVER_CLIENT_SECRET")
    if not client_id or not client_secret:
        return []

    try:
        response = requests.get(
            NAVER_NEWS_URL,
            headers={"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret},
            params={"query": query, "display": limit, "start": 1, "sort": "date"},
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        print(f"[naver news] failed query={query}: {exc}")
        return []

    rows = []
    for item in data.get("items", []):
        url = item.get("originallink") or item.get("link") or ""
        rows.append({
            "title": short_text(clean_html(item.get("title", "")), 120),
            "description": short_text(clean_html(item.get("description", "")), 180),
            "url": url,
            "domain": domain_of(url),
            "published_at": parse_date(item.get("pubDate")),
            "source": "naver",
        })
    return rows


def fetch_trends(geo: str = "KR", limit: int = 12) -> list[str]:
    if feedparser is None:
        return []

    rss = GOOGLE_TRENDS_RSS_KR if geo.upper() == "KR" else GOOGLE_TRENDS_RSS_US
    try:
        feed = feedparser.parse(rss)
    except Exception as exc:
        print(f"[trends] failed geo={geo}: {exc}")
        return []

    keywords = []
    for entry in feed.entries[:limit]:
        title = normalize_keyword(getattr(entry, "title", ""))
        if title and title not in keywords:
            keywords.append(title)
    return keywords


def make_issue_from_articles(topic: str, articles: list[dict[str, Any]], category: str) -> dict[str, Any]:
    articles = dedupe_articles(articles, limit=3)
    if not articles:
        return {
            "topic": topic,
            "category": category,
            "headline": topic,
            "summary_lines": ["관련 기사 후보가 부족합니다.", "추가 수집 후 업데이트가 필요합니다.", "후속 보도를 확인하세요."],
            "insight": "근거 기사 수집량이 부족해 후속 업데이트가 필요합니다.",
            "articles": [],
        }

    headline = topic
    summary_lines = []
    for a in articles[:3]:
        summary_lines.append(short_text(a.get("title") or a.get("description") or topic, 72))
    while len(summary_lines) < 3:
        summary_lines.append("같은 주제의 후속 보도 흐름을 함께 확인할 필요가 있습니다.")

    insight = make_basic_insight(topic, category, " ".join(summary_lines))

    return {
        "topic": topic,
        "category": category,
        "headline": headline,
        "summary_lines": summary_lines[:3],
        "insight": insight,
        "articles": articles[:3],
        "sources": [a.get("domain") for a in articles[:3] if a.get("domain")],
    }


def make_basic_insight(topic: str, category: str, text: str) -> str:
    blob = f"{topic} {category} {text}"
    if any(k in blob for k in ["금리", "Federal Reserve", "Fed", "FOMC", "국채"]):
        return "금리 기대가 흔들리면 달러와 성장주, 채권금리가 동시에 시장 방향을 결정할 수 있습니다."
    if any(k in blob for k in ["증시", "나스닥", "S&P", "다우", "코스피", "주가", "Wall Street"]):
        return "간밤의 증시 흐름은 국내 개장 초반 수급과 투자심리에 직접 반영될 가능성이 큽니다."
    if any(k in blob for k in ["AI", "반도체", "Nvidia", "Apple", "Microsoft", "테슬라", "semiconductor"]):
        return "AI와 반도체 이슈는 국내 성장주와 대형 기술주의 단기 방향성을 가르는 핵심 변수입니다."
    if any(k in blob for k in ["환율", "달러", "원화", "외환"]):
        return "환율 변동성이 커지면 수입물가와 외국인 자금 흐름이 함께 흔들릴 수 있습니다."
    if any(k in blob for k in ["부동산", "전세", "주택", "대출"]):
        return "주거비와 대출 조건 변화는 소비심리와 가계 부담에 시차를 두고 영향을 줍니다."
    if any(k in blob for k in ["날씨", "폭염", "비", "미세먼지", "자외선"]):
        return "기상 변수는 출근길 이동과 건강관리, 야외 활동 계획에 직접적인 영향을 줍니다."
    return "여러 매체에서 반복되는 이슈는 후속 정책 반응과 시장 영향을 함께 확인해야 합니다."


def summarize_with_gemini(section_name: str, issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    api_key = env("GEMINI_API_KEY")
    if not api_key or not issues:
        return issues

    try:
        import google.generativeai as genai
    except Exception:
        return issues

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        payload = [
            {
                "topic": i.get("topic"),
                "category": i.get("category"),
                "headline": i.get("headline"),
                "articles": [
                    {
                        "title": a.get("title"),
                        "description": a.get("description"),
                        "domain": a.get("domain"),
                    }
                    for a in i.get("articles", [])[:3]
                ],
            }
            for i in issues
        ]
        prompt = f"""
아래는 '{section_name}' 섹션의 기사 묶음입니다.
각 항목을 카드뉴스와 텍스트 리포트에 들어갈 수 있도록 정리하세요.

반드시 JSON 배열만 반환하세요.
각 원소는 topic, category, headline, summary_lines, insight 키를 포함하세요.

규칙:
- headline: 단순 키워드가 아니라 공통 쟁점 제목. 18~36자.
- summary_lines: 정확히 3개. 각 45~70자.
- insight: 향후 전망/시장 영향/생활 영향 중심 한 문장. 42~75자.
- 입력 기사에 없는 구체적 수치나 사건을 만들지 마세요.
- 한국어로 작성하세요.

입력:
{json.dumps(payload, ensure_ascii=False)}
"""
        response = model.generate_content(prompt)
        text = response.text.strip()
        match = re.search(r"\[.*\]", text, re.S)
        if not match:
            return issues
        rows = json.loads(match.group(0))

        by_topic = {i["topic"]: i for i in issues}
        result = []
        for row in rows:
            topic = row.get("topic")
            base = by_topic.get(topic)
            if not base:
                continue
            result.append({
                **base,
                "headline": short_text(row.get("headline") or base["headline"], 50),
                "summary_lines": [short_text(x, 78) for x in (row.get("summary_lines") or base["summary_lines"])][:3],
                "insight": short_text(row.get("insight") or base["insight"], 95),
            })
        used = {x["topic"] for x in result}
        for issue in issues:
            if issue["topic"] not in used:
                result.append(issue)
        return result[:len(issues)]
    except Exception as exc:
        print(f"[gemini summary failed] {section_name}: {exc}")
        return issues


def collect_us_news() -> list[dict[str, Any]]:
    lookback = env_int("OVERNIGHT_LOOKBACK_HOURS", 16)
    articles = []
    for q in US_NEWS_QUERIES:
        articles.extend(fetch_google_news(q, limit=env_int("OVERNIGHT_NEWS_PER_QUERY", 8), hl="en-US", gl="US", ceid="US:en"))
    articles = filter_recent_articles(dedupe_articles(articles, 40), lookback)

    topics = ["미국 증시·경제", "연준·금리", "AI·빅테크", "국제유가·달러"]
    issues = []
    for topic in topics:
        related = [a for a in articles if topic_related(topic, a)]
        if not related:
            related = articles[:3]
        issues.append(make_issue_from_articles(topic, related[:3], "미국뉴스"))
    return summarize_with_gemini("미국뉴스 주요 이슈", issues)


def topic_related(topic: str, article: dict[str, Any]) -> bool:
    text = f"{article.get('title','')} {article.get('description','')}".lower()
    rules = {
        "미국 증시·경제": ["stock", "market", "wall street", "economy", "s&p", "dow", "nasdaq"],
        "연준·금리": ["fed", "federal reserve", "rate", "yield", "treasury", "inflation"],
        "AI·빅테크": ["ai", "nvidia", "apple", "microsoft", "tesla", "google", "semiconductor"],
        "국제유가·달러": ["oil", "dollar", "crude", "wti", "energy"],
        "국내 아침뉴스": ["오늘", "아침", "경제", "사회", "정치", "증시", "정부"],
    }
    return any(k in text for k in rules.get(topic, []))


def collect_korea_news() -> list[dict[str, Any]]:
    lookback = env_int("OVERNIGHT_LOOKBACK_HOURS", 16)
    articles = []
    for q in KOREA_NEWS_QUERIES:
        articles.extend(fetch_naver_news(q, limit=env_int("OVERNIGHT_NEWS_PER_QUERY", 8)))
        articles.extend(fetch_google_news(q, limit=4))
    articles = filter_recent_articles(dedupe_articles(articles, 45), lookback)

    topics = ["국내 아침뉴스", "경제·금융", "정책·사회", "산업·기업"]
    issues = []
    for topic in topics:
        related = [a for a in articles if korea_topic_related(topic, a)]
        if not related:
            related = articles[:3]
        issues.append(make_issue_from_articles(topic, related[:3], "국내뉴스"))
    return summarize_with_gemini("국내뉴스 아침 이슈", issues)


def korea_topic_related(topic: str, article: dict[str, Any]) -> bool:
    text = f"{article.get('title','')} {article.get('description','')}"
    rules = {
        "국내 아침뉴스": ["오늘", "아침", "주요", "뉴스"],
        "경제·금융": ["환율", "금리", "증시", "코스피", "대출", "물가", "금융", "부동산", "전세"],
        "정책·사회": ["정부", "국회", "정책", "지원", "검찰", "경찰", "사회", "사건"],
        "산업·기업": ["삼성", "하이닉스", "반도체", "AI", "현대차", "네이버", "카카오", "기업"],
    }
    return any(k in text for k in rules.get(topic, []))


def fetch_market_symbol(symbol: str, range_: str = "5d", interval: str = "1d") -> dict[str, Any]:
    try:
        response = requests.get(
            YAHOO_CHART_URL.format(symbol=symbol),
            params={"range": range_, "interval": interval},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()["chart"]["result"][0]
        timestamps = data.get("timestamp") or []
        quote = data.get("indicators", {}).get("quote", [{}])[0]
        closes = [x for x in (quote.get("close") or []) if x is not None]
        if len(closes) < 2:
            return {}
        start, end = float(closes[-2]), float(closes[-1])
        change = end - start
        change_pct = change / start * 100 if start else 0
        return {
            "symbol": symbol,
            "value": round(end, 2),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "direction": "상승" if change >= 0 else "하락",
            "points": [round(float(x), 2) for x in closes[-10:]],
        }
    except Exception as exc:
        print(f"[market] failed {symbol}: {exc}")
        return {}


def collect_us_market_summary() -> dict[str, Any]:
    indices = [
        ("다우", "^DJI"),
        ("S&P500", "^GSPC"),
        ("나스닥", "^IXIC"),
        ("필라델피아 반도체", "^SOX"),
        ("WTI", "CL=F"),
        ("달러인덱스", "DX-Y.NYB"),
        ("미국 10년물", "^TNX"),
    ]
    rows = []
    for name, symbol in indices:
        data = fetch_market_symbol(symbol)
        if data:
            rows.append({"name": name, **data})

    if not rows:
        return {
            "headline": "미증시 데이터 연결 대기",
            "summary_lines": ["지수 데이터 수집이 원활하지 않습니다.", "뉴스 흐름 중심으로 시장 분위기를 확인하세요.", "다음 실행에서 다시 업데이트됩니다."],
            "insight": "지수 데이터가 부족할 때는 금리·달러·기술주 뉴스 흐름을 함께 확인해야 합니다.",
            "indices": [],
        }

    main = rows[:4]
    up = [r for r in main if r.get("change", 0) >= 0]
    down = [r for r in main if r.get("change", 0) < 0]

    headline = "미증시 혼조" if up and down else ("미증시 상승" if up else "미증시 하락")
    summary_lines = [
        " · ".join(f"{r['name']} {r['direction']} {abs(r['change_pct'])}%" for r in main[:3]),
        "기술주·금리·달러 흐름이 국내 개장 초반 투자심리에 영향을 줄 수 있습니다.",
        "반도체와 빅테크 움직임은 국내 성장주 수급의 선행 변수로 볼 필요가 있습니다.",
    ]
    insight = "간밤 미증시 흐름은 국내 장 초반 반도체·성장주·환율 민감 업종의 방향성을 가를 수 있습니다."

    return {
        "headline": headline,
        "summary_lines": summary_lines,
        "insight": insight,
        "indices": rows,
    }


def collect_keywords() -> dict[str, Any]:
    kr = fetch_trends("KR", limit=env_int("OVERNIGHT_TREND_LIMIT", 12))
    us = fetch_trends("US", limit=env_int("OVERNIGHT_TREND_LIMIT", 12))

    realtime = []
    # Naver API가 있으면 검색어 관련 최신 기사 제목에서 보조 키워드 추출
    for q in REALTIME_KEYWORD_QUERIES:
        for article in fetch_naver_news(q, limit=5):
            title = normalize_keyword(article.get("title", ""))
            tokens = re.findall(r"[가-힣A-Za-z0-9]{2,}", title)
            for t in tokens:
                if t not in realtime and len(t) <= 12 and t not in {"실시간", "검색어", "급상승", "키워드", "오늘"}:
                    realtime.append(t)
            if len(realtime) >= 10:
                break
        if len(realtime) >= 10:
            break

    if not realtime:
        realtime = kr[:10]

    return {
        "kr_trends": kr[:10],
        "us_trends": us[:10],
        "realtime_keywords": realtime[:10],
        "popular_keywords": dedupe_keywords((kr[:6] + us[:6] + realtime[:6]))[:15],
    }


def dedupe_keywords(words: list[str]) -> list[str]:
    seen = set()
    result = []
    for w in words:
        key = re.sub(r"[^0-9A-Za-z가-힣]", "", str(w).lower())
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(str(w))
    return result


def uv_label(uv: float | None) -> str:
    if uv is None:
        return "정보없음"
    if uv < 3:
        return "낮음"
    if uv < 6:
        return "보통"
    if uv < 8:
        return "높음"
    if uv < 11:
        return "매우높음"
    return "위험"


def pm_label(pm: float | None) -> str:
    if pm is None:
        return "정보없음"
    if pm <= 15:
        return "좋음"
    if pm <= 35:
        return "보통"
    if pm <= 75:
        return "나쁨"
    return "매우나쁨"


def weather_code_label(code: int | None) -> str:
    if code is None:
        return "날씨 정보"
    if code == 0:
        return "맑음"
    if code in {1, 2, 3}:
        return "구름"
    if code in {45, 48}:
        return "안개"
    if code in {51, 53, 55, 61, 63, 65, 80, 81, 82}:
        return "비"
    if code in {71, 73, 75, 77, 85, 86}:
        return "눈"
    if code in {95, 96, 99}:
        return "뇌우"
    return "날씨 정보"


def collect_weather() -> list[dict[str, Any]]:
    if not env_bool("OVERNIGHT_ENABLE_WEATHER", True):
        return []

    regions = [x.strip() for x in env("OVERNIGHT_WEATHER_REGIONS", ",".join(WEATHER_REGIONS)).split(",") if x.strip()]
    rows = []
    today = datetime.now(KST).date().isoformat()

    for region in regions[:14]:
        latlon = WEATHER_COORDS.get(region)
        if not latlon:
            continue
        lat, lon = latlon

        try:
            weather_resp = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "daily": "weather_code,temperature_2m_max,temperature_2m_min,uv_index_max",
                    "timezone": "Asia/Seoul",
                    "forecast_days": 1,
                },
                timeout=12,
            )
            weather_resp.raise_for_status()
            wd = weather_resp.json().get("daily", {})
            code = (wd.get("weather_code") or [None])[0]
            tmax = (wd.get("temperature_2m_max") or [None])[0]
            tmin = (wd.get("temperature_2m_min") or [None])[0]
            uv = (wd.get("uv_index_max") or [None])[0]
        except Exception as exc:
            print(f"[weather] forecast failed {region}: {exc}")
            code, tmax, tmin, uv = None, None, None, None

        try:
            air_resp = requests.get(
                "https://air-quality-api.open-meteo.com/v1/air-quality",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "hourly": "pm2_5",
                    "timezone": "Asia/Seoul",
                    "forecast_days": 1,
                },
                timeout=12,
            )
            air_resp.raise_for_status()
            hourly = air_resp.json().get("hourly", {})
            times = hourly.get("time") or []
            pm_values = hourly.get("pm2_5") or []
            pm_today = [pm for t, pm in zip(times, pm_values) if str(t).startswith(today) and pm is not None]
            pm25 = sum(pm_today) / len(pm_today) if pm_today else None
        except Exception as exc:
            print(f"[weather] air failed {region}: {exc}")
            pm25 = None

        rows.append({
            "region": region,
            "weather": weather_code_label(code),
            "temp_min": round(tmin, 1) if isinstance(tmin, (int, float)) else None,
            "temp_max": round(tmax, 1) if isinstance(tmax, (int, float)) else None,
            "uv": round(uv, 1) if isinstance(uv, (int, float)) else None,
            "uv_label": uv_label(uv if isinstance(uv, (int, float)) else None),
            "pm25": round(pm25, 1) if isinstance(pm25, (int, float)) else None,
            "pm_label": pm_label(pm25 if isinstance(pm25, (int, float)) else None),
        })

    return rows


def choose_quote() -> dict[str, str]:
    q, author = random.choice(QUOTES)
    return {"text": q, "author": author}


def build_overnight_payload() -> dict[str, Any]:
    now = datetime.now(KST)
    us_news = collect_us_news()
    market = collect_us_market_summary()
    korea_news = collect_korea_news()
    keywords = collect_keywords()
    weather = collect_weather()
    quote = choose_quote()

    payload = {
        "title": "간밤의 핫이슈",
        "subtitle": "카테고리 무관",
        "generated_at": now.isoformat(),
        "publish_time_kst": "05:30",
        "us_news": us_news,
        "us_market": market,
        "korea_news": korea_news,
        "keywords": keywords,
        "weather": weather,
        "quote": quote,
    }
    return payload


def build_text_report(payload: dict[str, Any]) -> str:
    now = datetime.now(KST)
    lines = [
        f"{now:%Y년 %m월%d일}({weekday_ko(now)}) 🌙",
        "🌅 간밤의 핫이슈",
        "카테고리 무관 · 한국시각 05:30 기준",
        "",
    ]

    lines.append("🇺🇸 1. 미국뉴스 주요 이슈")
    for idx, issue in enumerate(payload.get("us_news", [])[:4], start=1):
        lines.append(f"{idx}) {issue.get('headline')}")
        for line in issue.get("summary_lines", [])[:2]:
            lines.append(f"   - {line}")
        if issue.get("insight"):
            lines.append(f"   인사이트: {issue.get('insight')}")
    lines.append("")

    lines.append("📈 2. 미증시 요약")
    market = payload.get("us_market") or {}
    lines.append(f"- {market.get('headline')}")
    for line in market.get("summary_lines", [])[:3]:
        lines.append(f"  · {line}")
    if market.get("indices"):
        index_line = " / ".join(
            f"{r['name']} {r['direction']} {abs(r['change_pct'])}%"
            for r in market.get("indices", [])[:5]
        )
        lines.append(f"  지표: {index_line}")
    if market.get("insight"):
        lines.append(f"  인사이트: {market.get('insight')}")
    lines.append("")

    lines.append("🇰🇷 3. 국내뉴스 아침 이슈")
    for idx, issue in enumerate(payload.get("korea_news", [])[:4], start=1):
        lines.append(f"{idx}) {issue.get('headline')}")
        for line in issue.get("summary_lines", [])[:2]:
            lines.append(f"   - {line}")
        if issue.get("insight"):
            lines.append(f"   인사이트: {issue.get('insight')}")
    lines.append("")

    lines.append("🔥 4. 간밤의 인기 키워드 & 트렌드")
    kw = payload.get("keywords") or {}
    if kw.get("popular_keywords"):
        lines.append("- " + " · ".join(kw.get("popular_keywords", [])[:12]))
    lines.append("")

    lines.append("⚡ 5. 실시간 급상승 키워드 순위")
    for idx, word in enumerate(kw.get("realtime_keywords", [])[:10], start=1):
        lines.append(f"{idx}. {word}")
    lines.append("")

    lines.append("🌤 6. 오늘의 지역별 날씨")
    for row in payload.get("weather", [])[:13]:
        temp = ""
        if row.get("temp_min") is not None and row.get("temp_max") is not None:
            temp = f"{row.get('temp_min')}~{row.get('temp_max')}℃"
        lines.append(
            f"- {row.get('region')}: {row.get('weather')} {temp} / "
            f"자외선 {row.get('uv_label')} / 미세먼지 {row.get('pm_label')}"
        )
    lines.append("")

    quote = payload.get("quote") or {}
    lines.append("📝 7. 오늘의 명언")
    lines.append(f"“{quote.get('text')}”")
    lines.append(f"- {quote.get('author')}")
    lines.append("")
    lines.append("gooddaynews.store")

    return "\n".join(lines).strip()
