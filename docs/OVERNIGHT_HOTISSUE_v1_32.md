# v1.32 간밤의 핫이슈 리포트

## 목적

기존 Morning Headline News와 별도로, 매일 한국시각 새벽 5시 30분에 `간밤의 핫이슈`를 전송합니다.

## 발행 정보

```text
제목: 간밤의 핫이슈(카테고리 무관)
발행시각: 한국시각 새벽 5시 30분
전송 형태: 텍스트 리포트 + 카드뉴스 이미지
```

## 구성

```text
1. 미국뉴스 주요 이슈
2. 미증시 요약
3. 국내뉴스 아침 이슈
4. 간밤의 인기 키워드 & 트렌드
5. 실시간 급상승 키워드 순위
6. 오늘의 지역별 날씨
7. 오늘의 명언 한줄
```

## 신규 파일

```text
app/services/overnight_hotissue_service.py
app/services/overnight_cardnews_render_service.py
app/jobs/send_overnight_hotissue_report.py
.github/workflows/overnight-hotissue-report.yml
```

## 스케줄

```yaml
- cron: "30 20 * * *"
```

이는 한국시각 05:30입니다.

## 데이터 소스

```text
미국뉴스: Google News RSS(US)
국내뉴스: Naver News API + Google News RSS
미증시: Yahoo Finance chart endpoint
키워드/트렌드: Google Trends RSS + 보조 뉴스 추출
날씨: Open-Meteo forecast + air-quality API
명언: 내장 quote list
```

## 필요 Secrets

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
NAVER_CLIENT_ID
NAVER_CLIENT_SECRET
GEMINI_API_KEY
```

Gemini가 없으면 기본 요약 로직으로 fallback 됩니다.

## Actions 확인

업로드 후 GitHub Actions에 아래 항목이 추가되어야 합니다.

```text
Overnight Hot Issue Report
```
