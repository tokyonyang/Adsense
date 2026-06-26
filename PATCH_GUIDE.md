# AdSense SEO 운영 대시보드 v1.8 패치

## 이번 버전 목표

경제지표가 중복으로 표시되는 문제를 수정하고, 주요 경제지표 이벤트일에는 검색량을 늘리는 다음 단계 백엔드 파일을 추가했습니다.

## 핵심 변경

### 1. 경제지표 중복 표시 방지

같은 아래 조건이면 화면에서는 1개만 표시합니다.

```text
event_date
country
currency
event_name
```

중복 중에서는 아래 우선순위로 하나를 선택합니다.

```text
1. importance가 높은 데이터
2. actual_value가 있는 데이터
3. forecast_value / previous_value가 있는 데이터
4. 최신 updated_at / created_at 데이터
```

### 2. 검색 강화 큐도 중복 제거

경제지표 검색 강화 큐에서도 같은 이벤트가 여러 번 나오지 않도록 수정했습니다.

### 3. Supabase 중복 정리 SQL 추가

```text
supabase/economic_events_dedupe_v1_8.sql
```

이 SQL은 기존 중복 데이터를 정리하고, 앞으로 중복 입력을 막는 unique index를 추가합니다.

### 4. 백엔드 이벤트 검색량 강화 파일 추가

```text
app/services/event_boost_service.py
app/jobs/run_event_boost_preview.py
```

경제지표 이벤트가 있으면 아래처럼 수집량을 올릴 수 있게 준비했습니다.

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

## GitHub에 업로드할 파일

```text
index.html
dashboard/index.html
vercel.json
supabase/economic_events_dedupe_v1_8.sql
app/services/event_boost_service.py
app/jobs/run_event_boost_preview.py
docs/event_dedupe_and_boost_v1_8.md
```

`dashboard_config.js`는 건드리지 않습니다.

## 적용 순서

1. GitHub에 파일 업로드/교체
2. Supabase SQL Editor에서 아래 파일 실행

```text
supabase/economic_events_dedupe_v1_8.sql
```

3. Vercel 배포 후 확인

```text
https://gooddaynews.vercel.app/?v=18
```

4. 경제지표 일정에서 중복이 1개로 병합되는지 확인

## 백엔드 미리보기 실행

GitHub Actions 또는 로컬에서 아래 명령으로 이벤트일 수집 강화 판단을 확인할 수 있습니다.

```bash
python -m app.jobs.run_event_boost_preview
```

## 다음 v1.9 추천

이제 미리보기 수준이 아니라 실제 키워드 수집 파이프라인에 `event_boost_config`를 연결합니다.

연결 대상:

```text
app/jobs/run_daily_pipeline.py
app/services/keyword_service.py
trend_sources.py
news_sources.py
```
