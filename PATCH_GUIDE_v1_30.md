# v1.30 적용 가이드

## 적용 파일

```text
app/services/reference_headline_service.py
app/services/daily_hotissue_engine.py
app/services/daily_hotissue_source.py
app/services/headline_cardnews_summary_service.py
app/services/headline_cardnews_render_service.py
data/morning_reference_headlines.txt
.github/workflows/daily-adsense-seo.yml
.github/workflows/morning-headline-news.yml
docs/DEDUP_REFERENCE_POSTER_v1_30.md
PATCH_GUIDE_v1_30.md
```

## 적용 후 테스트

### 1. Daily 실행

```text
Actions
→ Daily AdSense SEO Hot Issue Report
→ Run workflow
```

확인:

```text
- 경제/증권/산업/정책/사회/국제/IT 이슈가 다양하게 잡히는지
- 같은 이슈가 표현만 다르게 중복되지 않는지
```

### 2. Morning 실행

```text
Actions
→ Morning Headline News Report
→ Run workflow
```

확인:

```text
- 카드가 정사각형 포스터 스타일로 바뀌었는지
- 큰 제목이 단순 키워드가 아니라 공통 쟁점인지
- 중복 이슈가 빠졌는지
- 전망 인사이트가 의미 있는지
```

## 주요신문 헤드라인 직접 반영 방법

`data/morning_reference_headlines.txt`에 매일 아침 정리한 신문 헤드라인을 넣으면 됩니다.

예시:

```text
<경제>
정부 등록임대 제도 집값 안정 전세난 우려
카카오뱅크 인수합병 종합금융플랫폼 도약
```

이 파일은 Daily 수집 seed로 사용됩니다.
