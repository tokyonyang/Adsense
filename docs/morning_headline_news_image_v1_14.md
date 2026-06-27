# v1.14 아침 헤드라인 뉴스 이미지 자동 전송

## 핵심 기능

매일 아침 텔레그램으로 아래 2가지를 함께 전송합니다.

1. 카드형 요약 이미지(PNG)
2. 텍스트형 헤드라인 목록

## 실행 시간

```text
KST 06:10
```

UTC cron:

```text
10 21 * * *
```

기존 07:10보다 1시간 앞당겼습니다.

## 동작 흐름

1. Naver News API / Google News RSS로 헤드라인 수집
2. Gemini로 10개 뉴스의 짧은 제목/강조문구/요약 bullet 생성
3. Pillow로 카드형 뉴스 이미지 렌더링
4. 텔레그램 sendPhoto로 이미지 전송
5. 필요 시 텍스트 목록도 추가 전송

## 추가/교체 파일

```text
app/services/telegram_photo_service.py
app/services/headline_news_image_service.py
app/jobs/send_headline_news_report.py
.github/workflows/morning-headline-news.yml
```

## 필수 GitHub Secrets

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
NAVER_CLIENT_ID
NAVER_CLIENT_SECRET
GEMINI_API_KEY
```

## 수동 테스트

```text
Actions
→ Morning Headline News Report
→ Run workflow
```

정상이라면 카드형 이미지 + 텍스트 메시지가 함께 도착합니다.

## 옵션

텍스트 메시지를 같이 보내기 싫다면:

```text
HEADLINE_SEND_TEXT=false
```

로 변경하면 됩니다.
