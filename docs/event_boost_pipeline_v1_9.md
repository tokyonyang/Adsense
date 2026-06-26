# v1.9 경제지표 이벤트일 자동 검색량 증가 파이프라인

## 목표

`economic_events`에 high/critical 이벤트가 있으면 자동 수집량을 상향합니다.

## 적용 기준

| 상황 | MAX_KEYWORDS | NEWS_LINKS_PER_TOPIC | LOOKBACK_HOURS |
|---|---:|---:|---:|
| 평상시 | 30 | 5 | 24 |
| high 이벤트 | 60 | 10 | 24 |
| critical 이벤트 | 80 | 15 | 24 |

## 실행 흐름

```text
GitHub Actions
→ app.jobs.run_daily_pipeline
→ event_boost_service.get_today_event_boost_config()
→ economic_events 조회
→ 중복 제거
→ 중요도 판단
→ seed_keywords 생성
→ KeywordService.collect_keywords()
→ trend_keywords 저장
```

## 미리보기

```bash
python -m app.jobs.run_event_boost_preview
```

## 실제 실행

```bash
python -m app.jobs.run_daily_pipeline
```

## 기존 root main.py와 연결하는 경우

기존 자동화가 여전히 `python main.py`를 실행한다면, 두 가지 중 하나를 선택합니다.

### 선택 A: workflow에서 wrapper 실행

```bash
python run_main_with_event_boost.py
```

### 선택 B: main.py 최상단에 직접 추가

```python
from event_boost_runtime import apply_event_boost_env
apply_event_boost_env()
```

단, `main.py`가 환경변수를 import 시점에 읽는 구조라면 최대한 상단에 넣어야 합니다.
