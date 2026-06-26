너는 Next.js + Supabase 기반 SaaS 관리자 대시보드를 만드는 시니어 풀스택 개발자다.

목표:
현재 정적 HTML로 만들어진 AdSense SEO 자동화 대시보드를 실제 데이터와 연결 가능한 Next.js 프로젝트로 전환한다.

기술 스택:
- Next.js App Router
- TypeScript
- Tailwind CSS
- shadcn/ui
- Supabase Auth
- Supabase PostgreSQL
- API Routes
- 기존 Python 자동화 서버와 연동 가능하게 설계

주요 페이지:
- /dashboard
- /calendar
- /keywords
- /issues
- /evidence
- /sns-trends
- /card-news
- /articles
- /drafts
- /seo-check
- /ab-test
- /publish
- /telegram
- /profile
- /members
- /about
- /privacy
- /terms
- /support
- /settings
- /logs

핵심 요구:
1. 좌측 사이드바 메뉴 그룹화
2. 로그인 상태에 따라 사용자 정보 표시
3. user_profiles 기반 사용자별 관심 카테고리/콘텐츠 목적 저장
4. 모든 테이블은 Supabase 데이터 기반으로 전환 가능하게 설계
5. 초기에는 mock data를 사용하되, lib/api.ts에 API 함수로 분리
6. API 응답 타입을 types/*.ts로 정의
7. SNS 트렌드, 경제지표, 키워드, 콘텐츠 아이디어, 발행 로그를 각각 컴포넌트 분리
8. SEO 검수/애드센스 안전도 화면은 점수 카드와 체크리스트 구조로 구성
9. 개인정보방침/이용약관/문의하기 페이지 포함
10. 모바일 반응형 대응

디자인:
- 현재 HTML의 밝은 SaaS 스타일 유지
- blue/green/amber/red 상태 배지
- 카드 기반 레이아웃
- 운영자가 하루에 여러 번 확인하는 실무형 UI
