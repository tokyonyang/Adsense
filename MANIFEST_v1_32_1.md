# v1.32.1 Complete Patch Manifest

## 긴급 수정

```text
weekday_ko 함수 누락으로 인한 Overnight Hot Issue Report 실패 수정
```

## 포함 workflow

```text
.github/workflows/daily-adsense-seo.yml
.github/workflows/morning-headline-news.yml
.github/workflows/adsense-dashboard-cron.yml
.github/workflows/telegram-send-test.yml
.github/workflows/overnight-hotissue-report.yml
```

## 핵심 수정 파일

```text
app/services/overnight_hotissue_service.py
.github/workflows/overnight-hotissue-report.yml
```
