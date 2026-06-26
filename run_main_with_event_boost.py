"""
기존 루트 main.py를 그대로 두고 이벤트 부스트 + 텔레그램 요약을 적용하는 wrapper.

GitHub Actions에서 기존:
    python main.py

대신:
    python run_main_with_event_boost.py

로 바꾸면 됩니다.
"""

from __future__ import annotations

import runpy

from event_boost_runtime import apply_event_boost_env


def main():
    apply_event_boost_env()
    runpy.run_module("main", run_name="__main__")


if __name__ == "__main__":
    main()
