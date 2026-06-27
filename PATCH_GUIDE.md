# v1.25 적용 가이드

## 핵심 변경

이번 패치는 두 가지를 동시에 수정합니다.

1. **Daily Hot Issue TOP 10을 카테고리별 1~2개씩 균형 선정**
2. **Morning Headline Cardnews를 Daily Hot Issue TOP Item 기준으로 생성**

## 교체/추가 파일

```text
main.py
.github/workflows/daily-adsense-seo.yml
.github/workflows/morning-headline-news.yml
app/services/daily_hotissue_source.py
app/services/headline_cardnews_summary_service.py
app/services/headline_cardnews_render_service.py
app/services/telegram_album_service.py
app/jobs/send_headline_cardnews_report.py
docs/daily_hotissue_category_anchor_cardnews_v1_25.md
```

## Daily 리포트 개선

기존에는 전체 점수 TOP 10만 사용해 로또/스포츠/연예 등 특정 분야가 쏠릴 수 있었습니다.
이제 기본값은 아래와 같습니다.

```text
HOT_ISSUE_CATEGORY_BALANCED=true
HOT_ISSUE_PER_CATEGORY_MAX=2
HOT_ISSUE_OTHER_MAX=1
```

즉, 카테고리별 상위 항목을 1~2개씩 뽑고, 기타는 최대 1개만 노출합니다.

## Morning 리포트 개선

기존 Morning Headline은 별도 뉴스 수집 결과를 사용했습니다.
이제는 Daily Hot Issue와 같은 수집/분류/균형선정 함수를 호출합니다.

```text
Daily HOT Issue TOP Item
→ Morning Headline Cardnews
```

## 테스트 순서

1. `Daily AdSense SEO Hot Issue Report` 수동 실행
2. 텔레그램 리포트의 `카테고리 구성` 확인
3. `Morning Headline News Report` 수동 실행
4. 카드뉴스의 이슈가 Daily HOT Issue TOP Item 기준인지 확인

## 확인 로그

Daily:

```text
오늘의 핫이슈 TOP 10
카테고리 구성: ...
```

Morning:

```text
[daily-hotissue-cardnews result]
category_mix
issues_preview
```
