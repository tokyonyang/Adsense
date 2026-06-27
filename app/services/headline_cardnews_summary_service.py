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


def fallback_issue_summary(cluster: dict[str, Any], index: int) -> dict[str, Any]:
    articles = cluster.get("articles") or []
    rep = articles[0] if articles else {}
    title = clean_sentence(cluster.get("representative_title") or rep.get("title", ""), 54)
    category = cluster.get("category") or rep.get("category") or "주요"
    keywords = cluster.get("keywords") or []

    lines = []
    for article in articles[:3]:
        desc = clean_sentence(article.get("description") or article.get("title"), 70)
        if desc and desc not in lines:
            lines.append(desc)

    while len(lines) < 3:
        if len(lines) == 0:
            lines.append("같은 이슈를 다룬 복수 기사에서 공통 흐름이 확인됩니다.")
        elif len(lines) == 1:
            lines.append("핵심 쟁점은 정책·시장·사회적 영향으로 이어질 가능성입니다.")
        else:
            lines.append("후속 보도에서 세부 영향과 책임 소재를 확인할 필요가 있습니다.")

    links = []
    for article in articles[:3]:
        url = article.get("url") or ""
        if not url:
            continue
        links.append({
            "title": clean_sentence(article.get("title", ""), 42),
            "url": url,
            "domain": domain(url),
        })

    return {
        "rank": index,
        "category": category,
        "headline": title,
        "summary_lines": lines[:3],
        "insight": "중복 보도를 하나의 이슈로 묶어 핵심 흐름만 정리했습니다.",
        "keywords": [str(k) for k in keywords[:4]],
        "links": links[:3],
        "article_count": len(articles),
    }


def summarize_clusters_with_gemini(clusters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    각 클러스터를 카드뉴스용 이슈로 변환합니다.
    Gemini가 실패하면 기사 description 기반 fallback을 사용합니다.
    """
    if not clusters:
        return []

    api_key = env("GEMINI_API_KEY")
    fallback = [fallback_issue_summary(c, i + 1) for i, c in enumerate(clusters)]

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
        for idx, cluster in enumerate(clusters, start=1):
            payload.append({
                "rank": idx,
                "category": cluster.get("category"),
                "representative_title": cluster.get("representative_title"),
                "keywords": cluster.get("keywords", [])[:5],
                "articles": [
                    {
                        "title": a.get("title"),
                        "description": a.get("description"),
                        "domain": domain(a.get("url")),
                        "published_at": a.get("published_at").isoformat() if isinstance(a.get("published_at"), datetime) else str(a.get("published_at") or ""),
                    }
                    for a in (cluster.get("articles") or [])[:3]
                ],
            })

        prompt = f"""
아래는 오늘 아침 헤드라인 뉴스용으로 묶은 유사 기사 클러스터입니다.
각 클러스터는 같은 이슈를 다룬 기사 최대 3개입니다.

반드시 JSON 배열만 반환하세요.
각 원소는 다음 키를 포함하세요:
rank, category, headline, summary_lines, insight, keywords

작성 규칙:
- headline: 34자 이내. 자연스러운 한국어 완성형 제목.
- summary_lines: 정확히 3개. 각 36자 이내.
  1줄: 무슨 일이 있었는지
  2줄: 왜 중요한지 / 유사 기사 공통점
  3줄: 영향 또는 앞으로 볼 포인트
- insight: 34자 이내의 한줄 해석.
- keywords: 3~4개.
- 입력 기사에 없는 사실을 만들지 마세요.
- "세부 내용 확인 필요", "분야 주요 이슈", "후속 기사 확인 필요" 같은 상투 문구 금지.
- "...", "…", "外", "오늘의 주요뉴스" 금지.
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
        result = []
        fallback_by_rank = {x["rank"]: x for x in fallback}

        for row in rows:
            rank = int(row.get("rank") or len(result) + 1)
            fb = fallback_by_rank.get(rank, fallback[min(len(result), len(fallback) - 1)])

            headline = clean_sentence(row.get("headline") or fb["headline"], 42)
            if any(bad in headline for bad in ["...", "…", "外", "오늘의 주요뉴스"]):
                headline = fb["headline"]

            lines = []
            for line in row.get("summary_lines") or []:
                line = clean_sentence(line, 42)
                if line and line not in lines and not any(bad in line for bad in ["세부 내용 확인", "분야 주요", "후속 기사"]):
                    lines.append(line)

            if len(lines) < 3:
                lines = fb["summary_lines"]

            issue = {
                **fb,
                "rank": rank,
                "category": str(row.get("category") or fb["category"]),
                "headline": headline,
                "summary_lines": lines[:3],
                "insight": clean_sentence(row.get("insight") or fb["insight"], 42),
                "keywords": [str(k)[:12] for k in (row.get("keywords") or fb["keywords"])][:4],
            }
            result.append(issue)

        # 순서 안정화 및 누락 보충
        result.sort(key=lambda x: x["rank"])
        used = {x["rank"] for x in result}
        for fb in fallback:
            if fb["rank"] not in used:
                result.append(fb)
        result.sort(key=lambda x: x["rank"])
        return result[:len(clusters)]

    except Exception as exc:
        print("[cardnews gemini summary failed]", exc)
        return fallback
