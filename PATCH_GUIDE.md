# AdSense SEO 운영 대시보드 v1.7 패치

## 이번 버전 목표

모바일 사용성을 강화하고, 주요 경제지표 이벤트가 있는 날에 검색을 더 많이 해야 한다는 운영 요구를 화면에 반영했습니다.

## 추가 기능

### 1. 모바일 하단 빠른 메뉴

모바일 화면 하단에 아래 메뉴가 고정됩니다.

```text
홈
키워드
SNS
일정
로그
```

### 2. 경제지표 이벤트 검색 강화 큐

콘텐츠 캘린더 화면에 `경제지표 이벤트 검색 강화 큐`가 추가됩니다.

critical/high 이벤트가 있으면 다음 검색어를 자동 제안합니다.

```text
지표명
국가
물가
금리
환율
증시
국채금리
연준
```

### 3. 경제지표 모바일 카드형 뷰

모바일에서는 긴 표 대신 경제지표가 카드형으로 표시됩니다.

### 4. SNS 트렌드 모바일 카드형 뷰

모바일에서는 SNS 트렌드도 카드형으로 표시됩니다.

## GitHub에 업로드할 파일

```text
index.html
dashboard/index.html
vercel.json
docs/event_search_boost_logic_v1_7.md
```

`dashboard_config.js`는 건드리지 않습니다.

## 적용 후 확인

```text
https://gooddaynews.vercel.app/?v=17
```

## 다음 v1.8 추천

경제지표 이벤트일에 실제 자동 수집량을 늘리는 백엔드 로직을 연결합니다.

예:

```text
평상시: MAX_KEYWORDS=30 / NEWS_LINKS_PER_TOPIC=5
이벤트일: MAX_KEYWORDS=80 / NEWS_LINKS_PER_TOPIC=15
```

연결 대상:

```text
app/jobs/run_daily_pipeline.py
app/services/keyword_service.py
economic_events 테이블
```
