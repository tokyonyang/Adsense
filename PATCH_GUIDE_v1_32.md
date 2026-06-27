# v1.32 적용 가이드

## 적용 파일

```text
app/services/overnight_hotissue_service.py
app/services/overnight_cardnews_render_service.py
app/jobs/send_overnight_hotissue_report.py

.github/workflows/overnight-hotissue-report.yml

docs/OVERNIGHT_HOTISSUE_v1_32.md
PATCH_GUIDE_v1_32.md
```

이번 패치에는 기존 workflow도 누락 방지를 위해 함께 포함했습니다.

```text
.github/workflows/daily-adsense-seo.yml
.github/workflows/morning-headline-news.yml
.github/workflows/adsense-dashboard-cron.yml
.github/workflows/telegram-send-test.yml
```

## 테스트

```text
Actions
→ Overnight Hot Issue Report
→ Run workflow
```

정상 결과:

```text
1. 텔레그램 텍스트 리포트 전송
2. 카드뉴스 이미지 7장 전송
3. 로그에 [overnight-hotissue result] 표시
```

## 발행 시간

```text
한국시각 05:30
```

workflow cron:

```yaml
- cron: "30 20 * * *"
```
