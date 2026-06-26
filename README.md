# AdSense SEO 자동화 스타터

트렌드 키워드를 수집하고, 텔레그램으로 **오늘의 핫이슈 / 오늘의 카드뉴스 / 오늘의 작성글 후보**를 보내는 자동화 패키지입니다. 기본값은 경제·금융 관련 아이템만 우선 활용하며, 긴 글 초안은 미리 생성하지 않습니다.

## 이번 수정 사항 v8

- 전체 후보를 **조회수 많은 순**으로 정렬합니다.
- 텔레그램 리포트 구조를 아래 3개 섹션으로 바꿨습니다.
  - `🔥 오늘의 핫이슈`: 조회수 높은 순으로 TOP 10 정리
  - `🃏 오늘의 카드뉴스`: 카드뉴스로 만들기 좋은 항목 TOP 3 추천
  - `✍️ 오늘의 작성글`: 블로그/워드프레스 글로 작성하기 좋은 항목 TOP 3 추천
- 대상 항목마다 뒷받침할 수 있는 **관련 신문 기사 링크**를 함께 붙입니다.
- 기사 URL 원문은 노출하지 않고 `링크1` ~ `링크5` 클릭 라벨로 표시합니다.
- Google Trends RSS의 `20K+`, `1M+`, `2만+` 같은 조회수 표현을 숫자로 변환해 정렬합니다.
- 수동/seed 키워드처럼 조회수 정보가 없는 항목은 하단으로 밀립니다.

## 기본 실행

```bash
pip install -r requirements.txt
cp .env.example .env
python main.py --max-keywords 30 --max-posts 10 --category-filter finance
```

기본값은 아래와 같습니다.

```text
MAX_KEYWORDS=30
MAX_POSTS_PER_RUN=10
ITEM_LIST_ONLY=true
NEWS_LINKS_PER_TOPIC=5
HOT_ISSUE_COUNT=10
CARD_NEWS_COUNT=3
ARTICLE_COUNT=3
CATEGORY_FILTER=finance
```

즉, 최대 30개 키워드를 수집하고 그중 경제·금융 관련 후보를 조회수 순으로 정리한 뒤, 텔레그램에 오늘의 운영 후보만 보냅니다.

## 텔레그램 표시 예시

```text
🔥 오늘의 핫이슈 · 카드뉴스 · 작성글 후보
분야 필터: 경제·금융 우선
정렬 기준: 조회수 많은 순 → 근거 기사 수 → 내부 점수

🔥 오늘의 핫이슈 TOP 10

1. [경제·금융] 기준금리 전망
조회수: 10.0만+ / 근거강도: 강함
수집경로: google_trends_rss
작성각도: 금리 변화 → 가계부담/저축전략 → 확인할 금융상품 포인트
근거자료:
  1) 기사 제목 (매체 · 날짜) / 링크1
  2) 기사 제목 (매체 · 날짜) / 링크2
  3) 기사 제목 (매체 · 날짜) / 링크3
  4) 기사 제목 (매체 · 날짜) / 링크4
  5) 기사 제목 (매체 · 날짜) / 링크5

🃏 오늘의 카드뉴스 추천
1. #1 기준금리 전망
선정이유: 조회수 10.0만+, 기사근거 5개
구성방향: 원인 → 가계 영향 → 오늘 확인할 숫자 → 대응법 카드 구성

✍️ 오늘의 작성글 추천
1. #1 기준금리 전망
선정이유: 검색 유입 가능성 + 조회수 10.0만+ + 근거 기사 5개
글방향: 기준금리 전망 배경과 가계/금융상품 영향, 확인해야 할 지표를 정리하는 해설형 글
```

## GitHub Actions 수동 실행 옵션

`Actions → daily-adsense-seo → Run workflow`에서 아래 값을 조정할 수 있습니다.

| 옵션 | 기본값 | 설명 |
|---|---:|---|
| `topics` | 비움 | 특정 주제만 보고 싶을 때 쉼표/줄바꿈으로 입력 |
| `category_filter` | `finance` | 경제·금융 우선. `all`이면 전체 카테고리 |
| `item_list_only` | `true` | 글 초안 생성 없이 후보 리포트만 전송 |
| `news_links_per_topic` | `5` | 주제별 근거 기사 링크 수 |
| `hot_issue_count` | `10` | 오늘의 핫이슈 표시 개수 |
| `card_news_count` | `3` | 오늘의 카드뉴스 추천 개수 |
| `article_count` | `3` | 오늘의 작성글 추천 개수 |
| `telegram_only` | `false` | 글 초안 생성 모드에서 WordPress 업로드 생략 |
| `send_articles_to_telegram` | `false` | 글 초안 생성 모드에서 본문을 텔레그램으로 전송 |

## 카테고리 필터

기본값 `finance`에는 아래 4개 그룹이 포함됩니다.

- `💰 경제·금융`: 금리, 환율, 물가, 대출, 예금, 카드, 보험, 세금
- `📈 증권·투자`: 코스피, 코스닥, 주식, ETF, 공모주, 실적, 반도체
- `🏠 부동산·주거금융`: 청약, 전세, 월세, 주택담보대출, DSR
- `🏛️ 정책·지원금`: 소상공인 지원금, 근로장려금, 국민연금, 최저임금

전체 카테고리를 보고 싶으면 수동 실행에서 `category_filter=all`로 바꾸면 됩니다.

## WordPress 글 초안 생성이 필요할 때

평소에는 `ITEM_LIST_ONLY=true`를 권장합니다. 특정 주제를 보고 글 작성까지 하고 싶을 때만 아래처럼 실행하세요.

```text
item_list_only = false
telegram_only = true
send_articles_to_telegram = true
topics = 기준금리 전망, 원달러 환율 전망
```

이 경우 WordPress 업로드 없이 텔레그램으로 글 초안을 받을 수 있습니다.

## 보고서 파일

실행이 끝나면 GitHub Actions artifact로 아래 파일이 저장됩니다.

- `trend_keywords_raw_YYYYMMDD.csv`: 원본 수집 키워드
- `trend_keywords_YYYYMMDD.csv`: 카테고리 필터 후 조회수 정렬 키워드
- `idea_items_YYYYMMDD.json`: 후보 아이템과 근거 기사 전체 데이터
- `idea_items_YYYYMMDD.csv`: 순위, 조회수, 추천 용도, 근거 기사 링크 요약
