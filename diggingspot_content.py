"""디깅스팟 전용 글 생성 모듈.

content_generator.py의 Gemini 호출/파싱 로직을 재사용하되, 프롬프트와 라벨 규칙만
diggingspot_prompt.md / 디깅스팟 5개 카테고리에 맞춰 새로 정의합니다.
"""

import os
from pathlib import Path

from content_generator import _extract_json
from seo_utils import make_slug, clean_text

DIGGINGSPOT_CATEGORIES = ["경제·금융", "AI·기술", "부동산·정책", "라이프스타일", "글로벌 이슈"]


def _normalize_diggingspot_article(data: dict, topic: str) -> dict:
    data = dict(data or {})
    data["keyword"] = topic
    data["title"] = clean_text(data.get("title") or topic)
    data["slug"] = data.get("slug") or make_slug(data["title"] or topic)
    data["meta_description"] = clean_text(data.get("meta_description") or "")
    data["html"] = data.get("html") or ""

    tags = data.get("tags") if isinstance(data.get("tags"), list) else []
    data["tags"] = [str(t).strip() for t in tags if str(t).strip()][:4]

    category = str(data.get("category") or "").strip()
    if category not in DIGGINGSPOT_CATEGORIES:
        category = "라이프스타일"
    data["category"] = category

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
