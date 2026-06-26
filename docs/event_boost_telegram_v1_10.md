# v1.10 경제지표 이벤트 부스트 텔레그램 리포트

## 목표

경제지표 이벤트일에 수집량이 왜 늘었는지 텔레그램에서 바로 확인합니다.

## 텔레그램에 표시되는 내용

```text
📊 경제지표 검색 강화 상태
- 상태: critical / high / normal
- 검색 강화 적용 여부
- 키워드 수집량
- 근거자료 수집량
- 강화 검색어
- 주요 경제지표
```

## 예시

```text
📊 경제지표 검색 강화 상태
- 상태: 🔴 critical · 최우선 검색
- 검색 강화 적용: 예
- 키워드 수집량: 80개
- 근거자료 수집량: 이슈당 15개
- 조회 기간: 최근 24시간
- 강화 검색어: PCE, CPI, 물가, 금리, 환율, 국채금리, 연준

주요 경제지표
1) 2026-06-27 21:30 · 미국 · PCE 물가지수 (critical)
```

## 테스트

```bash
python -m app.jobs.run_event_boost_preview
python -m app.jobs.run_daily_pipeline
```

## 텔레그램 전송 조건

GitHub Secrets에 아래 값이 있어야 합니다.

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

값이 없으면 파이프라인은 실패하지 않고 텔레그램 전송만 skipped 처리됩니다.
