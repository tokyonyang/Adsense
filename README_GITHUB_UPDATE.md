# AdSense SEO 자동화 대시보드 GitHub 업데이트 파일

이 패키지는 기존 GitHub 레포에 추가해서 사용할 수 있는 **서비스화 준비 파일 모음**입니다.

## 목적

현재 Python 기반 AdSense SEO 자동화 코드를 다음 구조로 확장합니다.

```text
기존 자동화 코드
→ Supabase DB 저장
→ 대시보드 API
→ 회원별 최적화
→ SNS 트렌드
→ 경제지표 캘린더
→ SEO 검수
→ 워드프레스/텔레그램 발행관리
```

## 포함 폴더

```text
docs/
  00_SETUP_GUIDE.md
  01_SERVICE_ARCHITECTURE.md
  02_API_SPEC.md
  03_DEPLOYMENT_GUIDE.md

supabase/
  schema.sql
  rls_policies.sql
  seed_sample_data.sql

app/
  core/
  db/
  repositories/
  services/
  routers/
  jobs/
  schemas/
  main.py

dashboard/
  static_dashboard.html
  README.md

.github/
  workflows/
    adsense-dashboard-cron.yml

.env.example.dashboard
requirements.dashboard.txt
copy_files_to_repo.bat
```

## 사용 순서

1. 이 ZIP 파일을 압축 해제합니다.
2. 기존 GitHub 레포 루트에 폴더와 파일을 복사합니다.
3. Supabase 프로젝트를 생성합니다.
4. Supabase SQL Editor에서 아래 순서로 실행합니다.
   - `supabase/schema.sql`
   - `supabase/rls_policies.sql`
   - `supabase/seed_sample_data.sql`
5. `.env.example.dashboard`를 참고해 GitHub Secrets 또는 서버 환경변수를 설정합니다.
6. `requirements.dashboard.txt` 기준으로 의존성을 설치합니다.
7. `app/main.py` FastAPI 서버를 실행해 API 연결을 테스트합니다.

## 주의

- 이 패키지는 기존 자동화 파일을 직접 삭제하거나 변경하지 않는 **추가형 구조**입니다.
- 기존 `main.py`와 충돌하지 않도록 FastAPI 진입점은 `app/main.py`로 분리했습니다.
- 실제 외부 API 키는 절대 GitHub에 직접 올리지 말고 GitHub Secrets 또는 서버 환경변수에 저장하세요.
