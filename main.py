import os
import argparse
import json
import re
from pathlib import Path
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
from bs4 import BeautifulSoup

from trend_sources import collect_keywords
from content_generator import generate_article
from wp_publisher import create_wp_post
from telegram_notify import send_telegram, send_telegram_long, html_escape


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


def main():
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--geo", default=os.environ.get("GOOGLE_TRENDS_GEO", "KR"))
    parser.add_argument("--max-keywords", type=int, default=int(os.environ.get("MAX_KEYWORDS", "30")))
    parser.add_argument("--max-posts", type=int, default=int(os.environ.get("MAX_POSTS_PER_RUN", "10")))
    parser.add_argument("--topics", default=os.environ.get("SELECTED_TOPICS", ""))
    parser.add_argument("--no-wordpress", action="store_true")
    parser.add_argument("--send-articles-to-telegram", action="store_true")
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

    topics = _parse_topics(args.topics)

    Path("reports").mkdir(exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")

    if topics:
        keywords = _keyword_dataframe_from_topics(topics).head(args.max_keywords)
    else:
        keywords = collect_keywords(args.geo, args.max_keywords)

    keywords.to_csv(f"reports/trend_keywords_{today}.csv", index=False, encoding="utf-8-sig")

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
