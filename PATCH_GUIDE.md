# v1.10.2 Telegram 자동 전송 진단/수정 패치

## 증상

GitHub Actions는 실행됐는데 텔레그램 자동 메시지가 오지 않는 경우.

## 이번 패치에서 바꾼 점

- 텔레그램 토큰/채팅ID 존재 여부를 Actions 로그에 표시
- 텔레그램 전송 실패 시 Actions가 실패하도록 변경
- 수동 테스트용 workflow 추가
- 자동 파이프라인 전에 Telegram test message를 먼저 보냄

## GitHub에 업로드/교체할 파일

```text
app/services/telegram_report_service.py
app/jobs/send_telegram_test.py
app/jobs/run_daily_pipeline.py
.github/workflows/adsense-dashboard-cron.yml
.github/workflows/telegram-send-test.yml
docs/telegram_delivery_fix_v1_10_2.md
```

## 적용 후 가장 먼저 할 테스트

GitHub에서:

```text
Actions
→ Telegram Send Test
→ Run workflow
```

성공하면 텔레그램에 아래 메시지가 와야 합니다.

```text
✅ Telegram 연결 테스트
```

## 테스트가 실패하면

Actions 로그에서 아래를 확인하세요.

```text
TELEGRAM_BOT_TOKEN이 설정되지 않았습니다.
TELEGRAM_CHAT_ID가 설정되지 않았습니다.
Telegram 전송 실패: ...
```

## TELEGRAM_CHAT_ID 확인

채널/그룹이면 보통 아래처럼 `-100`으로 시작합니다.

```text
-100xxxxxxxxxx
```

채널에는 봇을 관리자로 추가하고 메시지 전송 권한을 줘야 합니다.

## 자동 리포트 확인

Telegram Send Test가 성공한 뒤:

```text
Actions
→ AdSense Dashboard Cron
→ Run workflow
```

단계에 아래가 보여야 합니다.

```text
Validate Telegram secrets
Preview event boost config
Run daily dashboard pipeline and Telegram report
```
