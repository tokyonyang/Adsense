# AdSense SEO 운영 대시보드 v1.2 패치

## 수정 목표

Vercel 화면에서 사용자가 혼동할 수 있는 `API 연결 예정입니다` 알림을 전부 제거했습니다.

## 주요 변경

- 브라우저 alert 팝업 제거
- 안내는 화면 하단 토스트 메시지로 표시
- 수동 실행이 아직 안 되는 버튼은 실행 로그 또는 관련 화면으로 이동
- 회원 기능은 계속 비활성화
- 대시보드 상단에 자동 수집/전송 상태 안내 추가
- 프롬프트 복사 버튼은 실제 textarea 내용을 복사하도록 일부 개선
- Vercel 배포용 `index.html`, `dashboard/index.html`, `vercel.json` 포함

## GitHub에 업로드할 파일

```text
index.html
dashboard/index.html
vercel.json
```

## 적용 방법

1. ZIP 압축 해제
2. GitHub 레포 루트에 위 3개 파일 업로드/교체
3. Commit changes
4. Vercel 자동 재배포 확인

## 접속 주소

```text
https://gooddaynews.vercel.app
```

또는 현재 Vercel 프로젝트 주소

## 다음 개선 순서

1. 버튼 정리 완료 여부 확인
2. Supabase 데이터를 화면에 읽어오는 기능 연결
3. 실행 로그 실제 데이터 연결
4. 키워드/SNS 트렌드 실제 테이블 연결
5. 수동 재수집 API 연결
