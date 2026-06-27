# v1.32.1 적용 가이드

## 적용 파일

```text
app/services/overnight_hotissue_service.py

.github/workflows/overnight-hotissue-report.yml
.github/workflows/daily-adsense-seo.yml
.github/workflows/morning-headline-news.yml
.github/workflows/adsense-dashboard-cron.yml
.github/workflows/telegram-send-test.yml

docs/OVERNIGHT_HOTISSUE_FIX_v1_32_1.md
PATCH_GUIDE_v1_32_1.md
MANIFEST_v1_32_1.md
```

## 이번 수정으로 해결되는 문제

```text
NameError: name 'weekday_ko' is not defined
```

## 업로드 후 테스트

```text
Actions
→ Overnight Hot Issue Report
→ Run workflow
```

## workflow 누락 확인

GitHub Actions에 아래 항목이 보여야 합니다.

```text
Daily AdSense SEO Hot Issue Report
Morning Headline News Report
AdSense Dashboard Pipeline Report
Telegram Send Test
Overnight Hot Issue Report
```
