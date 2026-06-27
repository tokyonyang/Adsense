# v1.28 적용 가이드

## 적용 파일

아래 파일을 GitHub에 업로드/교체하세요.

```text
main.py
app/services/daily_hotissue_engine.py
app/services/daily_hotissue_source.py
app/jobs/send_headline_cardnews_report.py
.github/workflows/daily-adsense-seo.yml
.github/workflows/morning-headline-news.yml
docs/EDITORIAL_ENGINE_v1_28.md
```

## 적용 후 테스트

### 1. Daily 테스트

```text
Actions
→ Daily AdSense SEO Hot Issue Report
→ Run workflow
```

정상 리포트에는 아래가 보입니다.

```text
🔥 오늘의 핫이슈 TOP 10

📊 오늘의 이슈 구성
슬롯 구성:
카테고리 구성:
편집 정책:
```

각 항목에는 아래 정보가 추가됩니다.

```text
왜 중요함:
글감 방향:
점수:
근거자료:
```

### 2. Morning 테스트

```text
Actions
→ Morning Headline News Report
→ Run workflow
```

정상 로그:

```text
[daily-hotissue-cardnews result]
source_items
issues_preview
```

## 슬롯 조정

더 강한 경제/금융형:

```yaml
HOT_ISSUE_SLOT_PLAN: "경제·금융:3,증권·투자:2,산업·기업:2,정책·생활:1,국제·안전:1,사회·시사:1"
HOT_ISSUE_NOISE_MAX: 0
```

대중 관심도 조금 더 반영:

```yaml
HOT_ISSUE_SLOT_PLAN: "경제·금융:2,증권·투자:2,산업·기업:2,정책·생활:1,국제·안전:1,사회·시사:1,대중관심:1"
HOT_ISSUE_NOISE_MAX: 1
```

Morning 카드뉴스에서 대중관심도 허용:

```yaml
HEADLINE_AVOID_SLOTS: ""
```
