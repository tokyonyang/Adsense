# v1.14 아침 헤드라인 뉴스 이미지 자동화 패치

## 요청 반영 사항

- 아침 헤드라인 뉴스를 텔레그램으로 보낼 때
  - 관련 카드형 이미지도 함께 생성해서 전송
- 실행 시간을 기존 07:10 → 06:10 으로 1시간 앞당김

## 업로드/교체할 파일

```text
app/services/telegram_photo_service.py
app/services/headline_news_image_service.py
app/jobs/send_headline_news_report.py
.github/workflows/morning-headline-news.yml
docs/morning_headline_news_image_v1_14.md
```

## 실행 시간

```text
Morning Headline News Report
→ KST 06:10
```

## 전송 결과

텔레그램으로 아래 순서로 전송됩니다.

1. 카드형 헤드라인 뉴스 이미지
2. 텍스트 헤드라인 뉴스 목록

## 이미지 특징

- 검정/골드 계열 뉴스 카드 레이아웃
- 10개 뉴스 타일 구성
- 날짜 표시
- 핵심 키워드 footer
- Gemini 요약 기반 short title / bullet summary

## 필요한 환경

GitHub Actions workflow에서 자동으로 아래를 설치합니다.

```text
fonts-nanum
requests
feedparser
pillow
python-dotenv
google-generativeai
```

## 수동 테스트

```text
Actions
→ Morning Headline News Report
→ Run workflow
```

## 참고

Gemini 요약이 실패하면 제목 기반 fallback 요약으로 이미지를 계속 생성합니다.
