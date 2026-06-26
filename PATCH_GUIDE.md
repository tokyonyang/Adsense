# AdSense SEO 운영 대시보드 v1.9 패치

## 이번 단계

경제지표 이벤트일에 자동 검색량을 실제 파이프라인에 반영합니다.

## GitHub에 업로드/교체할 파일

```text
app/services/event_boost_service.py
app/services/keyword_service.py
app/jobs/run_daily_pipeline.py
app/jobs/run_event_boost_preview.py
.github/workflows/adsense-dashboard-cron.yml
event_boost_runtime.py
run_main_with_event_boost.py
docs/event_boost_pipeline_v1_9.md
```

## 핵심 동작

`economic_events`에 주요 이벤트가 있으면 자동으로 수집량이 바뀝니다.

```text
평상시:
MAX_KEYWORDS=30
NEWS_LINKS_PER_TOPIC=5

high 이벤트:
MAX_KEYWORDS=60
NEWS_LINKS_PER_TOPIC=10

critical 이벤트:
MAX_KEYWORDS=80
NEWS_LINKS_PER_TOPIC=15
```

## 적용 전 확인

Supabase에 아래 테이블이 있어야 합니다.

```text
economic_events
trend_keywords
dashboard_runs
```

GitHub Secrets에는 아래가 있어야 합니다.

```text
SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY
```

## 적용 후 테스트

GitHub Actions에서 수동 실행:

```text
Actions
→ AdSense Dashboard Cron
→ Run workflow
```

또는 로컬/Actions 로그에서:

```bash
python -m app.jobs.run_event_boost_preview
python -m app.jobs.run_daily_pipeline
```

## 주의

이번 패치는 dashboard 화면 파일은 건드리지 않습니다.
`dashboard_config.js`도 건드리지 않습니다.

## 기존 main.py 자동화도 같이 쓰는 경우

기존 GitHub Actions가 `python main.py`를 실행하고 있다면 아래 중 하나를 선택해야 합니다.

### 방법 1. wrapper 사용

기존:

```bash
python main.py
```

변경:

```bash
python run_main_with_event_boost.py
```

### 방법 2. main.py 최상단에 직접 추가

```python
from event_boost_runtime import apply_event_boost_env
apply_event_boost_env()
```

이렇게 하면 기존 main.py가 읽는 `MAX_KEYWORDS`, `NEWS_LINKS_PER_TOPIC`, `LOOKBACK_HOURS` 환경변수가 이벤트일에 자동으로 상향됩니다.
