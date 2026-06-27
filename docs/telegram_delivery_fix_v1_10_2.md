# Telegram 자동 전송 문제 해결 v1.10.2

## 핵심

이번 버전부터 텔레그램 전송 실패는 조용히 넘어가지 않습니다.  
토큰/채팅ID/권한 문제가 있으면 GitHub Actions가 실패하고 로그에 원인이 표시됩니다.

## 수동 테스트

```bash
python -m app.jobs.send_telegram_test
```

## 성공 로그 예시

```json
{
  "ok": true,
  "sent_parts": 1,
  "chat_id_masked": "-100...1234"
}
```

## 실패 로그 예시

```text
TELEGRAM_CHAT_ID가 설정되지 않았습니다.
```

또는

```text
Telegram 전송 실패: chat not found
```

## chat not found일 때

- TELEGRAM_CHAT_ID가 틀렸을 가능성
- 봇이 채널/그룹에 초대되지 않았을 가능성
- 채널이면 `-100`으로 시작하는 ID를 써야 할 가능성
