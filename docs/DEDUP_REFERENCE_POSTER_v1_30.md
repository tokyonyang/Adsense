# v1.30 중복 제거 + 신문 헤드라인 반영 + 포스터형 카드뉴스

## 반영 내용

사용자가 공유한 주요신문 헤드라인 구조와 참고 카드뉴스 이미지를 반영했습니다.

## 핵심 개선

```text
1. 중복 이슈 제거 강화
2. 주요신문 헤드라인 seed 반영
3. Daily 선별 시 신문형 경제/증권/정책/사회/국제/IT 이슈 우선 보강
4. Morning 카드뉴스에서 중복 이슈 제거
5. 카드뉴스 디자인을 참고 이미지처럼 포스터형 큰 제목 스타일로 변경
```

## 신문 헤드라인 반영 방식

아래 파일을 추가했습니다.

```text
data/morning_reference_headlines.txt
```

이 파일에 주요신문 헤드라인을 넣으면 Daily 이슈 후보 seed로 사용됩니다.

또한 기본 내장 seed pack이 추가되었습니다.

```text
economic_newspaper
stock_finance
international
politics_social
it_science_life
```

환경변수:

```yaml
HOT_ISSUE_USE_REFERENCE_HEADLINES: "true"
HOT_ISSUE_REFERENCE_PACKS: "economic_newspaper,stock_finance,international,politics_social,it_science_life"
HOT_ISSUE_REFERENCE_HEADLINES_FILE: "data/morning_reference_headlines.txt"
```

## 카드뉴스 디자인 변경

기존:

```text
검정 배경 + 박스형 텍스트 카드
```

변경:

```text
정사각형 포스터 카드
큰 제목
카테고리 리본
강한 시각적 배경
기사 흐름 3줄
전망 인사이트
관련 키워드/출처 하단 표시
```

이미지 크기:

```yaml
HEADLINE_IMAGE_WIDTH: 1080
HEADLINE_IMAGE_HEIGHT: 1080
HEADLINE_IMAGE_SCALE: 2
```

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

## 한계

참고 이미지처럼 완전한 AI 일러스트 배경을 매번 새로 생성하는 구조는 아닙니다.  
GitHub Actions에서는 안정성을 위해 HTML/CSS 기반 포스터 스타일로 구현했습니다.

향후 OpenAI 이미지 API 또는 별도 이미지 생성 API를 붙이면 배경 일러스트까지 자동 생성할 수 있습니다.
