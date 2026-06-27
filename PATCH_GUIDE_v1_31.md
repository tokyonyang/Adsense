# v1.31 적용 가이드

## 적용 파일

```text
app/services/headline_cardnews_render_service.py

.github/workflows/daily-adsense-seo.yml
.github/workflows/morning-headline-news.yml
.github/workflows/adsense-dashboard-cron.yml
.github/workflows/telegram-send-test.yml

docs/CARDNEWS_LAYOUT_v1_31.md
PATCH_GUIDE_v1_31.md
```

## workflow 누락 방지

이번 패치에는 workflow 4개를 반드시 포함했습니다.

```text
.github/workflows/daily-adsense-seo.yml
.github/workflows/morning-headline-news.yml
.github/workflows/adsense-dashboard-cron.yml
.github/workflows/telegram-send-test.yml
```

## 테스트

```text
Actions
→ Morning Headline News Report
→ Run workflow
```

확인할 것:

```text
- 커버가 프리미엄 경제 브리핑 스타일로 나오는지
- 본문 카드가 차트/요약/인사이트/출처 패널로 분리되는지
- 하단 브랜드가 gooddaynews.store인지
- "비티의 인사이트 노트" 문구가 사라졌는지
```
