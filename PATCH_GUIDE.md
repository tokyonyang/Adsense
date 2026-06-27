# v1.20 아침 헤드라인 최신성/정합성 최종 보강 패치

## 교체할 파일

```text
app/jobs/send_headline_news_report.py
.github/workflows/morning-headline-news.yml
docs/morning_headline_freshness_fix_v1_20.md
```

## 해결하는 문제

- 오래된 뉴스가 헤드라인 이미지에 섞이는 문제
- 06/27 리포트에 05월, 04월, 03월 기사 포함
- 후보가 부족할 때 무리하게 오래된 기사로 채우는 문제

## 핵심 변경

```text
24시간 이내 뉴스 우선
부족하면 48시간까지만 확장
48시간보다 오래된 뉴스는 절대 사용 금지
부족하면 부족한 개수 그대로 전송
```

## 적용 후 테스트

```text
Actions
→ Morning Headline News Report
→ Run workflow
```

GitHub Actions 로그에서 아래를 확인하세요.

```text
[headline freshness] primary 24h candidates:
[headline freshness] fallback 48h candidates:
[headline selected]
[briefs preview]
```

`briefs preview`의 `published_at`이 모두 최근 48시간 이내면 정상입니다.
