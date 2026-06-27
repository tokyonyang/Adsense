from __future__ import annotations

import json
import os
import re
from datetime import datetime
from typing import Any
from urllib.parse import urlparse


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def clean_sentence(text: str, max_len: int = 74) -> str:
    text = str(text or "")
    text = text.replace("...", "…").replace("⋯", "…")
    text = text.replace("세부 내용 확인 필요", "").replace("분야 주요 이슈", "")
    text = re.sub(r"\s+", " ", text).strip(" -·ㆍ|")
    text = text.replace("…", " ")
    text = re.sub(r"\s+", " ", text).strip()

    if len(text) <= max_len:
        return text

    for sep in ["다.", "요.", "니다.", "·", " - ", " | ", ":"]:
        pos = text.find(sep, 30)
        if 34 <= pos <= max_len:
            return text[:pos + len(sep)].strip()

    return text[: max_len - 1].rstrip() + "…"


def domain(url: str | None) -> str:
    if not url:
        return "news"
    try:
        host = urlparse(url).netloc or urlparse(url).path
        return host.replace("www.", "")[:32] or "news"
    except Exception:
        return "news"


def extract_keywords(text: str, limit: int = 4) -> list[str]:
    words = []
    for token in re.findall(r"[가-힣A-Za-z0-9]{2,}", text or ""):
        if token in ["오늘", "뉴스", "속보", "종합", "관련", "주요"]:
            continue
        if token not in words and len(token) <= 12:
            words.append(token)
        if len(words) >= limit:
            break
    return words


def fallback_issue_from_anchor_group(group: dict[str, Any]) -> dict[str, Any]:
    articles = group.get("articles") or []
    anchor = group.get("anchor") or {}
    title = clean_sentence(group.get("anchor_title") or anchor.get("title", ""), 54)
    category = group.get("category") or anchor.get("category") or "주요"

    lines = []
    for article in articles[:3]:
        desc = clean_sentence(article.get("description") or article.get("title"), 48)
        if desc and desc not in lines:
            lines.append(desc)

    while len(lines) < 3:
        if len(lines) == 0:
            lines.append("관련 기사들이 같은 이슈를 반복 보도하고 있습니다.")
        elif len(lines) == 1:
            lines.append("핵심 쟁점은 기사 제목과 설명에서 공통적으로 확인됩니다.")
        else:
            lines.append("후속 흐름은 원문 기사에서 추가 확인이 필요합니다.")

    links = []
    for article in articles[:3]:
        url = article.get("url") or ""
        if not url:
            continue
        links.append({
            "title": clean_sentence(article.get("title", ""), 44),
            "url": url,
            "domain": domain(url),
        })

    keywords = group.get("keywords") or extract_keywords(title + " " + " ".join(lines), 4)

    return {
        "rank": group.get("rank"),
        "category": category,
        "headline": title,
        "summary_lines": lines[:3],
        "insight": "헤드라인 목록을 기준으로 관련 기사 3건을 묶었습니다.",
        "keywords": [str(k) for k in keywords[:4]],
        "links": links[:3],
        "article_count": len(articles),
        "anchor_title": title,
    }


def summarize_anchor_groups_with_gemini(groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    v1.24:
    독립 클러스터가 아니라 '헤드라인 뉴스 List(anchor)' 기반으로 요약합니다.
    """
    if not groups:
        return []

    fallback = [fallback_issue_from_anchor_group(g) for g in groups]
    api_key = env("GEMINI_API_KEY")
    if not api_key:
        return fallback

    try:
        import google.generativeai as genai
    except Exception:
        return fallback

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        payload = []
        for group in groups:
            payload.append({
                "rank": group.get("rank"),
                "category": group.get("category"),
                "anchor_title": group.get("anchor_title"),
                "articles": [
                    {
                        "title": a.get("title"),
                        "description": a.get("description"),
                        "domain": domain(a.get("url")),
                        "published_at": a.get("published_at").isoformat() if isinstance(a.get("published_at"), datetime) else str(a.get("published_at") or ""),
                    }
                    for a in (group.get("articles") or [])[:3]
                ],
            })

        prompt = f"""
아래 입력은 이미 선정된 '아침 헤드라인 뉴스 List'입니다.
각 항목의 anchor_title은 반드시 카드뉴스의 기준 제목입니다.
절대 새로운 이슈를 추가하거나, anchor_title과 다른 주제로 바꾸지 마세요.

반드시 JSON 배열만 반환하세요.
각 원소는 rank, category, headline, summary_lines, insight, keywords 키를 포함하세요.

작성 규칙:
- rank는 입력 rank와 동일.
- headline은 anchor_title의 의미를 유지하되 36자 이내로 자연스럽게 정리.
- summary_lines는 정확히 3개.
  1줄: anchor_title 기준으로 무슨 일이 있었는지
  2줄: 유사 기사 3건에서 공통으로 다루는 쟁점
  3줄: 영향 또는 앞으로 볼 포인트
- summary_lines는 입력 articles의 title/description에 근거해야 함.
- 입력에 없는 사실을 만들지 마세요.
- "세부 내용 확인 필요", "분야 주요 이슈", "후속 기사 확인 필요" 금지.
- "...", "…", "外", "오늘의 주요뉴스" 금지.
- insight는 34자 이내.
- keywords는 3~4개.
- 한국어만 사용.
- 마크다운 금지.

입력:
{json.dumps(payload, ensure_ascii=False)}
"""
        response = model.generate_content(prompt)
        text = response.text.strip()
        match = re.search(r"\[.*\]", text, re.S)
        if not match:
            return fallback

        rows = json.loads(match.group(0))
        fb_by_rank = {int(x["rank"]): x for x in fallback}
        result = []

        for row in rows:
            rank = int(row.get("rank") or 0)
            fb = fb_by_rank.get(rank)
            if not fb:
                continue

            headline = clean_sentence(row.get("headline") or fb["headline"], 42)
            if any(bad in headline for bad in ["...", "…", "外", "오늘의 주요뉴스"]):
                headline = fb["headline"]

            lines = []
            for line in row.get("summary_lines") or []:
                line = clean_sentence(line, 48)
                if not line:
                    continue
                if any(bad in line for bad in ["세부 내용 확인", "분야 주요", "후속 기사"]):
                    continue
                if line not in lines:
                    lines.append(line)

            if len(lines) < 3:
                lines = fb["summary_lines"]

            result.append({
                **fb,
                "rank": rank,
                "category": str(row.get("category") or fb["category"]),
                "headline": headline,
                "summary_lines": lines[:3],
                "insight": clean_sentence(row.get("insight") or fb["insight"], 42),
                "keywords": [str(k)[:12] for k in (row.get("keywords") or fb["keywords"])][:4],
            })

        # 누락 보충
        used = {int(x["rank"]) for x in result}
        for fb in fallback:
            if int(fb["rank"]) not in used:
                result.append(fb)

        result.sort(key=lambda x: int(x["rank"]))
        return result[:len(groups)]

    except Exception as exc:
        print("[anchor summary gemini failed]", exc)
        return fallback
