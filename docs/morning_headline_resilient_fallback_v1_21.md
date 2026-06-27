# v1.21 아침 헤드라인 운영 안정화

## 문제

v1.20에서 최신성 필터를 강하게 걸자 후보가 0개일 때 workflow가 실패했습니다.

```text
[headline freshness] primary 24h candidates: 0
[headline freshness] fallback 48h candidates: 0
RuntimeError
```

## 수정

- 24시간 후보
- 48시간 후보
- 날짜 포함 쿼리 재검색
- 72시간 relaxed 후보
- 날짜 없는 최신 상단 후보 제한 사용
- 그래도 없으면 실패 대신 텍스트 안내 전송

## 오래된 뉴스 방지

날짜가 명확히 있고 72시간보다 오래된 뉴스는 최종 단계에서 제거합니다.

## 로그

```text
[headline freshness] primary 24h candidates:
[headline freshness] fallback 48h candidates:
[headline freshness] dated-query relaxed candidates:
[headline freshness] relaxed 72h candidates:
[headline freshness] undated fallback candidates:
[headline selected]
```
