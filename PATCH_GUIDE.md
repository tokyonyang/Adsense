# v1.21 아침 헤드라인 운영 안정화 패치

## 교체할 파일

```text
app/jobs/send_headline_news_report.py
.github/workflows/morning-headline-news.yml
docs/morning_headline_resilient_fallback_v1_21.md
```

## 해결하는 문제

v1.20에서 후보가 0개일 때 workflow가 실패하던 문제를 수정합니다.

## 변경 내용

```text
24h → 48h → 날짜포함 재검색 → 72h → 날짜불명 후보
```

순서로 후보를 찾습니다.

다만 날짜가 명확히 있고 72시간보다 오래된 뉴스는 최종적으로 제외합니다.

## 적용 후 테스트

```text
Actions
→ Morning Headline News Report
→ Run workflow
```

확인할 로그:

```text
[headline selected]
[briefs preview]
```

후보가 0개여도 workflow는 실패하지 않고 텔레그램에 안내 메시지만 보냅니다.
