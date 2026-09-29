"""디깅스팟 전용 글 생성 모듈.

content_generator.py의 Gemini 호출/파싱 로직을 재사용하되, 프롬프트와 라벨 규칙만
diggingspot_prompt.md / 디깅스팟 6개 카테고리에 맞춰 새로 정의합니다.
카테고리는 블로그 사이드바 '카테고리' 위젯에 노출되는 라벨과 정확히 같아야 합니다.
"""

import os
from pathlib import Path

from content_generator import _extract_json
from seo_utils import make_slug, clean_text

DIGGINGSPOT_CATEGORIES = ["경제·금융", "AI·기술", "부동산·정책", "생활정보", "육아·교육", "글로벌이슈"]

# 예전 이름으로 생성돼도 사이드바 카테고리로 맞춰 줍니다.
CATEGORY_ALIASES = {
    "라이프스타일": "생활정보",
    "글로벌 이슈": "글로벌이슈",
    "AI·테크": "AI·기술",
    "경제금융": "경제·금융",
    "육아": "육아·교육",
}


def _normalize_diggingspot_article(data: dict, topic: str) -> dict:
    data = dict(data or {})
    data["keyword"] = topic
    data["title"] = clean_text(data.get("title") or topic)
    data["slug"] = data.get("slug") or make_slug(data["title"] or topic)
    data["meta_description"] = clean_text(data.get("meta_description") or "")
    data["html"] = data.get("html") or ""

    category = str(data.get("category") or "").strip()
    category = CATEGORY_ALIASES.get(category, category)
    if category not in DIGGINGSPOT_CATEGORIES:
        category = "생활정보"
    data["category"] = category

    tags = data.get("tags") if isinstance(data.get("tags"), list) else []
    tags = [str(t).strip() for t in tags if str(t).strip() and str(t).strip() != category]
    data["tags"] = tags[:2]

    data["review_checklist"] = (
        data.get("review_checklist") if isinstance(data.get("review_checklist"), list) else []
    )
    return data


def generate_diggingspot_article(topic: str, model: str = None) -> dict:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY가 없습니다.")

    model = model or os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    template_path = Path(__file__).resolve().parent / "templates" / "diggingspot_prompt.md"
    template_text = template_path.read_text(encoding="utf-8")
    prompt = template_text.replace("{topic}", topic)

    from google import genai

    client = genai.Client(api_key=api_key)
    resp = client.models.generate_content(model=model, contents=prompt)
    data = _extract_json(resp.text or "")
    return _normalize_diggingspot_article(data, topic)
