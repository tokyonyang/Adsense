# 01. 서비스 아키텍처

## 전체 구조

```text
[GitHub Actions / Cron]
        ↓
[Python/FastAPI Backend]
        ↓
[Supabase PostgreSQL]
        ↓
[Dashboard Frontend]
        ↓
[WordPress / Telegram]
```

## 핵심 데이터 흐름

```text
1. 키워드 수집
   Google Trends / Naver News / DataLab

2. SNS 트렌드 수집
   Google / YouTube / Naver 우선
   X / TikTok / Instagram은 단계적 연결

3. 경제지표 캘린더
   초기에는 수동/반자동 입력
   추후 Investing.com 위젯/외부 데이터 참고

4. 콘텐츠 후보 생성
   trend_keywords
   sns_trends
   economic_events
   → content_ideas

5. 글/카드뉴스 초안 생성
   content_ideas
   → generated_articles
   → cardnews_drafts

6. 검수
   SEO 점수
   애드센스 안전도
   근거자료 신뢰도

7. 발행
   WordPress
   Telegram
   Manual Copy

8. 로그 저장
   dashboard_runs
   publish_logs
```

## 권장 배포 구조

### 안정형

```text
Frontend: Vercel / Netlify
Backend: Railway / Render
DB/Auth: Supabase
Scheduler: GitHub Actions
```

### 단순형

```text
Python 자동화: GitHub Actions
DB: Supabase
Dashboard: 정적 HTML 또는 Vercel
```

## 사용자별 최적화

`user_profiles` 테이블 기준으로 다음 설정을 저장합니다.

- 관심 카테고리
- 콘텐츠 목적
- 작성 톤
- 발행 채널
- 일일 추천 개수
- 사이트/블로그 설명

이를 바탕으로 대시보드 추천 순서를 조정합니다.

## SNS 트렌드 우선 연결 순서

1. Google Trends
2. YouTube Data API
3. Naver Search API
4. X Trends API
5. TikTok Creative Center 참고형
6. Instagram/Threads 수동형

## 경제지표 캘린더 운영 방식

초기:

- 수동 입력
- 주요 지표만 관리
- 주간/월간 화면 제공

추후:

- 외부 캘린더 위젯
- 발표 후 실제치 수동 입력
- 지표 기반 후속 콘텐츠 자동 추천
