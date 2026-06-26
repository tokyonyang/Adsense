# 00. 설치 및 적용 가이드

## 1. 기존 GitHub 레포에 파일 추가

압축을 해제한 뒤 기존 레포 루트에 아래 구조로 복사합니다.

```text
docs/
supabase/
app/
dashboard/
.github/workflows/
.env.example.dashboard
requirements.dashboard.txt
```

기존 파일을 바로 덮어쓰기보다는 새 브랜치를 만드는 것을 권장합니다.

```bash
git checkout -b dashboard-supabase-v1
```

## 2. Supabase 프로젝트 생성

1. Supabase에서 새 프로젝트 생성
2. SQL Editor 열기
3. `supabase/schema.sql` 실행
4. `supabase/rls_policies.sql` 실행
5. 테스트용 데이터가 필요하면 `supabase/seed_sample_data.sql` 실행

## 3. 환경변수 설정

`.env.example.dashboard`를 `.env`로 복사합니다.

```bash
copy .env.example.dashboard .env
```

필수 값:

```text
SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY
NAVER_CLIENT_ID
NAVER_CLIENT_SECRET
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
GEMINI_API_KEY
WP_BASE_URL
WP_USERNAME
WP_APP_PASSWORD
```

## 4. 의존성 설치

```bash
pip install -r requirements.dashboard.txt
```

## 5. FastAPI 서버 실행

```bash
uvicorn app.main:app --reload --port 8000
```

확인:

```text
http://localhost:8000/health
http://localhost:8000/docs
```

## 6. 정적 대시보드 확인

`dashboard/static_dashboard.html` 파일을 브라우저에서 열어 화면을 확인합니다.

## 7. GitHub Actions 스케줄

`.github/workflows/adsense-dashboard-cron.yml`은 하루 4회 실행 기준입니다.

KST 기준:

- 06:00
- 11:00
- 15:00
- 19:00

UTC cron:

```text
0 21,2,6,10 * * *
```

## 8. 다음 단계

1. 기존 Python 자동화 함수와 `app/services` 연결
2. 대시보드 API에서 Supabase 데이터 조회
3. Next.js 프론트로 전환
4. 실제 워드프레스/텔레그램 발행 연결
