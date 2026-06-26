# v1.7 경제지표 이벤트 검색 강화 로직

## 목적

중요 경제지표가 있는 날에는 해당 이벤트를 중심으로 검색량과 뉴스 수집량을 늘립니다.

## 강화 대상

아래 조건 중 하나에 해당하면 검색 강화 큐에 포함합니다.

```text
importance = critical
importance = high
content_usage = article
content_usage = cardnews
content_usage = telegram
content_usage = followup
```

## 예시

### 미국 CPI / PCE

검색어 확장:

```text
CPI
PCE
물가
금리
환율
국채금리
연준
달러
나스닥
S&P500
```

### FOMC / 기준금리

검색어 확장:

```text
FOMC
기준금리
연준
금리인하
달러
채권금리
환율
증시
```

### 고용지표

검색어 확장:

```text
비농업고용
실업률
임금상승률
고용시장
금리인하
달러
미국증시
```

## 추천 자동화 정책

경제지표 발표일 기준:

```text
D-1: 사전 전망 검색 강화
D-Day: 발표 전/후 검색 강화
D+1: 시장 반응과 후속 해설 검색 강화
```

## 추천 수집량

평상시:

```text
NEWS_LINKS_PER_TOPIC=5
MAX_KEYWORDS=30
```

경제지표 이벤트일:

```text
NEWS_LINKS_PER_TOPIC=10~15
MAX_KEYWORDS=50~80
LOOKBACK_HOURS=12 또는 24
```

## 향후 백엔드 연결 방향

GitHub Actions 또는 Python 자동화에서 economic_events 테이블을 조회한 뒤,
오늘 또는 내일 critical/high 이벤트가 있으면 수집 파라미터를 자동 상향합니다.

의사코드:

```python
events = get_today_major_economic_events()

if events:
    max_keywords = 80
    news_links_per_topic = 15
    include_event_keywords = True
else:
    max_keywords = 30
    news_links_per_topic = 5
```
