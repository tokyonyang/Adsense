# v1.23 아침 헤드라인 카드뉴스 자동화

## 핵심 변경

기존 한 장짜리 헤드라인 이미지 대신, 텔레그램 카드뉴스 앨범으로 전송합니다.

## 구성

기본 7장 구성입니다.

1. 표지
2. 이슈 1
3. 이슈 2
4. 이슈 3
5. 이슈 4
6. 이슈 5
7. 마무리 요약

## 핵심 로직

1. 뉴스 기사 수집
2. 최근 48시간 필터
3. 유사 기사 클러스터링
4. 각 클러스터별 대표 이슈 생성
5. 유사 기사 3건 기반 3줄 요약
6. HTML/CSS 프리미엄 카드뉴스 렌더링
7. 텔레그램 media group 전송
8. 원문 링크 텍스트 메시지 별도 전송

## 새 파일

```text
app/services/headline_cluster_service.py
app/services/headline_cardnews_summary_service.py
app/services/headline_cardnews_render_service.py
app/services/telegram_album_service.py
app/jobs/send_headline_cardnews_report.py
.github/workflows/morning-headline-news.yml
```

## 주요 환경변수

```text
HEADLINE_LOOKBACK_HOURS=48
HEADLINE_CARDNEWS_ISSUES=5
HEADLINE_MIN_CLUSTER_SIZE=2
HEADLINE_CLUSTER_THRESHOLD=0.24
HEADLINE_IMAGE_SCALE=2
HEADLINE_SEND_LINK_DIGEST=true
```

## 수동 테스트

```text
Actions
→ Morning Headline News Report
→ Run workflow
```

정상이라면 텔레그램에 카드뉴스 이미지 앨범과 원문 링크 메시지가 도착합니다.
