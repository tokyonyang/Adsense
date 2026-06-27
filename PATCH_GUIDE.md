# v1.22 헤드라인 이미지 퀄리티 개선 + 뉴스 링크 포함 패치

## 교체할 파일

```text
app/services/telegram_photo_service.py
app/services/headline_news_image_service.py
app/jobs/send_headline_news_report.py
.github/workflows/morning-headline-news.yml
docs/morning_headline_premium_image_v1_22.md
```

## 핵심 개선

기존:
```text
Pillow로 사각형과 텍스트를 직접 그림
```

변경:
```text
HTML/CSS 프리미엄 템플릿 생성
Playwright로 고해상도 PNG 캡처
Telegram 전송
```

## 추가 개선

- 헤드라인 카드 10개 → 8개로 줄여 가독성 개선
- 카드 하단에 출처/원문 링크 영역 포함
- 텍스트 메시지에는 실제 원문 URL 포함
- `HEADLINE_IMAGE_SCALE=2`로 고해상도 렌더링
- `HEADLINE_SEND_AS_DOCUMENT=true` 설정 시 원본 화질 파일로 전송 가능

## 적용 후 테스트

```text
Actions
→ Morning Headline News Report
→ Run workflow
```

## 만약 텔레그램에서 이미지가 여전히 흐릿하면

workflow의 아래 값을 변경하세요.

```text
HEADLINE_SEND_AS_DOCUMENT: "true"
```

그러면 텔레그램이 이미지 압축을 덜 하고 파일 원본으로 보냅니다.
