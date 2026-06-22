import re
from slugify import slugify

def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()

def make_slug(text: str) -> str:
    return slugify(text, lowercase=True, max_length=80) or "post"

def is_blocked_keyword(keyword: str, blocked_csv: str = "") -> bool:
    kw = clean_text(keyword).lower()
    blocked = [clean_text(x).lower() for x in (blocked_csv or "").split(",") if clean_text(x)]
    return any(b and b in kw for b in blocked)

def score_keyword(keyword: str, source: str = "", approx_traffic: int = 0) -> float:
    score = 50.0
    if approx_traffic:
        score += min(30, approx_traffic / 10000)
    if len(keyword) >= 4:
        score += 5
    if any(x in keyword for x in ["방법", "정리", "뜻", "신청", "비교", "추천", "기간", "가격"]):
        score += 10
    return round(min(score, 100), 2)
