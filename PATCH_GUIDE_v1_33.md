# v1.33 적용 가이드

## 적용 파일

```text
app/services/overnight_hotissue_service.py
app/services/overnight_cardnews_render_service.py
app/jobs/send_overnight_hotissue_report.py

.github/workflows/overnight-hotissue-report.yml
.github/workflows/daily-adsense-seo.yml
.github/workflows/morning-headline-news.yml
.github/workflows/adsense-dashboard-cron.yml
.github/workflows/telegram-send-test.yml

docs/OVERNIGHT_LINKS_SNS_v1_33.md
PATCH_GUIDE_v1_33.md
MANIFEST_v1_33.md
```

## 테스트

```text
Actions
→ Overnight Hot Issue Report
→ Run workflow
```

정상 결과:

```text
1. 텔레그램 텍스트 리포트가 전송됨
2. 링크가 많으면 텍스트가 2개 이상으로 자동 분할됨
3. 카드뉴스 이미지 8장이 전송됨
4. 로그에 [overnight-hotissue result] 표시
5. 로그에 sns_trends 개수가 표시됨
```

## 확인 포인트

```text
- 미국뉴스 이슈 아래 근거 링크가 있는지
- 미증시 지표에 Yahoo Finance 링크가 있는지
- 국내뉴스 이슈 아래 근거 링크가 있는지
- 인기 키워드/급상승 키워드에 관련 기사 링크가 있는지
- SNS별 트렌드 섹션이 추가되었는지
```
