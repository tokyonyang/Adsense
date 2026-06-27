# AdSense 자동화 최종 통합본 v1.15

이 통합본은 아래 4개 자동화 흐름을 한 번에 정리한 최종본입니다.

## 1) Morning Headline News Report
- KST 06:10
- 카드형 헤드라인 이미지 + 텍스트 전송

## 2) Daily AdSense SEO Hot Issue Report
- KST 06:07 / 11:07 / 15:07 / 19:07
- 기존 `🔥 오늘의 핫이슈 TOP 10` 전송

## 3) AdSense Dashboard Pipeline Report
- KST 09:17 / 17:17
- 운영자용 대시보드/경제지표 강화 리포트 전송

## 4) Telegram Send Test
- 수동 테스트용

---

## GitHub에 업로드할 파일

```text
.github/workflows/daily-adsense-seo.yml
.github/workflows/adsense-dashboard-cron.yml
.github/workflows/morning-headline-news.yml
.github/workflows/telegram-send-test.yml

app/services/telegram_report_service.py
app/services/telegram_photo_service.py
app/services/headline_news_image_service.py

app/jobs/send_telegram_test.py
app/jobs/run_daily_pipeline.py
app/jobs/send_headline_news_report.py
```

> 주의: `app.services.event_boost_service`, `app.services.keyword_service`, `app.services.sns_trend_service`, `app.jobs.run_event_boost_preview`, `main.py` 는 기존 레포에 이미 있어야 합니다.

---

## 필수 GitHub Secrets

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
NAVER_CLIENT_ID
NAVER_CLIENT_SECRET
GEMINI_API_KEY
SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY
WP_BASE_URL
WP_USERNAME
WP_APP_PASSWORD
```

---

## Actions에 보여야 하는 workflow 목록

```text
Morning Headline News Report
Daily AdSense SEO Hot Issue Report
AdSense Dashboard Pipeline Report
Telegram Send Test
```
