from __future__ import annotations

import os
from typing import Any


DEFAULT_PRIORITY_CATEGORIES = [
    "경제·금융",
    "증권·투자",
    "산업·기업",
    "정책·지원금",
    "부동산·주거금융",
    "생활·제도",
    "국제",
]

DEFAULT_SECONDARY_CATEGORIES = [
    "시사·정치",
    "사회·사건",
    "날씨·안전",
    "건강·의료",
    "교육·입시",
]

DEFAULT_LOW_PRIORITY_CATEGORIES = [
    "연예·문화",
    "스포츠",
    "기타",
]


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def parse_csv(value: str, fallback: list[str]) -> list[str]:
    if not value:
        return fallback[:]
    parsed = [x.strip() for x in value.split(",") if x.strip()]
    return parsed or fallback[:]


def parse_int_env(name: str, default: int) -> int:
    try:
        return int(env(name, str(default)))
    except Exception:
        return default


def category_policy_from_env() -> dict[str, Any]:
    """
    HOT_ISSUE_CATEGORY_MODE
    - finance_first: 경제/금융·증시·산업·정책 카테고리를 우선 선발
    - balanced: 카테고리별 균형 선발
    - all_score: 전체 점수순 선발

    HOT_ISSUE_PRIORITY_CATEGORIES
    - 우선 카테고리 CSV

    HOT_ISSUE_PRIORITY_MIN
    - TOP 10 중 우선 카테고리에서 최소 몇 개를 채울지

    HOT_ISSUE_LOW_PRIORITY_MAX
    - 연예/스포츠/기타 등 저우선 카테고리 전체 허용 개수

    HOT_ISSUE_OTHER_MAX
    - 기타 카테고리 허용 개수

    HOT_ISSUE_PER_CATEGORY_MAX
    - 단일 카테고리 최대 개수
    """
    mode = env("HOT_ISSUE_CATEGORY_MODE", "finance_first").lower()

    priority_categories = parse_csv(
        env("HOT_ISSUE_PRIORITY_CATEGORIES"),
        DEFAULT_PRIORITY_CATEGORIES,
    )

    secondary_categories = parse_csv(
        env("HOT_ISSUE_SECONDARY_CATEGORIES"),
        DEFAULT_SECONDARY_CATEGORIES,
    )

    low_priority_categories = parse_csv(
        env("HOT_ISSUE_LOW_PRIORITY_CATEGORIES"),
        DEFAULT_LOW_PRIORITY_CATEGORIES,
    )

    return {
        "mode": mode,
        "priority_categories": priority_categories,
        "secondary_categories": secondary_categories,
        "low_priority_categories": low_priority_categories,
        "top_n": parse_int_env("HOT_ISSUE_TOP_N", 10),
        "priority_min": parse_int_env("HOT_ISSUE_PRIORITY_MIN", 6),
        "priority_max": parse_int_env("HOT_ISSUE_PRIORITY_MAX", 8),
        "secondary_max": parse_int_env("HOT_ISSUE_SECONDARY_MAX", 3),
        "low_priority_max": parse_int_env("HOT_ISSUE_LOW_PRIORITY_MAX", 2),
        "other_max": parse_int_env("HOT_ISSUE_OTHER_MAX", 1),
        "per_category_max": parse_int_env("HOT_ISSUE_PER_CATEGORY_MAX", 2),
        "priority_per_category_max": parse_int_env("HOT_ISSUE_PRIORITY_PER_CATEGORY_MAX", 3),
    }


def item_category(item: dict[str, Any]) -> str:
    return str(
        item.get("category")
        or item.get("cat")
        or item.get("section")
        or item.get("category_name")
        or "기타"
    ).strip() or "기타"


def item_score(item: dict[str, Any]) -> float:
    for key in ["score", "hot_score", "trend_score", "total_score"]:
        try:
            return float(item.get(key) or 0)
        except Exception:
            pass
    return 0.0


def category_rank(category: str, policy: dict[str, Any]) -> int:
    if category in policy["priority_categories"]:
        return 0
    if category in policy["secondary_categories"]:
        return 1
    if category in policy["low_priority_categories"]:
        return 2
    return 2


def sort_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(items, key=lambda x: item_score(x), reverse=True)


def select_balanced_items(items: list[dict[str, Any]], policy: dict[str, Any]) -> list[dict[str, Any]]:
    top_n = policy["top_n"]
    per_category_max = policy["per_category_max"]
    other_max = policy["other_max"]

    selected = []
    used_ids = set()
    category_count: dict[str, int] = {}

    for item in sort_items(items):
        if len(selected) >= top_n:
            break

        category = item_category(item)
        key = id(item)

        if category == "기타" and category_count.get("기타", 0) >= other_max:
            continue
        if category_count.get(category, 0) >= per_category_max:
            continue

        selected.append(item)
        used_ids.add(key)
        category_count[category] = category_count.get(category, 0) + 1

    if len(selected) < top_n:
        for item in sort_items(items):
            if len(selected) >= top_n:
                break
            if id(item) in used_ids:
                continue
            selected.append(item)
            used_ids.add(id(item))

    return selected[:top_n]


def select_finance_first_items(items: list[dict[str, Any]], policy: dict[str, Any]) -> list[dict[str, Any]]:
    """
    경제/금융 우선 운영용 선발 로직.

    1. 우선 카테고리에서 최소 priority_min개 확보
    2. 우선 카테고리는 단일 카테고리 최대 priority_per_category_max개까지 허용
    3. 보조 카테고리에서 secondary_max개까지 보충
    4. 연예/스포츠/기타 등 저우선 카테고리는 low_priority_max개까지만 허용
    5. 부족하면 전체 점수순으로 채움
    """
    top_n = policy["top_n"]
    priority_min = min(policy["priority_min"], top_n)
    priority_max = min(policy["priority_max"], top_n)
    secondary_max = policy["secondary_max"]
    low_priority_max = policy["low_priority_max"]
    other_max = policy["other_max"]
    priority_per_category_max = policy["priority_per_category_max"]
    per_category_max = policy["per_category_max"]

    priority_set = set(policy["priority_categories"])
    secondary_set = set(policy["secondary_categories"])
    low_set = set(policy["low_priority_categories"])

    selected = []
    used_ids = set()
    category_count: dict[str, int] = {}
    group_count = {"priority": 0, "secondary": 0, "low": 0}

    def can_add(item: dict[str, Any], stage: str) -> bool:
        category = item_category(item)

        if id(item) in used_ids:
            return False

        if category == "기타" and category_count.get("기타", 0) >= other_max:
            return False

        if category in priority_set:
            max_for_cat = priority_per_category_max
        else:
            max_for_cat = per_category_max

        if category_count.get(category, 0) >= max_for_cat:
            return False

        if stage == "priority":
            return category in priority_set and group_count["priority"] < priority_max

        if stage == "secondary":
            return category in secondary_set and group_count["secondary"] < secondary_max

        if stage == "low":
            return category in low_set and group_count["low"] < low_priority_max

        return True

    def add(item: dict[str, Any]):
        category = item_category(item)
        selected.append(item)
        used_ids.add(id(item))
        category_count[category] = category_count.get(category, 0) + 1

        if category in priority_set:
            group_count["priority"] += 1
        elif category in secondary_set:
            group_count["secondary"] += 1
        else:
            group_count["low"] += 1

    sorted_all = sort_items(items)

    # 1) 우선 카테고리 최소 확보
    for item in sorted_all:
        if len(selected) >= top_n or group_count["priority"] >= priority_min:
            break
        if can_add(item, "priority"):
            add(item)

    # 2) 우선 카테고리 추가 확보(priority_max까지)
    for item in sorted_all:
        if len(selected) >= top_n or group_count["priority"] >= priority_max:
            break
        if can_add(item, "priority"):
            add(item)

    # 3) 보조 카테고리 보충
    for item in sorted_all:
        if len(selected) >= top_n:
            break
        if can_add(item, "secondary"):
            add(item)

    # 4) 저우선 카테고리 제한 보충
    for item in sorted_all:
        if len(selected) >= top_n:
            break
        if can_add(item, "low"):
            add(item)

    # 5) 그래도 부족하면 전체 점수순으로 보충
    for item in sorted_all:
        if len(selected) >= top_n:
            break
        if can_add(item, "any"):
            add(item)

    return selected[:top_n]


def apply_hotissue_category_policy(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    policy = category_policy_from_env()
    mode = policy["mode"]

    if mode == "all_score":
        return sort_items(items)[:policy["top_n"]]

    if mode == "balanced":
        return select_balanced_items(items, policy)

    # default
    return select_finance_first_items(items, policy)


def category_mix_text(items: list[dict[str, Any]]) -> str:
    counts: dict[str, int] = {}
    for item in items:
        category = item_category(item)
        counts[category] = counts.get(category, 0) + 1

    return " / ".join(f"{cat} {cnt}개" for cat, cnt in sorted(counts.items(), key=lambda x: (-x[1], x[0])))


def policy_debug_text() -> str:
    p = category_policy_from_env()
    return (
        f"모드={p['mode']} · "
        f"우선={','.join(p['priority_categories'])} · "
        f"우선최소={p['priority_min']} · "
        f"저우선최대={p['low_priority_max']} · "
        f"기타최대={p['other_max']}"
    )
