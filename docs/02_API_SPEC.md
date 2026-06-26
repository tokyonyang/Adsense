# 02. API 명세

## Health

### GET /health

서버 상태 확인.

응답:

```json
{
  "ok": true,
  "service": "adsense-dashboard-api"
}
```

## Dashboard

### GET /api/dashboard/summary

대시보드 KPI와 오늘의 추천 액션 반환.

Query:

```text
user_id optional
```

## Profile

### GET /api/profile

사용자 프로필 조회.

### PATCH /api/profile

관심 카테고리, 콘텐츠 목적, 작성 톤, 발행 채널 저장.

## Keywords

### GET /api/keywords

키워드 목록 조회.

Query:

```text
category
status
limit
```

### POST /api/keywords/collect

키워드 수집 실행.

## Issues

### GET /api/issues/top

오늘의 핫이슈 TOP 목록 조회.

### POST /api/issues/{keyword_id}/convert

키워드를 글감/카드뉴스/상품소싱 후보로 전환.

## Evidence

### GET /api/evidence

근거자료 목록 조회.

### POST /api/evidence/refresh

선택 키워드의 근거자료 재수집.

## SNS Trends

### GET /api/sns/trends

SNS 트렌드 목록 조회.

Query:

```text
platform
category
content_usage
limit
```

### POST /api/sns/collect

SNS 트렌드 수집 실행.

### POST /api/sns/trends/{trend_id}/convert

SNS 트렌드를 글감/카드뉴스/상품소싱 후보로 전환.

## Economic Events

### GET /api/economic-events

경제지표 캘린더 조회.

Query:

```text
start_date
end_date
country
importance
```

### POST /api/economic-events

경제지표 일정 추가.

### PATCH /api/economic-events/{event_id}

실제치, 상태, 콘텐츠 활용 방식 수정.

## Content

### GET /api/ideas

콘텐츠 후보 목록 조회.

### POST /api/articles/generate

SEO 글 초안 생성.

### POST /api/cardnews/generate

카드뉴스 구성안 생성.

### POST /api/seo/check

SEO/애드센스 안전도 검수.

### POST /api/ab/generate

제목/썸네일 A/B 후보 생성.

## Publish

### GET /api/calendar

콘텐츠 캘린더 조회.

### POST /api/calendar

캘린더 일정 추가.

### POST /api/publish/wordpress

워드프레스 발행.

### POST /api/send/telegram

텔레그램 전송.

## Logs

### GET /api/logs

실행 로그 조회.

## Support

### POST /api/support

문의 접수.
