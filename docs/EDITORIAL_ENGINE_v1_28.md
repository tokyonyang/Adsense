# v1.28 Daily Hot Issue Editorial Engine

## 목적

v1.27까지는 구조 안정화가 핵심이었고, 실제 뉴스 큐레이션 품질은 아직 약했습니다.  
v1.28은 Daily HOT Issue를 단순 트렌드 수집기가 아니라 `편집 데스크형 큐레이션 엔진`으로 바꾸는 패치입니다.

## 핵심 변경

기존:

```text
트렌드 키워드 수집
→ 근거 기사 수집
→ 카테고리 분류
→ 점수순/경제 우선 정렬
```

변경:

```text
트렌드 키워드 + 경제 seed 수집
→ 근거 기사 수집
→ 카테고리 분류
→ 트렌드 점수 / 근거 점수 / 신선도 점수 / 애드센스 글감 점수 / 편집 중요도 / 노이즈 감점
→ 카테고리 슬롯에 맞춰 TOP 10 선발
→ Morning 카드뉴스용 이슈 별도 선별
```

## 기본 TOP 10 슬롯

```yaml
HOT_ISSUE_SLOT_PLAN: "경제·금융:2,증권·투자:2,산업·기업:2,정책·생활:1,국제·안전:1,사회·시사:1,대중관심:1"
```

출력 구성:

```text
경제·금융 2개
증권·투자 2개
산업·기업 2개
정책·생활 1개
국제·안전 1개
사회·시사 1개
대중관심 1개
```

## 노이즈 감점

아래 유형은 감점됩니다.

```text
로또
포토뉴스
오늘의 운세
열애설
단순 방송 캡처
스포츠 단순 경기 결과
연예 가십
기타성 키워드
```

단, 완전 제외하지 않고 `대중관심` 슬롯 1개 안에서만 허용합니다.

## 애드센스 글감 점수

높게 평가되는 요소:

```text
환율
금리
물가
대출
부동산
전기요금
가스요금
지원금
소상공인
정책
세금
보험
연금
건강
교육
주식
반도체
전기차
AI
관세
유가
```

## Daily 리포트 개선

각 항목에 아래가 추가됩니다.

```text
왜 중요함
글감 방향
편집점수 / 글감점수 / 노이즈점수
주의 신호
근거자료
```

## Morning 카드뉴스 개선

Morning은 Daily TOP 10을 그대로 복사하지 않고, Daily 결과 중에서 카드뉴스에 적합한 이슈만 고릅니다.

기본 선호 슬롯:

```yaml
HEADLINE_PREFER_SLOTS: "경제·금융,증권·투자,산업·기업,정책·생활,국제·안전,사회·시사"
HEADLINE_AVOID_SLOTS: "대중관심"
HEADLINE_CARDNEWS_MIN_EDITORIAL_SCORE: 40
```

## 주요 파일

```text
main.py
app/services/daily_hotissue_engine.py
app/services/daily_hotissue_source.py
app/jobs/send_headline_cardnews_report.py
.github/workflows/daily-adsense-seo.yml
.github/workflows/morning-headline-news.yml
docs/EDITORIAL_ENGINE_v1_28.md
```

## 테스트 순서

1. Daily 수동 실행

```text
Actions
→ Daily AdSense SEO Hot Issue Report
→ Run workflow
```

2. Telegram 리포트에서 확인

```text
📊 오늘의 이슈 구성
슬롯 구성:
카테고리 구성:
편집 정책:
```

3. Morning 수동 실행

```text
Actions
→ Morning Headline News Report
→ Run workflow
```

4. 카드뉴스 기준 이슈가 Daily의 경제/금융·증권·산업·정책 이슈 위주인지 확인
