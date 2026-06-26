# AdSense SEO 자동화 스타터

트렌드 키워드를 수집하고, 텔레그램으로 **작성 후보 아이템과 관련 신문 기사 링크**를 보내는 자동화 패키지입니다. 필요할 때만 Gemini 글 초안 생성과 WordPress draft 업로드를 사용할 수 있습니다.

## 이번 수정 사항 v5
- 기본 동작을 `글 초안 생성`이 아니라 **작성 후보 리스트 전송**으로 변경했습니다.
- 텔레그램에는 주제별로 `작성각도`와 `관련 기사 링크 5개`만 전송합니다.
- Gemini로 긴 본문을 미리 생성하지 않기 때문에 텔레그램 메시지가 과도하게 쌓이지 않습니다.
- Google News RSS 기반으로 최근 관련 뉴스 링크를 수집합니다.
- GitHub Actions 수동 실행 옵션에 `item_list_only`, `news_links_per_topic`을 추가했습니다.

## 기본 실행
```bash
pip install -r requirements.txt
cp .env.example .env
python main.py --max-keywords 30 --max-posts 10
```

기본값은 아래와 같습니다.

```text
MAX_KEYWORDS=30
MAX_POSTS_PER_RUN=10
ITEM_LIST_ONLY=true
NEWS_LINKS_PER_TOPIC=5
```

즉, 최대 30개 키워드를 수집하고 그중 10개 작성 후보를 골라, 각 주제별 관련 기사 링크 5개를 텔레그램으로 보냅니다.

## GitHub Actions 사용
`Actions → daily-adsense-seo → Run workflow`에서 다음 옵션을 볼 수 있어야 합니다.

```text
topics
item_list_only
news_links_per_topic
telegram_only
send_articles_to_telegram
```

### 추천 운영값
```text
item_list_only = true
news_links_per_topic = 5
```

이렇게 실행하면 WordPress 업로드와 글 초안 생성 없이 선별용 리포트만 옵니다.

### 선택 주제만 받고 싶을 때
`topics`에 쉼표나 줄바꿈으로 입력하세요.

```text
전기요금 절약 방법, 소상공인 지원금 정리, 전시 작전통제권
```

## 글 초안 생성 모드로 전환
선택한 주제를 실제 글 초안으로 만들고 싶을 때만 아래처럼 실행하세요.

```text
item_list_only = false
telegram_only = true
send_articles_to_telegram = true
```

WordPress draft 업로드까지 하려면 `telegram_only=false`로 두고, 워드프레스 권한을 먼저 정상화해야 합니다.

## WordPress 401 오류
아래 오류는 텔레그램 문제가 아니라 WordPress 권한 문제입니다.

```text
HTTP 401 rest_cannot_create
```

확인할 것:
- `WP_USERNAME` 사용자가 관리자/편집자/글쓴이 권한인지 확인
- 해당 사용자 프로필에서 Application Password를 새로 발급
- 보안 플러그인이 REST API 또는 Application Password를 막는지 확인

## GitHub Secrets
```text
GEMINI_API_KEY
WP_SITE_URL
WP_API_URL  # 선택 사항
WP_USERNAME
WP_APP_PASSWORD
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

`ITEM_LIST_ONLY=true`만 쓸 경우 WordPress 관련 Secrets가 없어도 후보 리포트 전송은 가능합니다.
