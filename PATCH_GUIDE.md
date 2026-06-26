# AdSense SEO 운영 대시보드 v1.3 패치

## 수정 내용

1. 키워드 수집 페이지 검색창 동작 추가
   - 키워드, 출처, 카테고리, 상태 텍스트 기준으로 테이블 필터링
   - 검색 결과 개수 표시
   - 카테고리 필터와 검색어를 함께 적용

2. 대시보드 핫이슈 검색창 동작 추가
   - 오늘의 핫이슈 테이블 검색 가능

3. 실행 로그 상세 보기 개선
   - 기존 알림 문구 제거
   - `상세` 버튼 클릭 시 화면 안에서 상세 패널 표시
   - 현재는 예시 로그이며, 실제 로그는 Supabase `dashboard_runs` 연결 후 표시 가능

4. 실시간 연동 상태 안내 추가
   - 현재 Vercel 페이지는 정적 HTML
   - GitHub Actions는 자동 수집/텔레그램 전송
   - 대시보드 실시간 데이터 조회는 다음 단계에서 Supabase 연결 필요

## GitHub에 업로드할 파일

```text
index.html
dashboard/index.html
vercel.json
```

## 적용 방법

1. ZIP 압축 해제
2. GitHub 레포 루트에 3개 파일 업로드/교체
3. Commit changes
4. Vercel 자동 재배포 확인

## 다음 단계

v1.4에서 추천하는 작업:

- Supabase anon key 기반 읽기 전용 연결
- `trend_keywords` 실제 데이터 표시
- `sns_trends` 실제 데이터 표시
- `dashboard_runs` 실제 로그 표시
