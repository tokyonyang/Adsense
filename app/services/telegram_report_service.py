from __future__ import annotations

import html
import os
from typing import Any

import requests


TELEGRAM_API_BASE = "https://api.telegram.org/bot"


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def escape_html(value: Any) -> str:
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def split_telegram_message(text: str, max_length: int = 3900) -> list[str]:
    if len(text) <= max_length:
        return [text]

    chunks: list[str] = []
    current = ""

    for block in text.split("\n\n"):
        candidate = f"{current}\n\n{block}".strip() if current else block
        if len(candidate) > max_length:
            if current:
                chunks.append(current)
            current = block
        else:
            current = candidate

    if current:
        chunks.append(current)

    return chunks


def send_telegram_message(
    message: str,
    *,
    bot_token: str | None = None,
    chat_id: str | None = None,
    parse_mode: str = "HTML",
    disable_web_page_preview: bool = True,
    fail_silently: bool = True,
) -> dict[str, Any]:
    bot_token = bot_token or _env("TELEGRAM_BOT_TOKEN")
    chat_id = chat_id or _env("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        result = {
            "ok": False,
            "skipped": True,
            "reason": "TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID가 없습니다.",
        }
        if fail_silently:
            return result
        raise RuntimeError(result["reason"])

    url = f"{TELEGRAM_API_BASE}{bot_token}/sendMessage"
    results = []

    for chunk in split_telegram_message(message):
        payload = {
            "chat_id": chat_id,
            "text": chunk,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
        }
        response = requests.post(url, json=payload, timeout=30)

        try:
            data = response.json()
        except Exception:
            data = {"ok": False, "description": response.text}

        if not response.ok or not data.get("ok"):
            if fail_silently:
                return {
                    "ok": False,
                    "skipped": False,
                    "reason": data,
                    "sent_parts": len(results),
                }
            raise RuntimeError(f"Telegram 전송 실패: {data}")

        results.append(data)

    return {"ok": True, "sent_parts": len(results), "results": results}


def _level_label(level: str | None) -> str:
    level = str(level or "normal").lower()
    if level == "critical":
        return "🔴 critical · 최우선 검색"
    if level == "high":
        return "🟠 high · 검색 강화"
    return "🟢 normal · 기본 수집"


def format_event_boost_section(boost: dict[str, Any] | None) -> str:
    boost = boost or {}
    enabled = bool(boost.get("enabled"))
    level = str(boost.get("level") or "normal")
    keywords = boost.get("event_keywords") or []
    events = boost.get("events") or []

    lines = [
        "<b>📊 경제지표 검색 강화 상태</b>",
        f"- 상태: <b>{escape_html(_level_label(level))}</b>",
        f"- 검색 강화 적용: {'예' if enabled else '아니오'}",
        f"- 키워드 수집량: <b>{escape_html(boost.get('max_keywords', 30))}개</b>",
        f"- 근거자료 수집량: <b>이슈당 {escape_html(boost.get('news_links_per_topic', 5))}개</b>",
        f"- 조회 기간: 최근 <b>{escape_html(boost.get('lookback_hours', 24))}시간</b>",
    ]

    if keywords:
        display_keywords = ", ".join(str(k) for k in keywords[:15])
        lines.append(f"- 강화 검색어: {escape_html(display_keywords)}")
    else:
        lines.append("- 강화 검색어: 없음")

    if events:
        lines.append("")
        lines.append("<b>주요 경제지표</b>")
        for idx, event in enumerate(events[:5], start=1):
            date = event.get("event_date") or "-"
            time = str(event.get("event_time") or "")[:5] or "-"
            country = event.get("country") or "-"
            name = event.get("event_name") or "-"
            importance = event.get("importance") or "-"
            merged = int(event.get("_merged_count") or 1)
            merged_text = f" · 중복 {merged}건 병합" if merged > 1 else ""
            lines.append(
                f"{idx}) {escape_html(date)} {escape_html(time)} · "
                f"{escape_html(country)} · {escape_html(name)} "
                f"({escape_html(importance)}){escape_html(merged_text)}"
            )

    return "\n".join(lines)


def format_pipeline_summary_report(
    *,
    boost: dict[str, Any] | None,
    keyword_result: dict[str, Any] | None,
    sns_result: dict[str, Any] | None,
) -> str:
    boost = boost or {}
    keyword_result = keyword_result or {}
    sns_result = sns_result or {}

    lines = [
        "<b>🤖 AdSense SEO 자동 수집 리포트</b>",
        "",
        format_event_boost_section(boost),
        "",
        "<b>🔍 키워드 수집 결과</b>",
        f"- 저장 키워드: <b>{escape_html(keyword_result.get('inserted', 0))}건</b>",
        f"- 적용 MAX_KEYWORDS: {escape_html(keyword_result.get('max_keywords', boost.get('max_keywords', 30)))}",
        f"- 적용 NEWS_LINKS_PER_TOPIC: {escape_html(keyword_result.get('news_links_per_topic', boost.get('news_links_per_topic', 5)))}",
        f"- 경제지표 강화 키워드 수: {escape_html(keyword_result.get('seed_keywords_count', len(boost.get('event_keywords') or [])))}",
        "",
        "<b>📱 SNS 트렌드 수집 결과</b>",
        f"- 저장 트렌드: <b>{escape_html(sns_result.get('inserted', 0))}건</b>",
        "",
        "—",
        "※ 경제·금융 이슈는 발행 전 공식 자료 확인이 필요합니다.",
    ]

    return "\n".join(lines).strip()


def send_pipeline_summary_report(
    *,
    boost: dict[str, Any] | None,
    keyword_result: dict[str, Any] | None,
    sns_result: dict[str, Any] | None,
) -> dict[str, Any]:
    message = format_pipeline_summary_report(
        boost=boost,
        keyword_result=keyword_result,
        sns_result=sns_result,
    )
    return send_telegram_message(message, fail_silently=True)
