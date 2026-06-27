# v1.16 Telegram 연결 테스트 메시지 제거

## 변경 이유

기존 `Telegram Send Test` 또는 각 workflow의 `Validate Telegram secrets` 단계에서 아래 메시지가 실제 텔레그램으로 전송되었습니다.

```text
Telegram 연결 테스트

- 실행 시각: ...
- 메시지가 보이면 GitHub Actions → Telegram 연결은 정상입니다.
```

운영 중에는 불필요한 메시지이므로 제거했습니다.

## 변경 내용

기존:

```text
sendMessage로 테스트 메시지 전송
```

수정:

```text
getMe API로 bot token 검증
getChat API로 chat_id 접근 가능 여부 검증
GitHub Actions 로그에만 결과 출력
텔레그램 채팅방에는 아무 메시지도 보내지 않음
```

## 확인 방법

GitHub Actions 로그에 아래처럼 출력되면 정상입니다.

```json
{
  "ok": true,
  "bot_username": "...",
  "chat_id_masked": "-100...1234",
  "chat_type": "channel",
  "message_sent": false
}
```
