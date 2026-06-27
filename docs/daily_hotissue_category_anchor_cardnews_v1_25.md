# v1.25 Daily Hot Issue 카테고리 균형 + Morning Cardnews 원천 통합

## 문제

Daily AdSense SEO Hot Issue Report와 Morning Headline News Report가 서로 다른 뉴스 수집 로직으로 움직여 결과가 달라졌습니다.
또한 Daily Hot Issue TOP 10이 특정 분야에 쏠리거나 대부분 `기타`로 분류되는 문제가 있었습니다.

## 수정 방향

1. Daily Hot Issue를 마스터 데이터로 사용
2. Morning Headline Cardnews는 Daily Hot Issue TOP Item을 기준으로 생성
3. Daily Hot Issue TOP 10은 카테고리별 1~2개씩 균형 선정
4. 인명/작품명 키워드는 근거 기사 제목을 함께 보고 카테고리 보정

## 추가 카테고리

- 경제·금융
- 증권·투자
- 부동산·주거금융
- 정책·지원금
- 산업·기업
- 생활·제도
- 교육·입시
- 날씨·안전
- 시사·정치
- 사회·사건
- 건강·의료
- 연예·문화
- 스포츠
- 국제
- 기타

## 주요 환경변수

```text
HOT_ISSUE_CATEGORY_BALANCED=true
HOT_ISSUE_PER_CATEGORY_MAX=2
HOT_ISSUE_OTHER_MAX=1
CATEGORY_FILTER=all
```

## 검증 포인트

Daily 리포트 상단에 `카테고리 구성`이 표시됩니다.
Morning 카드뉴스 로그에는 `[daily-hotissue-cardnews result]`가 표시됩니다.
