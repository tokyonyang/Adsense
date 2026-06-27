from __future__ import annotations

import json
from datetime import datetime

from app.services.telegram_report_service import send_telegram_message, validate_telegram_env


def main():
    env_status = validate_telegram_env()
    print("[telegram env]")
    print(json.dumps(env_status, ensure_ascii=False, indent=2))

    message = (
        "<b>✅ Telegram 연결 테스트</b>\n\n"
        f"- 실행 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        "- 메시지가 보이면 GitHub Actions → Telegram 연결은 정상입니다."
    )

    result = send_telegram_message(message, fail_silently=False)
    print("[telegram send result]")
    print(json.dumps({
        "ok": result.get("ok"),
        "sent_parts": result.get("sent_parts"),
        "chat_id_masked": result.get("chat_id_masked"),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
