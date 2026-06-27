from __future__ import annotations

import json
import os
import re
from datetime import datetime
from typing import Any
from urllib.parse import urlparse


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def clean_sentence(text: str, max_len: int = 88) -> str:
    text = str(text or "")
    text = text.replace("...", "…").replace("⋯", "…")
    for bad in ["세부 내용 확인 필요", "분야 주요 이슈", "후속 기사 확인 필요", "상세 내용은 본문 기사 확인 필요"]:
        text = text.replace(bad, "")
    text = re.sub(r"\s+", " ", text).strip(" -·ㆍ|")
    text = text.replace("…", " ")
    text = re.sub(r"\s+", " ", text).strip()

    if len(text) <= max_len:
        return text

    for sep in ["다.", "요.", "니다.", "된다.", "했다.", "이다.", "·", " - ", " | ", ":"]:
        pos = text.find(sep, 32)
        if 36 <= pos <= max_len:
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


def extract_keywords(text: str, limit: int = 5) -> list[str]:
    words = []
    stop = {"오늘", "뉴스", "속보", "종합", "관련", "주요", "헤드라인", "기사"}
    for token in re.findall(r"[가-힣A-Za-z0-9]{2,}", text or ""):
        if token in stop:
            continue
        if token not in words and len(token) <= 12:
            words.append(token)
        if len(words) >= limit:
            break
    return words


def infer_issue_title(anchor_title: str, articles: list[dict[str, Any]]) -> str:
    joined = " ".join([anchor_title] + [a.get("title", "") for a in articles])
    if "환율" in joined or "원달러" in joined or "달러" in joined:
        return "환율 변동성 확대"
    if "기준금리" in joined or "금리" in joined or "FOMC" in joined:
        return "기준금리 경로 재점검"
    if "유가" in joined or "원유" in joined or "석유" in joined:
        return "국제유가 변동성 확대"
    if "코스피" in joined or "증시" in joined or "주가" in joined:
        return "증시 변동성 확대"
    if "반도체" in joined or "하이닉스" in joined or "삼성전자" in joined or "엔비디아" in joined:
        return "AI 반도체 흐름 점검"
    if "전기요금" in joined or "가스요금" in joined or "공공요금" in joined or "물가" in joined:
        return "생활물가 부담 점검"
    return clean_sentence(anchor_title, 42)


def fallback_insight(title: str, category: str, articles: list[dict[str, Any]]) -> str:
    joined = " ".join([title] + [a.get("title", "") + " " + a.get("description", "") for a in articles])
    if any(k in joined for k in ["환율", "원달러", "달러", "원화"]):
        return "환율 상승은 수입물가와 외국인 자금 흐름을 흔들어 증시 변동성을 키울 수 있습니다."
    if any(k in joined for k in ["기준금리", "금리", "FOMC"]):
        return "금리 인상 기대가 커지면 달러 강세와 성장주 조정 압력이 함께 나타날 수 있습니다."
    if any(k in joined for k in ["유가", "원유", "석유"]):
        return "유가 상승은 시차를 두고 운송비와 공공요금 부담으로 번질 가능성이 있습니다."
    if any(k in joined for k in ["코스피", "증시", "주가", "차익실현"]):
        return "단기 급등 뒤 차익실현이 나오면 실적과 수급을 확인하는 장세로 바뀔 수 있습니다."
    if any(k in joined for k in ["반도체", "HBM", "하이닉스", "엔비디아"]):
        return "AI 수요 기대가 유지되더라도 밸류에이션 부담이 커지면 주가 변동성은 확대될 수 있습니다."
    if any(k in joined for k in ["물가", "공공요금", "전기요금", "가스요금", "할인"]):
        return "단기 물가 안정책은 체감 부담을 낮추지만 재정·공기업 부담은 후속 변수입니다."
    if category in {"국제", "국제·안전", "날씨·안전"}:
        return "해외 변수는 환율·유가·공급망을 통해 국내 물가와 증시에 파급될 수 있습니다."
    return "동일 이슈가 여러 매체에서 반복 보도돼 후속 영향과 정책 대응을 함께 볼 필요가 있습니다."


def fallback_issue_from_anchor_group(group: dict[str, Any]) -> dict[str, Any]:
    articles = group.get("articles") or []
    anchor = group.get("anchor") or {}
    anchor_title = group.get("anchor_title") or anchor.get("keyword") or anchor.get("title", "")
    category = group.get("category") or anchor.get("category") or "주요"

    title = infer_issue_title(anchor_title, articles)
    why = group.get("why_important") or anchor.get("why_important") or ""
    card_angle = group.get("card_angle") or anchor.get("card_angle") or ""

    lines = []
    for article in articles[:3]:
        desc = clean_sentence(article.get("description") or article.get("title"), 58)
        if desc and desc not in lines:
            lines.append(desc)

    if why and len(lines) < 3:
        lines.append(clean_sentence(why, 58))
    if card_angle and len(lines) < 3:
        lines.append(clean_sentence(card_angle, 58))

    while len(lines) < 3:
        if len(lines) == 0:
            lines.append("복수 기사에서 같은 이슈가 반복 보도되고 있습니다.")
        elif len(lines) == 1:
            lines.append("핵심은 원인보다 시장·생활 영향이 어디까지 번지는지입니다.")
        else:
            lines.append("후속 변수는 정책 대응과 시장 반응에서 확인해야 합니다.")

    links = []
    for article in articles[:3]:
        url = article.get("url") or ""
        if not url:
            continue
        links.append({
            "title": clean_sentence(article.get("title", ""), 46),
            "url": url,
            "domain": domain(url),
        })

    keyword_text = " ".join([anchor_title, category] + lines)
    keywords = group.get("keywords") or extract_keywords(keyword_text, 5)

    return {
        "rank": group.get("rank"),
        "category": category,
        "headline": title,
        "summary_lines": lines[:3],
        "insight": fallback_insight(title, category, articles),
        "keywords": [str(k) for k in keywords[:5]],
        "links": links[:3],
        "article_count": len(articles),
        "anchor_title": anchor_title,
        "why_important": why,
        "card_angle": card_angle,
    }


def summarize_anchor_groups_with_gemini(groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    v1.29:
    - 키워드 그대로 제목으로 쓰지 않음
    - 기사 3개의 공통 쟁점을 새로운 이슈 제목으로 생성
    - 한줄 인사이트는 기사 흐름, 시장 영향, 과거 유사 국면의 일반적 패턴을 바탕으로 생성
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
            anchor = group.get("anchor") or {}
            payload.append({
                "rank": group.get("rank"),
                "category": group.get("category"),
                "slot": group.get("slot"),
                "anchor_title": group.get("anchor_title"),
                "why_important": group.get("why_important") or anchor.get("why_important"),
                "card_angle": group.get("card_angle") or anchor.get("card_angle"),
                "score": group.get("score"),
                "editorial_score": group.get("editorial_score"),
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
아래 입력은 Daily Hot Issue 편집 엔진에서 선별한 카드뉴스 후보입니다.
각 항목에는 같은 이슈를 다룬 기사 최대 3개가 들어 있습니다.

반드시 JSON 배열만 반환하세요.
각 원소는 rank, category, headline, summary_lines, insight, keywords 키를 포함하세요.

중요 작성 규칙:
1. headline은 anchor_title을 그대로 쓰지 말고, 기사 3개의 공통 쟁점을 24~38자 이내의 '주요 이슈 제목'으로 재작성하세요.
   예: '환율' → '환율 변동성 확대, 물가·증시 부담 재부각'
2. summary_lines는 정확히 3개입니다.
   - 1줄: 기사들이 공통으로 말하는 현재 상황
   - 2줄: 왜 중요한지, 어떤 시장/생활/정책 영향이 있는지
   - 3줄: 앞으로 볼 변수 또는 후속 전망
3. insight는 36~58자 한 문장입니다.
   - 단순 요약 금지
   - 기사 흐름을 바탕으로 향후 전망, 시장 영향, 과거 유사 국면에서 흔히 나타난 패턴을 반영하세요.
   - 환율: 수입물가, 외국인 자금, 증시 변동성, 국민연금/수급 같은 관점 가능
   - 금리: 달러 강세, 성장주 조정, 대출 부담, 채권금리 관점 가능
   - 유가: 운송비, 물가, 정유/항공/소비 영향 가능
   - 증시: 차익실현, 수급, 실적 확인 장세 가능
   - 산업/기업: 실적, 공급망, 밸류에이션, 경쟁구도 가능
4. 입력 기사에 없는 구체적 숫자나 사건은 만들지 마세요.
5. 그러나 경제적으로 일반적으로 관찰되는 인과관계는 신중하게 활용해도 됩니다.
6. 아래 문구는 절대 쓰지 마세요.
   - 헤드라인 목록을 기준으로 관련 기사 3건을 묶었습니다
   - 관련 기사 3건을 묶었습니다
   - 세부 내용 확인 필요
   - 분야 주요 이슈
   - 후속 기사 확인 필요
7. "...", "…", "外", "오늘의 주요뉴스" 금지.
8. 한국어만 사용. 마크다운 금지.

입력:
{json.dumps(payload, ensure_ascii=False)}
"""
        response = model.generate_content(prompt)
        text = response.text.strip()
        match = re.search(r"\[.*\]", text, re.S)
        if not match:
            return fallback

        rows = json.loads(match.group(0))
        fb_by_rank = {int(x["rank"]): x for x in fallback if x.get("rank") is not None}
        result = []

        for row in rows:
            rank = int(row.get("rank") or 0)
            fb = fb_by_rank.get(rank)
            if not fb:
                continue

            headline = clean_sentence(row.get("headline") or fb["headline"], 48)
            bad_headline = any(bad in headline for bad in ["...", "…", "外", "오늘의 주요뉴스", "헤드라인 목록"])
            if bad_headline:
                headline = fb["headline"]

            lines = []
            for line in row.get("summary_lines") or []:
                line = clean_sentence(line, 62)
                if not line:
                    continue
                if any(bad in line for bad in ["세부 내용 확인", "분야 주요", "후속 기사", "헤드라인 목록"]):
                    continue
                if line not in lines:
                    lines.append(line)

            if len(lines) < 3:
                lines = fb["summary_lines"]

            insight = clean_sentence(row.get("insight") or fb["insight"], 68)
            if any(bad in insight for bad in ["헤드라인 목록", "관련 기사", "묶었습니다", "확인 필요", "정리했습니다"]):
                insight = fb["insight"]

            result.append({
                **fb,
                "rank": rank,
                "category": str(row.get("category") or fb["category"]),
                "headline": headline,
                "summary_lines": lines[:3],
                "insight": insight,
                "keywords": [str(k)[:14] for k in (row.get("keywords") or fb["keywords"])][:5],
            })

        used = {int(x["rank"]) for x in result}
        for fb in fallback:
            if int(fb["rank"]) not in used:
                result.append(fb)

        result.sort(key=lambda x: int(x["rank"]))
        return result[:len(groups)]

    except Exception as exc:
        print("[anchor summary gemini failed]", exc)
        return fallback
