# v1.29 카드뉴스 인사이트/차트 개선 패치

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

## 개선 내용

기존 `한줄 인사이트`의 일반 fallback 문구를 제거하고, 기사 내용 기반의 전망형 인사이트로 바꿉니다.

기존:

```text
헤드라인 목록을 기준으로 관련 기사 3건을 묶었습니다.
```

변경:

```text
환율 상승은 수입물가와 외국인 자금 흐름을 흔들어 증시 변동성을 키울 수 있습니다.
금리 인상 기대가 커지면 달러 강세와 성장주 조정 압력이 함께 나타날 수 있습니다.
유가 상승은 시차를 두고 운송비와 공공요금 부담으로 번질 가능성이 있습니다.
```

## 차트

환율, 유가, 코스피, 코스닥, 나스닥 관련 이슈는 카드 안에 간단한 추이 차트를 표시합니다.

## 테스트

```text
Actions
→ Morning Headline News Report
→ Run workflow
```

정상 로그:

```text
[daily-hotissue-cardnews result]
issues_preview
chart
insight
```

카드뉴스에서 확인할 것:

```text
- 제목이 단순 키워드가 아니라 주요 이슈 문장으로 바뀌었는지
- 기사 흐름 3줄 요약이 자연스러운지
- 전망 인사이트가 작업 설명이 아니라 해석 문장인지
- 환율/유가/증시 관련 카드에 차트가 들어가는지
```
