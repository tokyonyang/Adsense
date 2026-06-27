from __future__ import annotations

# v1.27: 카테고리 정책은 daily_hotissue_engine을 단일 원천으로 사용합니다.
# 기존 import 경로 호환을 위해 re-export만 유지합니다.
from app.services.daily_hotissue_engine import (  # noqa: F401
    DEFAULT_LOW_PRIORITY_CATEGORIES,
    DEFAULT_PRIORITY_CATEGORIES,
    DEFAULT_SECONDARY_CATEGORIES,
    apply_hotissue_category_policy,
    category_mix_text,
    category_policy_from_env,
    item_category,
    item_score,
    policy_debug_text,
    select_balanced_items,
    select_finance_first_items,
    sort_items,
)
