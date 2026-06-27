# v1.26 Daily Hot Issue 경제/금융 우선 옵션

## 목적

Daily HOT Issue TOP 10이 연예, 스포츠, 기타 이슈에 과도하게 쏠리지 않도록 하고,
경제/금융·증권·산업·정책·부동산·생활경제 중심으로 먼저 정리할 수 있는 옵션을 추가합니다.

## 핵심 환경변수

```yaml
HOT_ISSUE_CATEGORY_MODE: "finance_first"
```

사용 가능한 모드:

```text
finance_first: 경제/금융 우선
balanced: 카테고리별 균형
all_score: 전체 점수순
```

## 기본 우선 카테고리

```yaml
HOT_ISSUE_PRIORITY_CATEGORIES: "경제·금융,증권·투자,산업·기업,정책·지원금,부동산·주거금융,생활·제도,국제"
```

## 기본 선발 정책

```yaml
HOT_ISSUE_PRIORITY_MIN: 6
HOT_ISSUE_PRIORITY_MAX: 8
HOT_ISSUE_SECONDARY_MAX: 3
HOT_ISSUE_LOW_PRIORITY_MAX: 2
HOT_ISSUE_OTHER_MAX: 1
HOT_ISSUE_PER_CATEGORY_MAX: 2
HOT_ISSUE_PRIORITY_PER_CATEGORY_MAX: 3
```

즉 TOP 10 중 최소 6개는 경제/금융 관련 우선 카테고리에서 가져오고,
연예/스포츠/기타는 합산 최대 2개까지만 허용합니다.

## 더 강하게 경제 중심으로 운영하고 싶을 때

```yaml
HOT_ISSUE_PRIORITY_MIN: 8
HOT_ISSUE_PRIORITY_MAX: 9
HOT_ISSUE_LOW_PRIORITY_MAX: 1
HOT_ISSUE_OTHER_MAX: 0
```

## 완전히 균형형으로 운영하고 싶을 때

```yaml
HOT_ISSUE_CATEGORY_MODE: "balanced"
HOT_ISSUE_PER_CATEGORY_MAX: 2
HOT_ISSUE_OTHER_MAX: 1
```

## 전체 점수순으로 되돌리고 싶을 때

```yaml
HOT_ISSUE_CATEGORY_MODE: "all_score"
```
