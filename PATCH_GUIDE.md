# AdSense SEO 운영 대시보드 v1.5.1 패치

## 수정한 문제

v1.5에서 Supabase 연결 코드와 anon key는 정상이어도 화면이 계속 `Supabase 연결 대기`로 남는 문제가 있었습니다.

원인:
페이지 로딩 후 `loadSupabaseDashboardData()`를 자동 실행하는 호출 코드가 빠져 있었습니다.

## 이번 수정

- 페이지 로딩 후 Supabase 데이터 자동 동기화 실행
- `데이터 새로고침` 버튼 추가
- `window.forceSupabaseRefresh()` 전역 함수 추가
- 기존 `dashboard_config.js`는 건드리지 않음

## GitHub에 업로드할 파일

아래 3개만 교체하세요.

```text
index.html
dashboard/index.html
vercel.json
```

`dashboard_config.js`는 이미 anon key를 넣어두었으므로 그대로 두는 것을 추천합니다.

## 적용 후 확인

Vercel 재배포 후 아래 주소로 접속하세요.

```text
https://gooddaynews.vercel.app/?v=151
```

정상이라면 상단 상태가 아래처럼 바뀝니다.

```text
Supabase 실제 데이터 연결됨
```

그리고 콘텐츠 캘린더의 주요 경제지표 일정도 실제 데이터 또는 데이터 없음 상태로 갱신됩니다.

## 수동 확인

Console에서 아래를 입력해도 됩니다.

```javascript
window.forceSupabaseRefresh()
```
