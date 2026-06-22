import os, json, re
from pathlib import Path
from google import genai
from seo_utils import make_slug, clean_text

def _extract_json(text: str) -> dict:
    text = (text or "").strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    start, end = text.find("{"), text.rfind("}")
    if start >= 0 and end > start:
        text = text[start:end+1]
    return json.loads(text)

def generate_article(keyword: str, site_description: str = "", model: str = None) -> dict:
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY가 없습니다.")
    model = model or os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    tmpl = Path("templates/article_prompt.md").read_text(encoding="utf-8")
    prompt = tmpl.format(keyword=keyword, site_description=site_description or "생활 정보 블로그")
    client = genai.Client(api_key=api_key)
    resp = client.models.generate_content(model=model, contents=prompt)
    data = _extract_json(resp.text or "")
    data["keyword"] = keyword
    data["slug"] = data.get("slug") or make_slug(data.get("title") or keyword)
    data["title"] = clean_text(data.get("title") or keyword)
    data["meta_description"] = clean_text(data.get("meta_description") or "")
    data["html"] = data.get("html") or ""
    data["tags"] = data.get("tags") or []
    data["category"] = data.get("category") or "생활정보"
    return data
