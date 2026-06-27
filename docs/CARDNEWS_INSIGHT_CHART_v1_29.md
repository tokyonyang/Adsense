# v1.29 카드뉴스 인사이트/차트 개선

## 문제

기존 카드뉴스의 `한줄 인사이트`가 아래처럼 작업 설명에 가까운 문구로 출력되었습니다.

```text
헤드라인 목록을 기준으로 관련 기사 3건을 묶었습니다.
```

이 문구는 독자가 얻을 정보가 거의 없고, 카드뉴스 품질을 낮춥니다.

## v1.29 핵심 개선

```text
1. 기사 3개의 공통 쟁점을 AI가 새 제목으로 생성
2. summary_lines는 기사 흐름 3줄 요약으로 변경
3. insight는 향후 전망/시장 영향/과거 유사 국면의 일반 패턴 중심으로 생성
4. 환율·유가·코스피·코스닥·나스닥 등은 시장 추이 차트 자동 삽입
5. Gemini 실패 시에도 fallback 문구가 작업 설명이 아니라 경제적 해석 문장으로 출력
```

## 차트 지원 항목

```text
원·달러 환율: USDKRW=X
코스피: ^KS11
코스닥: ^KQ11
국제유가 WTI: CL=F
나스닥: ^IXIC
```

데이터는 Yahoo Finance chart endpoint를 사용합니다.

## 환경변수

```yaml
HEADLINE_ENABLE_MARKET_CHARTS: "true"
HEADLINE_CHART_RANGE: "3mo"
HEADLINE_CHART_INTERVAL: "1d"
```

## 개선된 카드 구조

```text
주요 이슈 제목
기사 흐름 3줄 요약
관련 지표 차트
전망 인사이트
관련 키워드 / 출처
```

## 적용 파일

```text
app/services/headline_cardnews_summary_service.py
app/services/headline_cardnews_render_service.py
app/services/market_chart_service.py
app/jobs/send_headline_cardnews_report.py
.github/workflows/morning-headline-news.yml
docs/CARDNEWS_INSIGHT_CHART_v1_29.md
PATCH_GUIDE_v1_29.md
```
