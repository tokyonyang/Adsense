"""
v1.26 main.py 패치 포인트

기존 main.py 전체를 이 파일로 무조건 교체하기보다,
아래 import와 선택 로직을 기존 Daily AdSense SEO Hot Issue Report의
TOP 10 선발 직전에 반영하세요.

필수 import:

from app.services.hotissue_category_policy import (
    apply_hotissue_category_policy,
    category_mix_text,
    policy_debug_text,
)

기존에 score 순으로 TOP 10을 자르던 코드가 아래 중 하나처럼 되어 있을 가능성이 높습니다.

items = sorted(items, key=lambda x: x["score"], reverse=True)[:10]
top_items = items[:10]
report_items = scored_items[:10]

위 부분을 아래처럼 변경하세요.

report_items = apply_hotissue_category_policy(scored_items)

텔레그램 리포트 하단 또는 상단에는 아래 메모를 추가하세요.

카테고리 정책: {policy_debug_text()}
카테고리 구성: {category_mix_text(report_items)}

주의:
이 파일은 프로젝트마다 main.py 구조가 달라서 안전하게 덮어쓰기 어렵습니다.
v1.26의 실제 핵심 로직은 app/services/hotissue_category_policy.py 입니다.
"""

from app.services.hotissue_category_policy import (
    apply_hotissue_category_policy,
    category_mix_text,
    policy_debug_text,
)

__all__ = [
    "apply_hotissue_category_policy",
    "category_mix_text",
    "policy_debug_text",
]
