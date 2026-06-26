import os
import re
import html
import feedparser
import pandas as pd
from datetime import datetime, timezone
from seo_utils import clean_text, score_keyword, is_blocked_keyword, is_valid_korean_keyword

GOOGLE_TRENDS_RSS = "https://trends.google.com/trending/rss?geo={geo}"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def fetch_google_trends_rss(geo: str = "KR", limit: int = 30) -> pd.DataFrame:
    """Google Trends Trending Now RSS를 best-effort로 읽습니다.
    Google이 RSS 형식을 바꾸면 실패할 수 있으므로 빈 DataFrame을 반환합니다.
    """
    try:
        feed = feedparser.parse(GOOGLE_TRENDS_RSS.format(geo=geo))
        rows = []
        for e in feed.entries[:limit]:
            title = clean_text(html.unescape(getattr(e, "title", "")))
            summary = clean_text(html.unescape(getattr(e, "summary", "")))
            approx = 0
            m = re.search(r"(\d[\d,]*)", summary)
            if m:
                approx = int(m.group(1).replace(",", ""))
            if title:
                rows.append({
                    "keyword": title,
                    "source": "google_trends_rss",
                    "approx_traffic": approx,
                    "collected_at": _utc_now(),
                })
        return pd.DataFrame(rows)
    except Exception as exc:
        print(f"[WARN] Google Trends RSS fetch failed: {exc}")
        return pd.DataFrame(columns=["keyword", "source", "approx_traffic", "collected_at"])


def load_seed_keywords(path: str = "data/seed_keywords.csv") -> pd.DataFrame:
    if not os.path.exists(path):
        return pd.DataFrame(columns=["keyword", "source", "approx_traffic", "collected_at"])
    df = pd.read_csv(path)
    if "keyword" not in df.columns:
        return pd.DataFrame(columns=["keyword", "source", "approx_traffic", "collected_at"])
    if "source" not in df.columns:
        df["source"] = "seed"
    if "approx_traffic" not in df.columns:
        df["approx_traffic"] = 0
    df["collected_at"] = _utc_now()
    return df[["keyword", "source", "approx_traffic", "collected_at"]]


def collect_keywords(geo: str = "KR", limit: int = 30, blocked_keywords: str = "") -> pd.DataFrame:
    allow_english = os.environ.get("ALLOW_ENGLISH_KEYWORDS", "false").lower() in {"1", "true", "yes", "y"}

    df = pd.concat([fetch_google_trends_rss(geo, limit), load_seed_keywords()], ignore_index=True)
    if df.empty:
        return df

    df["keyword"] = df["keyword"].map(clean_text)
    df = df[df["keyword"] != ""].drop_duplicates("keyword")
    df = df[~df["keyword"].map(lambda x: is_blocked_keyword(x, blocked_keywords))]
    df = df[df["keyword"].map(lambda x: is_valid_korean_keyword(x, allow_english=allow_english))]

    if df.empty:
        return df.reset_index(drop=True)

    df["score"] = df.apply(
        lambda r: score_keyword(r["keyword"], r.get("source", ""), int(r.get("approx_traffic") or 0)),
        axis=1,
    )
    return df.sort_values(["score", "approx_traffic"], ascending=False).head(limit).reset_index(drop=True)
