# v1.8 경제지표 중복 제거 및 이벤트일 검색 강화

## 중복 제거 기준

대시보드와 SQL 모두 아래 기준으로 중복을 판단합니다.

```text
event_date + country + currency + normalized(event_name)
```

## 화면 표시 기준

중복이 있으면 하나만 표시하되, 아래 우선순위로 대표 데이터를 선택합니다.

1. `importance`가 높은 데이터
2. `actual_value`가 있는 데이터
3. `forecast_value`가 있는 데이터
4. `previous_value`가 있는 데이터
5. 최신 데이터

## 이벤트일 검색 강화

경제지표 중요도에 따라 자동 검색 수집량을 늘립니다.

| 중요도 | MAX_KEYWORDS | NEWS_LINKS_PER_TOPIC |
|---|---:|---:|
| 평상시 | 30 | 5 |
| high | 60 | 10 |
| critical | 80 | 15 |

## 검색어 확장 예시

### inflation

```text
물가, CPI, PCE, PPI, 금리, 환율, 국채금리, 연준, 달러, 나스닥
```

### rate

```text
기준금리, FOMC, 금통위, 연준, 달러, 채권금리, 환율, 증시
```

### employment

```text
고용, 실업률, 비농업고용, 임금, 금리인하, 달러, 미국증시
```
