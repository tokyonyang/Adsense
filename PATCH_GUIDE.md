# AdSense SEO 운영 대시보드 v1.10 패치

## 이번 단계

경제지표 이벤트 부스트 결과를 텔레그램 리포트에 표시합니다.

## GitHub에 업로드/교체할 파일

```text
app/services/telegram_report_service.py
app/jobs/run_daily_pipeline.py
app/jobs/run_event_boost_preview.py
.github/workflows/adsense-dashboard-cron.yml
run_main_with_event_boost.py
docs/event_boost_telegram_v1_10.md
```

## 핵심 변경

v1.9에서는 경제지표 이벤트일에 검색량만 자동 증가했습니다.

v1.10에서는 텔레그램에 아래 내용이 추가됩니다.

```text
📊 경제지표 검색 강화 상태
- 상태
- 키워드 수집량
- 근거자료 수집량
- 강화 검색어
- 대상 경제지표
```

## 적용 후 테스트

GitHub Actions에서 수동 실행:

```text
Actions
→ AdSense Dashboard Cron
→ Run workflow
```

로그에서 아래 단계가 보여야 합니다.

```text
Preview event boost config
Run daily dashboard pipeline and Telegram report
```

정상이라면 텔레그램에 자동 수집 리포트가 전송됩니다.

## 텔레그램 전송이 skipped 되는 경우

GitHub Secrets에 아래 값이 있는지 확인하세요.

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

값이 없더라도 파이프라인은 실패하지 않고, 출력 로그에 skipped로 표시됩니다.

## 다음 v1.11 추천

이제 다음 단계는 텔레그램 리포트를 두 종류로 나누는 것입니다.

```text
1. 운영자용 리포트
   - 수집량, 오류, 이벤트 부스트 상태

2. 공유용 핫이슈 리포트
   - 핫이슈 제목 + 근거자료 링크만 간결하게 표시
```
