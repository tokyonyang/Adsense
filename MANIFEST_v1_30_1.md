# v1.30.1 Complete Patch Manifest

이 패치는 `.github/workflows` 누락 문제를 방지하기 위해 workflow 파일을 강제로 포함한 완전 패치입니다.

## 반드시 포함된 workflow 파일

```text
.github/workflows/daily-adsense-seo.yml
.github/workflows/morning-headline-news.yml
.github/workflows/adsense-dashboard-cron.yml
.github/workflows/telegram-send-test.yml
```

## 핵심 실행 구조

```text
Daily AdSense SEO Hot Issue Report
→ main.py
→ app/services/daily_hotissue_engine.py
→ reports/latest_daily_hotissue.json 저장
→ Telegram 텍스트 리포트 전송

Morning Headline News Report
→ app/jobs/send_headline_cardnews_report.py
→ Daily HOT Issue 결과 기반 카드뉴스 생성
→ Telegram 카드뉴스 앨범 + 원문 링크 전송
```

## 적용 방법

ZIP 압축을 풀고, 폴더 구조 그대로 GitHub 저장소에 업로드/교체하세요.

특히 아래 폴더가 GitHub에 반드시 보여야 합니다.

```text
.github
└── workflows
    ├── daily-adsense-seo.yml
    ├── morning-headline-news.yml
    ├── adsense-dashboard-cron.yml
    └── telegram-send-test.yml
```

## 확인 방법

GitHub Actions 왼쪽 목록에 아래 항목이 보여야 합니다.

```text
Daily AdSense SEO Hot Issue Report
Morning Headline News Report
AdSense Dashboard Pipeline Report
Telegram Send Test
```

## 누락 파일 검사 결과

누락된 파일:

```text
없음
```
