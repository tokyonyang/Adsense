# v1.33.1 Complete Patch Manifest

## 목적

새벽/아침 브리핑 schedule 미실행 문제를 줄이기 위해 Daily workflow를 스케줄 허브로 전환했습니다.

## 포함 workflow

```text
.github/workflows/daily-adsense-seo.yml
.github/workflows/overnight-hotissue-report.yml
.github/workflows/morning-headline-news.yml
.github/workflows/adsense-dashboard-cron.yml
.github/workflows/telegram-send-test.yml
```

## 핵심 변경

```text
1. Daily workflow가 overnight / daily / morning 실행을 모두 담당
2. Overnight workflow는 수동 실행 전용
3. Morning workflow는 수동 실행 전용
4. 중복 자동 발송 방지
```
