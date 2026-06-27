from __future__ import annotations

import json

from app.services.telegram_report_service import validate_telegram_connection, validate_telegram_env


def main():
    """
    텔레그램 연결 상태를 검증합니다.

    v1.16 변경:
    - 더 이상 테스트 메시지를 텔레그램으로 보내지 않습니다.
    - getMe / getChat API로 토큰과 채팅 접근 가능 여부만 확인합니다.
    - 결과는 GitHub Actions 로그에만 출력합니다.
    """
    print("[telegram env]")
    print(json.dumps(validate_telegram_env(), ensure_ascii=False, indent=2))

    result = validate_telegram_connection(fail_silently=False)

    print("[telegram connection validation]")
    print(json.dumps({
        "ok": result.get("ok"),
        "bot_username": result.get("bot_username"),
        "chat_id_masked": result.get("chat_id_masked"),
        "chat_type": result.get("chat_type"),
        "chat_title": result.get("chat_title"),
        "message_sent": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
