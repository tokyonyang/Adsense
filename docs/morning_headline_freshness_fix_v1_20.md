# v1.20 아침 헤드라인 최신성 강제 필터

## 문제

06/27 리포트에 05/14, 04/07, 03/24 같은 오래된 뉴스가 섞였습니다.

## 원인

기존 로직이 최근 뉴스가 부족하다고 판단하면 오래된 candidates를 다시 허용했습니다.

## 수정

- 24시간 이내 뉴스 우선
- 부족하면 48시간까지만 확장
- 48시간보다 오래된 뉴스는 절대 사용하지 않음
- 부족하면 부족한 개수 그대로 전송
- 후보가 없으면 workflow 실패 처리
- Actions 로그에 freshness 후보 수 출력

## 로그 예시

```text
[headline freshness] primary 24h candidates: 18
[headline freshness] fallback 48h candidates: 7
[headline selected] 10
```

## 기대 효과

이미지와 텍스트 모두 최근 24~48시간 이내 뉴스만 사용합니다.
