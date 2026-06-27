# v1.11 Workflow Schedule Split

## 목적

기존 핫이슈 리포트와 새 대시보드 파이프라인 리포트를 둘 다 운영하되, 발송 시간을 분리합니다.

## 운영 스케줄

| Workflow | 용도 | KST 실행 시각 | UTC cron |
|---|---|---:|---|
| `daily-adsense-seo.yml` | 기존 핫이슈 TOP 10 리포트 | 06:00 / 11:00 / 15:00 / 19:00 | `0 21,2,6,10 * * *` |
| `adsense-dashboard-cron.yml` | 대시보드/경제지표 이벤트 부스트 리포트 | 09:00 / 17:00 | `0 0,8 * * *` |
| `telegram-send-test.yml` | 텔레그램 연결 수동 테스트 | 수동 실행 | 없음 |

## 메시지 구분

### Daily AdSense SEO

```text
🔥 오늘의 핫이슈 TOP 10
```

### Dashboard Pipeline

```text
🤖 AdSense SEO 자동 수집 리포트
📊 경제지표 검색 강화 상태
```

## 주의

GitHub Actions cron은 UTC 기준입니다.

```text
KST = UTC + 9
KST 09:00 = UTC 00:00
KST 17:00 = UTC 08:00
```
