# AdSense SEO 운영 대시보드 v1.4 Supabase 연결 패치

## 이번 버전의 목표

Vercel 정적 대시보드에서 Supabase의 실제 데이터를 읽어옵니다.

연결 대상:

```text
trend_keywords
sns_trends
dashboard_runs
```

## GitHub에 업로드할 파일

```text
index.html
dashboard/index.html
dashboard_config.js
dashboard/dashboard_config.js
vercel.json
```

## Supabase에 실행할 SQL

```text
supabase/public_read_policy_v1_4.sql
```

Supabase SQL Editor에서 실행하세요.

## anon public key 입력 방법

Supabase에서:

```text
Project Settings
→ API
→ Project API keys
→ anon public
```

값을 복사해서 아래 파일 두 곳에 넣으세요.

```text
dashboard_config.js
dashboard/dashboard_config.js
```

수정 전:

```javascript
SUPABASE_ANON_KEY: "PASTE_SUPABASE_ANON_PUBLIC_KEY_HERE"
```

수정 후:

```javascript
SUPABASE_ANON_KEY: "eyJ..."
```

## 절대 하면 안 되는 것

브라우저용 파일에 아래 값을 넣으면 안 됩니다.

```text
SUPABASE_SERVICE_ROLE_KEY
service_role key
```

service role key는 GitHub Actions나 서버에서만 사용해야 합니다.

## 적용 순서

1. ZIP 압축 해제
2. `supabase/public_read_policy_v1_4.sql`을 Supabase SQL Editor에서 실행
3. `dashboard_config.js`, `dashboard/dashboard_config.js`에 anon public key 입력
4. GitHub에 파일 업로드/교체
5. Commit changes
6. Vercel 자동 재배포 확인
7. Vercel 사이트 접속
8. 대시보드 상단 상태가 `Supabase 실제 데이터 연결됨`으로 바뀌는지 확인

## 현재 한계

- 읽기 전용 연결입니다.
- 수동 재수집 버튼은 아직 실제 API를 호출하지 않습니다.
- 회원별 private 데이터는 아직 비활성화 상태입니다.
- user_id가 null인 공용 운영 데이터만 읽습니다.

## 다음 단계 v1.5 추천

- 실제 `economic_events` 캘린더 표시
- 실제 `content_ideas` 작성글 후보 표시
- 수동 재수집 버튼을 GitHub Actions dispatch 또는 FastAPI API와 연결
