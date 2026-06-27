# v1.26 경제/금융 우선 옵션 패치

## 핵심

Daily HOT Issue TOP 10을 경제/금융 등 우선 카테고리 중심으로 먼저 선발할 수 있는 옵션을 추가합니다.

## 추가/교체 파일

```text
app/services/hotissue_category_policy.py
.github/workflows/daily-adsense-seo.yml
.github/workflows/morning-headline-news.yml
docs/daily_hotissue_finance_priority_v1_26.md
```

## main.py 반영 필요

`main.py`는 프로젝트마다 구조가 달라서 완전 덮어쓰기보다 아래 방식으로 반영하는 것을 권장합니다.

### 1. import 추가

```python
from app.services.hotissue_category_policy import (
    apply_hotissue_category_policy,
    category_mix_text,
    policy_debug_text,
)
```

### 2. TOP 10 자르는 부분 교체

기존 예시:

```python
top_items = sorted(scored_items, key=lambda x: x["score"], reverse=True)[:10]
```

변경:

```python
top_items = apply_hotissue_category_policy(scored_items)
```

### 3. 텔레그램 리포트에 정책 메모 추가

```python
lines.append("")
lines.append("📊 카테고리 정책")
lines.append(policy_debug_text())
lines.append(f"카테고리 구성: {category_mix_text(top_items)}")
```

## 운영 옵션

경제/금융 우선:

```yaml
HOT_ISSUE_CATEGORY_MODE: "finance_first"
```

카테고리 균형:

```yaml
HOT_ISSUE_CATEGORY_MODE: "balanced"
```

전체 점수순:

```yaml
HOT_ISSUE_CATEGORY_MODE: "all_score"
```

## 더 강한 경제/금융 중심

```yaml
HOT_ISSUE_PRIORITY_MIN: 8
HOT_ISSUE_PRIORITY_MAX: 9
HOT_ISSUE_LOW_PRIORITY_MAX: 1
HOT_ISSUE_OTHER_MAX: 0
```

## 테스트

```text
Actions
→ Daily AdSense SEO Hot Issue Report
→ Run workflow
```

텔레그램 결과에서 아래를 확인하세요.

```text
📊 카테고리 정책
모드=finance_first ...
카테고리 구성: 경제·금융 2개 / 증권·투자 2개 / 산업·기업 2개 ...
```
