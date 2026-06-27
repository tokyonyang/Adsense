# v1.23 헤드라인 카드뉴스형 자동화 패치

## 적용 목표

아침 헤드라인 뉴스를 한 장짜리 이미지가 아니라, 카드뉴스 6~7장 구조로 자동 생성해 텔레그램에 전송합니다.

## 업로드/교체 파일

```text
app/services/headline_cluster_service.py
app/services/headline_cardnews_summary_service.py
app/services/headline_cardnews_render_service.py
app/services/telegram_album_service.py
app/jobs/send_headline_cardnews_report.py
.github/workflows/morning-headline-news.yml
docs/morning_headline_cardnews_v1_23.md
```

## 전송 방식

- 표지 1장
- 이슈 카드 5장
- 마무리 요약 1장
- 텔레그램 media group으로 앨범 전송
- 마지막에 원문 링크 텍스트 메시지 전송

## 핵심 개선

- 유사 기사 3개를 하나의 이슈로 묶음
- 중복 이슈는 하나만 반영
- 이슈당 3줄 요약
- 이미지 한 장에 너무 많은 정보를 넣지 않음
- 원문 링크 포함
- 디자인은 블랙/골드 프리미엄 카드뉴스 스타일

## 테스트

```text
Actions
→ Morning Headline News Report
→ Run workflow
```

## 확인할 로그

```text
[cardnews articles]
[cardnews result]
articles
clusters
issues
pages
issues_preview
```

## 조정 가능한 값

더 많은 이슈를 보내고 싶으면:

```yaml
HEADLINE_CARDNEWS_ISSUES: 6
```

더 유사한 기사끼리만 묶고 싶으면:

```yaml
HEADLINE_CLUSTER_THRESHOLD: "0.30"
```

너무 묶이지 않으면:

```yaml
HEADLINE_CLUSTER_THRESHOLD: "0.20"
```
