# AdSense SEO Dashboard Service Blueprint

이 패키지는 현재 HTML 목업을 실제 서비스로 연결하기 위한 1차 설계 파일입니다.

## 포함 파일

- `supabase_schema.sql`  
  사용자별 최적화, 키워드, SNS 트렌드, 경제지표, 콘텐츠 후보, 발행 로그 저장용 DB 스키마

- `api_spec.json`  
  대시보드에서 필요한 API 엔드포인트 명세

- `implementation_plan.md`  
  Supabase, Python 자동화, Next.js/FastAPI 연결 순서

- `nextjs_build_prompt.md`  
  현재 HTML을 Next.js 프로젝트로 전환하기 위한 개발 프롬프트

- `fastapi_build_prompt.md`  
  기존 Python 자동화 코드를 FastAPI 백엔드로 전환하기 위한 개발 프롬프트

## 추천 다음 작업

1. Supabase 프로젝트 생성
2. `supabase_schema.sql` 실행
3. 기존 Python 자동화 코드에서 결과를 DB에 저장하도록 리팩토링
4. Next.js UI 프로젝트 생성
5. 로그인/내 최적화부터 Supabase Auth와 연결
6. 키워드/SNS 트렌드/경제지표 순서로 실제 API 연결

## 추천 배포 구조

- Frontend: Vercel
- Backend: Railway 또는 Render
- DB/Auth: Supabase
- Cron: GitHub Actions 또는 Vercel Cron
