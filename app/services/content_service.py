from app.repositories.content_repository import ContentIdeaRepository, ArticleRepository, CardnewsRepository


class ContentService:
    def __init__(self):
        self.ideas = ContentIdeaRepository()
        self.articles = ArticleRepository()
        self.cardnews = CardnewsRepository()

    def list_ideas(self, user_id: str | None = None, limit: int = 50):
        query = self.ideas.client.table("content_ideas").select("*").order("created_at", desc=True)
        if user_id:
            query = query.eq("user_id", user_id)
        return query.limit(limit).execute().data

    def generate_article(self, idea_id: str, user_id: str | None = None, tone: str | None = None):
        idea = self.ideas.get(idea_id)
        if not idea:
            return None

        title = idea.get("title") or "SEO 글 초안"
        html = f"""
<article>
  <h1>{title}</h1>
  <p>{idea.get('writing_angle') or '주요 이슈를 쉽게 정리합니다.'}</p>
  <h2>핵심 요약</h2>
  <p>이 글은 검색 수요와 근거자료를 바탕으로 작성된 초안입니다.</p>
  <h2>확인해야 할 포인트</h2>
  <ul>
    <li>공식 출처 확인</li>
    <li>과장 표현 제거</li>
    <li>FAQ 추가</li>
  </ul>
</article>
"""

        payload = {
            "user_id": user_id,
            "idea_id": idea_id,
            "title": title,
            "slug": title.lower().replace(" ", "-")[:80],
            "meta_description": idea.get("meta_description") or f"{title}에 대한 핵심 내용을 정리했습니다.",
            "category": idea.get("category"),
            "tags": idea.get("tags") or [],
            "html": html,
            "seo_score": 75,
            "adsense_safety": "caution" if idea.get("category") in ["economy", "policy"] else "safe",
            "status": "review_needed",
        }
        return self.articles.create(payload)

    def generate_cardnews(self, idea_id: str, user_id: str | None = None):
        idea = self.ideas.get(idea_id)
        if not idea:
            return None

        title = idea.get("title") or "카드뉴스 초안"
        payload = {
            "user_id": user_id,
            "idea_id": idea_id,
            "title": title,
            "thumbnail_copy": idea.get("hook_point") or "오늘 꼭 알아야 할 이슈",
            "tone": "informative",
            "cards": [
                {"no": 1, "title": "후킹", "body": idea.get("hook_point") or title},
                {"no": 2, "title": "상황 설명", "body": "현재 이슈가 주목받는 이유"},
                {"no": 3, "title": "핵심 원인", "body": "주요 원인을 쉽게 정리"},
                {"no": 4, "title": "내 생활 영향", "body": "독자에게 미치는 영향"},
                {"no": 5, "title": "확인 포인트", "body": "앞으로 봐야 할 지표"},
                {"no": 6, "title": "주의점", "body": "과장 없이 검토할 내용"},
                {"no": 7, "title": "요약", "body": "핵심만 한 장으로 정리"},
                {"no": 8, "title": "저장 유도", "body": "필요할 때 다시 보기"},
            ],
            "image_prompt": f"{title} 주제의 한국어 카드뉴스 이미지, 깔끔한 정보형 디자인",
            "status": "draft",
        }
        return self.cardnews.create(payload)

    def seo_check(self, title: str | None = None, html: str | None = None, category: str | None = None, article_id: str | None = None):
        score = 80
        checklist = []

        if title:
            if 20 <= len(title) <= 70:
                checklist.append({"item": "제목 길이", "status": "pass", "message": "제목 길이가 적정합니다."})
            else:
                score -= 10
                checklist.append({"item": "제목 길이", "status": "warn", "message": "제목 길이를 조정하세요."})

        if html and "<h2" in html:
            checklist.append({"item": "본문 구조", "status": "pass", "message": "H2 구조가 포함되어 있습니다."})
        else:
            score -= 10
            checklist.append({"item": "본문 구조", "status": "warn", "message": "H2/H3 구조가 필요합니다."})

        if category in ["economy", "policy", "stock"]:
            checklist.append({"item": "민감 주제", "status": "warn", "message": "금융/정책 주제는 공식 출처와 단정 표현 검수가 필요합니다."})
            safety = "caution"
        else:
            checklist.append({"item": "애드센스 안전도", "status": "pass", "message": "정책 리스크가 낮은 주제입니다."})
            safety = "safe"

        return {
            "seo_score": max(score, 0),
            "adsense_safety": safety,
            "checklist": checklist,
        }
