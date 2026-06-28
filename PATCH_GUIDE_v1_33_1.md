# v1.33.1 적용 가이드

## 적용 파일

```text
.github/workflows/daily-adsense-seo.yml
.github/workflows/overnight-hotissue-report.yml
.github/workflows/morning-headline-news.yml
.github/workflows/adsense-dashboard-cron.yml
.github/workflows/telegram-send-test.yml

docs/SCHEDULE_HUB_v1_33_1.md
PATCH_GUIDE_v1_33_1.md
MANIFEST_v1_33_1.md
```

## 적용 후 확인

GitHub Actions에는 아래 workflow가 그대로 보여야 합니다.

```text
Daily AdSense SEO Hot Issue Report
Overnight Hot Issue Report
Morning Headline News Report
AdSense Dashboard Pipeline Report
Telegram Send Test
```

다만 자동 실행 이력은 아래 workflow에 집중됩니다.

```text
Daily AdSense SEO Hot Issue Report
```

## 테스트 방법

```text
Actions
→ Daily AdSense SEO Hot Issue Report
→ Run workflow
→ report_type 선택
```

선택 가능:

```text
daily
overnight
morning
```

## 내일 자동 실행 확인

```text
05:30 KST → Daily AdSense SEO Hot Issue Report 이력에 overnight 실행
06:07 KST → Daily AdSense SEO Hot Issue Report 이력에 daily 실행
06:10 KST → Daily AdSense SEO Hot Issue Report 이력에 morning 실행
```
