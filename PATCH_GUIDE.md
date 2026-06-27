# v1.11 Workflow 스케줄 분리 패치

## 요청 반영 내용

두 종류의 텔레그램 메시지를 모두 실행하도록 구성했습니다.

```text
1. Daily AdSense SEO 핫이슈 리포트
2. 새 대시보드 파이프라인 리포트
```

단, 새 대시보드 파이프라인은 한국시간 오전 9시와 오후 5시에만 전송되도록 설정했습니다.

## GitHub에 업로드/교체할 파일

```text
.github/workflows/daily-adsense-seo.yml
.github/workflows/adsense-dashboard-cron.yml
.github/workflows/telegram-send-test.yml
docs/workflow_schedule_v1_11.md
```

## 스케줄

### 1. Daily AdSense SEO Hot Issue Report

기존 핫이슈 리포트입니다.

```text
KST 06:00 / 11:00 / 15:00 / 19:00
```

cron:

```text
0 21,2,6,10 * * *
```

전송 메시지 형태:

```text
🔥 오늘의 핫이슈 TOP 10
```

### 2. AdSense Dashboard Pipeline Report

새 대시보드 파이프라인 리포트입니다.

```text
KST 09:00 / 17:00
```

cron:

```text
0 0,8 * * *
```

전송 메시지 형태:

```text
🤖 AdSense SEO 자동 수집 리포트
📊 경제지표 검색 강화 상태
```

## 적용 후 확인

GitHub Actions 화면에서 아래 3개 workflow가 보여야 합니다.

```text
Daily AdSense SEO Hot Issue Report
AdSense Dashboard Pipeline Report
Telegram Send Test
```

## 수동 테스트 순서

1. 텔레그램 연결 테스트

```text
Actions
→ Telegram Send Test
→ Run workflow
```

2. 기존 핫이슈 리포트 테스트

```text
Actions
→ Daily AdSense SEO Hot Issue Report
→ Run workflow
```

3. 대시보드 파이프라인 테스트

```text
Actions
→ AdSense Dashboard Pipeline Report
→ Run workflow
```

## 중복 전송 주의

기존에 `daily-adsense-seo.yml` 또는 `adsense-dashboard-cron.yml` 외에 다른 workflow가 `main.py`나 `app.jobs.run_daily_pipeline`을 실행하고 있으면 메시지가 중복될 수 있습니다.

Actions 목록에서 비슷한 workflow가 있으면 이름과 스케줄을 확인하세요.
