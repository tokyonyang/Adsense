# 다음 스텝 구현 계획

## 현재 상태
현재 HTML 목업은 다음 기능 화면을 포함합니다.

- 회원제/로그인 목업
- 사용자별 최적화
- 카테고리형 키워드/뉴스 분류
- SNS 트렌드
- 콘텐츠 캘린더
- 근거자료 관리
- SEO 검수/애드센스 안전도
- 제목·썸네일 A/B
- 발행관리
- 텔레그램
- 개인정보방침/이용약관/문의하기

## 다음 단계 목표
정적 HTML을 실제 서비스로 연결하기 위한 DB/API 구조를 먼저 구축합니다.

## 1단계: Supabase 프로젝트 생성
1. Supabase 프로젝트 생성
2. SQL Editor에서 `supabase_schema.sql` 실행
3. Auth 이메일 로그인 활성화
4. user_profiles RLS 정책 추가
5. service role key는 서버 환경변수에만 저장

## 2단계: 기존 Python 자동화 코드 서비스화
기존 파일 구조를 아래처럼 분리합니다.

app/
  services/
    keyword_service.py
    sns_trend_service.py
    economic_calendar_service.py
    evidence_service.py
    article_service.py
    cardnews_service.py
    seo_check_service.py
    publish_service.py
  repositories/
    supabase_client.py
    keyword_repository.py
    content_repository.py
    run_repository.py
  jobs/
    collect_keywords_job.py
    collect_sns_trends_job.py
    full_pipeline_job.py

## 3단계: 안전한 데이터 소스부터 연결
우선순위는 다음과 같습니다.

1. Google Trends RSS / Trends API
2. YouTube Data API
3. Naver Search API
4. 경제지표 캘린더: 초기에는 수동/반자동 입력
5. X Trends API: 요금제 확인 후
6. TikTok/Instagram: 참고형/수동형부터

## 4단계: API 서버 만들기
추천 방식은 둘 중 하나입니다.

### 선택 A: Next.js API Routes
- 프론트와 백엔드를 한 프로젝트로 관리
- Vercel 배포가 쉬움
- 단, 긴 Python 작업은 별도 서버/Railway가 유리

### 선택 B: FastAPI + Next.js
- 기존 Python 코드 재사용이 쉬움
- 장기 작업/스케줄러/외부 API 수집에 유리
- 프론트는 Vercel, 백엔드는 Railway/Render 추천

## 5단계: 실제 화면 연결 순서
1. 로그인/내 최적화 → user_profiles
2. 대시보드 KPI → dashboard summary API
3. 키워드 수집 → trend_keywords
4. SNS 트렌드 → sns_trends
5. 경제지표 → economic_events
6. 콘텐츠 후보 → content_ideas
7. 글 초안 → generated_articles
8. 발행관리 → publish_logs/content_calendar

## 6단계: 스케줄 운영
하루 4회 운영 기준:

- 06:00 키워드/SNS/경제지표 수집
- 11:00 오전 핫이슈/글감 추천
- 15:00 카드뉴스/글 초안 생성
- 19:00 발행/텔레그램 리포트

GitHub Actions 또는 Vercel Cron으로 API를 호출합니다.
