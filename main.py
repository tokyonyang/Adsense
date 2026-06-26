import os
import argparse
import json
import re
import html as html_lib
from pathlib import Path
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
from bs4 import BeautifulSoup

from trend_sources import collect_keywords
from content_generator import generate_article
from wp_publisher import create_wp_post
from telegram_notify import send_telegram, send_telegram_long, html_escape
from news_sources import fetch_related_news


def _env_true(name: str, default: str = "false") -> bool:
    return os.environ.get(name, default).strip().lower() in {"1", "true", "yes", "y", "on"}


def _short_error(exc: Exception, max_len: int = 240) -> str:
    text = str(exc).replace("\\n", " ").replace("\n", " ").strip()
    return text[:max_len] + ("..." if len(text) > max_len else "")


def _parse_topics(text: str) -> list[str]:
    """GitHub Actions 수동 입력값에서 선택 주제를 추출합니다.

    쉼표, 줄바꿈, 세미콜론으로 구분합니다. 공백만으로는 나누지 않습니다.
    """
    text = str(text or "").strip()
    if not text:
        return []
    parts = re.split(r"[\n,;，、]+", text)
    topics = []
    seen = set()
    for part in parts:
        item = re.sub(r"\s+", " ", part).strip(" -•\t")
        if item and item not in seen:
            seen.add(item)
            topics.append(item)
    return topics


def _article_to_plain_text(article: dict) -> str:
    """WordPress HTML 초안을 텔레그램에서 읽기 쉬운 plain text로 변환합니다."""
    html = article.get("html") or ""
    soup = BeautifulSoup(html, "html.parser")

    # 제목형 태그 앞뒤에 여백을 넣어 가독성을 높입니다.
    for tag in soup.find_all(["h1", "h2", "h3"]):
        tag.insert_before("\n\n")
        tag.insert_after("\n")
    for tag in soup.find_all(["p", "li", "tr"]):
        tag.insert_after("\n")

    body = soup.get_text("\n", strip=True)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()

    tags = article.get("tags") if isinstance(article.get("tags"), list) else []
    tag_text = ", ".join(str(t) for t in tags[:8])

    lines = [
        "📝 AdSense SEO 글 초안",
        f"주제: {article.get('keyword') or ''}",
        f"제목: {article.get('title') or '제목 없음'}",
    ]
    if article.get("meta_description"):
        lines.append(f"메타설명: {article.get('meta_description')}")
    if tag_text:
        lines.append(f"태그: {tag_text}")
    lines.append("\n본문")
    lines.append(body or "본문 생성 결과가 비어 있습니다.")
    return "\n".join(lines)


def _keyword_dataframe_from_topics(topics: list[str]) -> pd.DataFrame:
    return pd.DataFrame([{"keyword": topic, "source": "manual"} for topic in topics])


def _safe_int_env(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, str(default)))
    except Exception:
        return default


def _build_item_angle(keyword: str) -> str:
    """글을 바로 작성하지 않고, 사람이 판단하기 좋은 작성 방향만 짧게 제안합니다."""
    k = str(keyword or "")
    if any(word in k for word in ["지원금", "신청", "환급", "보조금"]):
        return "대상·신청기간·필요서류·주의사항 중심의 실용형 정리"
    if any(word in k for word in ["전기요금", "가스요금", "난방비", "절약", "요금"]):
        return "가정에서 바로 적용 가능한 절약 방법과 요금제 확인 포인트"
    if any(word in k for word in ["대학", "입시", "모집", "수능", "교육"]):
        return "일정·대상·변경사항·체크리스트 중심의 정보형 글"
    if any(word in k for word in ["장마", "폭염", "태풍", "날씨", "폭우"]):
        return "대비 체크리스트·피해 예방·생활 안전 수칙 중심"
    if any(word in k for word in ["부동산", "청약", "주택", "전세", "월세"]):
        return "자격·일정·비용·리스크를 분리한 생활경제형 정리"
    return "이슈 배경 → 왜 관심이 커졌는지 → 독자가 확인할 것 순서로 정리"


def _build_idea_digest(keywords: pd.DataFrame, max_items: int, links_per_topic: int, geo: str) -> list[dict]:
    items = []
    for _, row in keywords.head(max_items).iterrows():
        keyword = str(row.get("keyword", "")).strip()
        if not keyword:
            continue
        news = fetch_related_news(keyword, limit=links_per_topic, geo=geo)
        items.append({
            "keyword": keyword,
            "source": str(row.get("source", "")),
            "approx_traffic": int(row.get("approx_traffic") or 0) if str(row.get("approx_traffic", "")).isdigit() else row.get("approx_traffic", 0),
            "angle": _build_item_angle(keyword),
            "news": news,
        })
    return items


def _html_attr(text: str) -> str:
    """HTML 링크 속성에 넣을 값을 안전하게 이스케이프합니다."""
    return html_lib.escape(str(text or ""), quote=True)


def _ideas_to_telegram_text(items: list[dict]) -> str:
    """텔레그램용 작성 후보 리포트를 생성합니다.

    기사 URL 전체를 노출하지 않고 <a href="...">링크1</a> 형태의
    클릭 가능한 라벨로만 표시합니다.
    """
    lines = [
        "🧭 <b>AdSense 작성 후보 아이템 리포트</b>",
        "글 초안은 생성하지 않았습니다. 선별용 주제와 관련 기사 링크만 정리했습니다.",
    ]
    if not items:
        lines.append("\n수집된 작성 후보가 없습니다. 트렌드 수집 또는 선택 주제를 확인해주세요.")
        return "\n".join(lines)

    for i, item in enumerate(items, 1):
        keyword = html_escape(item.get("keyword") or "")
        angle = html_escape(item.get("angle") or "")
        source = html_escape(item.get("source") or "")
        lines.append(f"\n<b>{i}. {keyword}</b>")
        if source:
            lines.append(f"수집경로: {source}")
        if angle:
            lines.append(f"작성각도: {angle}")
        news = item.get("news") or []
        if news:
            lines.append("관련 기사:")
            for n, article in enumerate(news, 1):
                title = html_escape(article.get("title") or "기사 제목 없음")
                media = html_escape(article.get("source") or "")
                published = html_escape(article.get("published") or "")
                url = str(article.get("url") or "").strip()
                meta = " · ".join(x for x in [media, published] if x)
                link_label = f"링크{n}"
                if url.startswith(("http://", "https://")):
                    link_text = f'<a href="{_html_attr(url)}">{link_label}</a>'
                else:
                    link_text = link_label

                if meta:
                    lines.append(f"  {n}) {title} ({meta}) / {link_text}")
                else:
                    lines.append(f"  {n}) {title} / {link_text}")
        else:
            lines.append("관련 기사: 최근 7일 기준 RSS에서 확인된 링크가 없습니다.")
    return "\n".join(lines)


def main():
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--geo", default=os.environ.get("GOOGLE_TRENDS_GEO", "KR"))
    parser.add_argument("--max-keywords", type=int, default=int(os.environ.get("MAX_KEYWORDS", "30")))
    parser.add_argument("--max-posts", type=int, default=int(os.environ.get("MAX_POSTS_PER_RUN", "10")))
    parser.add_argument("--topics", default=os.environ.get("SELECTED_TOPICS", ""))
    parser.add_argument("--no-wordpress", action="store_true")
    parser.add_argument("--send-articles-to-telegram", action="store_true")
    parser.add_argument("--list-only", action="store_true", help="글 초안 생성 없이 작성 후보와 관련 기사 링크만 텔레그램으로 전송")
    args = parser.parse_args()

    # 운영 기본값: GitHub Actions 워크플로우가 아직 예전 값(10/3)을 넘기더라도
    # 요청한 운영 기준인 30개 키워드 / 10개 포스팅으로 보정합니다.
    # 더 작은 값으로 테스트하고 싶을 때만 ALLOW_SMALLER_LIMITS=true를 사용하세요.
    if not _env_true("ALLOW_SMALLER_LIMITS"):
        args.max_keywords = max(args.max_keywords, 30)
        args.max_posts = max(args.max_posts, 10)

    telegram_only = _env_true("TELEGRAM_ONLY") or args.no_wordpress
    send_articles_to_telegram = (
        _env_true("SEND_ARTICLES_TO_TELEGRAM")
        or args.send_articles_to_telegram
        or telegram_only
    )
    # 기본 운영은 "후보 리스트만 전송"입니다. 글 초안 생성/워드프레스 업로드는 필요할 때만 끕니다.
    list_only = _env_true("ITEM_LIST_ONLY", "true") or args.list_only
    links_per_topic = max(1, _safe_int_env("NEWS_LINKS_PER_TOPIC", 5))

    topics = _parse_topics(args.topics)

    Path("reports").mkdir(exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")

    if topics:
        keywords = _keyword_dataframe_from_topics(topics).head(args.max_keywords)
    else:
        keywords = collect_keywords(args.geo, args.max_keywords)

    keywords.to_csv(f"reports/trend_keywords_{today}.csv", index=False, encoding="utf-8-sig")

    if list_only:
        items = _build_idea_digest(keywords, args.max_posts, links_per_topic, args.geo)
        Path(f"reports/idea_items_{today}.json").write_text(
            json.dumps(items, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        flat_rows = []
        for item in items:
            news = item.get("news") or []
            flat_rows.append({
                "keyword": item.get("keyword", ""),
                "source": item.get("source", ""),
                "angle": item.get("angle", ""),
                "news_count": len(news),
                "news_links": " | ".join(n.get("url", "") for n in news),
            })
        pd.DataFrame(flat_rows).to_csv(f"reports/idea_items_{today}.csv", index=False, encoding="utf-8-sig")
        send_telegram_long(_ideas_to_telegram_text(items), parse_mode="HTML")
        return

    results = []
    for _, row in keywords.head(args.max_posts).iterrows():
        keyword = row["keyword"]
        article = None
        try:
            article = generate_article(keyword, os.environ.get("SITE_DESCRIPTION", "생활 정보 블로그"))
            Path(f"reports/article_{today}_{len(results) + 1}.json").write_text(
                json.dumps(article, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            wp_result = {}
            if not telegram_only:
                wp_result = create_wp_post(article, status=os.environ.get("WP_DEFAULT_STATUS", "draft"))

            results.append({
                "keyword": keyword,
                "title": article.get("title"),
                "status": "telegram_only" if telegram_only else "draft",
                "wp_link": wp_result.get("link", ""),
                "review_checklist": " | ".join(article.get("review_checklist", [])),
            })

            if send_articles_to_telegram:
                send_telegram_long(_article_to_plain_text(article), parse_mode=None)

        except Exception as exc:
            print(f"[ERROR] {keyword}: {exc}")
            item = {"keyword": keyword, "error": _short_error(exc)}
            if article:
                item["title"] = article.get("title")
                item["status"] = "generated_wp_failed"
                # WordPress 업로드만 실패해도 생성된 글은 텔레그램으로 확인할 수 있게 보냅니다.
                if send_articles_to_telegram or _env_true("SEND_ARTICLE_ON_WP_FAIL", "true"):
                    send_telegram_long(_article_to_plain_text(article), parse_mode=None)
            results.append(item)

    pd.DataFrame(results).to_csv(f"reports/generated_posts_{today}.csv", index=False, encoding="utf-8-sig")

    lines = ["📝 <b>AdSense SEO 초안 생성 리포트</b>"]
    if telegram_only:
        lines.append("모드: 텔레그램 전용 생성 / WordPress 업로드 생략")
    elif topics:
        lines.append("모드: 선택 주제 생성")

    if not results:
        lines.append("생성할 수 있는 키워드가 없습니다. 선택 주제 또는 트렌드 수집 설정을 확인해주세요.")

    for i, r in enumerate(results, 1):
        if r.get("error"):
            title = r.get("title")
            title_line = f"\n생성제목: {html_escape(title)}" if title else ""
            lines.append(f"{i}. ❌ {html_escape(r['keyword'])}{title_line}\n오류: {html_escape(r['error'])}")
        else:
            title = html_escape(r.get("title") or "제목 없음")
            keyword = html_escape(r.get("keyword") or "")
            link = html_escape(r.get("wp_link") or "텔레그램 전송 완료" if telegram_only else "(로컬 저장)")
            lines.append(f"{i}. ✅ <b>{title}</b>\n키워드: {keyword}\n{link}")

    send_telegram("\n\n".join(lines), parse_mode="HTML")


if __name__ == "__main__":
    main()
