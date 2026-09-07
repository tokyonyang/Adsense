"""주제 1개를 받아 디깅스팟 글을 생성하고 Blogger에 발행하는 오케스트레이터.

발행 빈도 가드(주 2편, 같은 날 중복 금지)는 로컬 상태 파일 없이 Blogger API에서
최근 글 목록을 직접 조회해 판단합니다 (Cowork 등 다른 경로로 올라간 글도 함께 카운트됨).
"""

import os
from datetime import datetime, timedelta, timezone

from blogger_publisher import create_blogger_post, list_recent_posts
from diggingspot_content import generate_diggingspot_article

KST = timezone(timedelta(hours=9))


def _env_true(name: str, default: str = "false") -> bool:
    return os.environ.get(name, default).strip().lower() in {"1", "true", "yes", "y", "on"}


def _kst_now() -> datetime:
    return datetime.now(KST)


def _parse_published(value: str):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(KST)
    except Exception:
        return None


def _recent_publish_status(days: int = 7):
    posts = list_recent_posts(max_results=15)
    cutoff = _kst_now() - timedelta(days=days)
    count = 0
    last_date = None
    for post in posts:
        dt = _parse_published(post.get("published", ""))
        if not dt:
            continue
        if dt >= cutoff:
            count += 1
        if last_date is None or dt > last_date:
            last_date = dt
    return count, (last_date.strftime("%Y-%m-%d") if last_date else None)


def publish_diggingspot_topic(topic: str, force: bool = False) -> dict:
    topic = (topic or "").strip()
    if not topic:
        raise ValueError("topic이 비어 있습니다.")

    weekly_limit = int(os.environ.get("DIGGINGSPOT_WEEKLY_LIMIT", "2"))
    block_same_day = _env_true("DIGGINGSPOT_BLOCK_SAME_DAY", "true")

    if not force:
        count, last_date = _recent_publish_status(days=7)
        today = _kst_now().strftime("%Y-%m-%d")
        if block_same_day and last_date == today:
            return {"published": False, "reason": f"오늘({today}) 이미 발행한 글이 있어 중복 발행을 건너뜁니다."}
        if count >= weekly_limit:
            return {
                "published": False,
                "reason": f"최근 7일간 {count}편이 발행되어 주 {weekly_limit}편 기준을 넘습니다. 다음 주기까지 대기합니다.",
            }

    article = generate_diggingspot_article(topic)
    result = create_blogger_post(article)
    return {
        "published": True,
        "article": article,
        "post_url": result.get("url"),
        "post_id": result.get("id"),
    }
