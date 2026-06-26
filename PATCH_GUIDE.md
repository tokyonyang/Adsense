# AdSense SEO 운영 대시보드 v1.4.1 패치

## 수정한 문제

v1.4에서 콘솔에 아래 오류가 뜨던 문제를 수정했습니다.

```text
Uncaught ReferenceError: loadSupabaseDashboardData is not defined
```

원인:
Supabase 연결 함수가 잘못된 스코프에 들어가서 전역에서 실행되지 않았습니다.

수정:
`window.loadSupabaseDashboardData`와 `window.setupSupabaseAutoRefresh`로 전역 고정했습니다.

## GitHub에 업로드할 파일

```text
index.html
dashboard/index.html
dashboard_config.js
dashboard/dashboard_config.js
vercel.json
```

## 중요

`dashboard_config.js`와 `dashboard/dashboard_config.js`에는 반드시 anon public key를 다시 넣어야 합니다.

```javascript
SUPABASE_ANON_KEY: "eyJ..."
```

service_role key는 절대 넣지 마세요.

## Supabase SQL

이미 v1.4 SQL을 실행했다면 다시 실행하지 않아도 됩니다.
그래도 오류가 있으면 아래 파일을 다시 실행하세요.

```text
supabase/public_read_policy_v1_4_1.sql
```

## 적용 후 확인

1. Vercel 배포 완료 확인
2. 강제 새로고침 또는 아래 주소로 접속

```text
https://gooddaynews.vercel.app/?v=141
```

3. Console에서 확인

```javascript
typeof loadSupabaseDashboardData
```

정상 결과:

```text
"function"
```

4. 직접 실행

```javascript
loadSupabaseDashboardData()
```

정상이라면 상단 상태가 `Supabase 실제 데이터 연결됨`으로 바뀝니다.
