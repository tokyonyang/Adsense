# main.py 전체 교체본 v1.26.2

## 용도

기존 `main.py`가 v1.26 안내용 파일로 잘못 덮어쓰기 된 경우, 이 파일을 그대로 `main.py`로 교체해 Daily AdSense SEO Hot Issue Report를 다시 실행할 수 있습니다.

## 포함 기능

- Google Trends RSS 키워드 수집
- 경제/금융 우선 seed 키워드 추가
- Naver News API 기반 근거자료 수집
- Google News RSS fallback
- 기사 제목/설명 기반 카테고리 재분류
- 경제/금융 우선 카테고리 정책
- TOP 10 텔레그램 리포트 전송
- `reports/*.json`, `reports/*.txt` 저장

## 주요 환경변수

```yaml
HOT_ISSUE_CATEGORY_MODE: "finance_first"
HOT_ISSUE_PRIORITY_MIN: 6
HOT_ISSUE_PRIORITY_MAX: 8
HOT_ISSUE_LOW_PRIORITY_MAX: 2
HOT_ISSUE_OTHER_MAX: 1
HOT_ISSUE_TOP_N: 10
HOT_ISSUE_NEWS_PER_KEYWORD: 5
```

## 더 강하게 경제/금융 중심으로 운영

```yaml
HOT_ISSUE_PRIORITY_MIN: 8
HOT_ISSUE_PRIORITY_MAX: 9
HOT_ISSUE_LOW_PRIORITY_MAX: 1
HOT_ISSUE_OTHER_MAX: 0
```

## 주의

이 파일은 Daily Hot Issue Report용 전체 교체본입니다.
기존 프로젝트의 WordPress 자동 발행, Gemini 초안 생성 등 추가 기능이 따로 있었다면 이 파일에는 포함하지 않았습니다.
우선 텔레그램 HOT Issue Report를 안정 복구하는 목적입니다.
