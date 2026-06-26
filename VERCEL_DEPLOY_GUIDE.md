# Vercel 정적 대시보드 배포 가이드

## 목적

현재 GitHub 레포의 HTML 대시보드를 Vercel에서 실제 URL로 열어보면서 수정하기 위한 최소 설정입니다.

## GitHub에 추가/교체할 파일

```text
index.html
dashboard/index.html
vercel.json
```

## Vercel 등록 순서

1. https://vercel.com 접속
2. Add New → Project
3. GitHub 계정 연결
4. `Adsense` 레포 선택
5. Import 클릭
6. 설정값을 아래처럼 지정

```text
Framework Preset: Other
Root Directory: ./
Build Command: 비워두기
Output Directory: ./
Install Command: 비워두기
```

7. Deploy 클릭

## 접속 주소

배포 완료 후 Vercel이 아래와 비슷한 주소를 제공합니다.

```text
https://adsense-xxxx.vercel.app
```

또는 Vercel 프로젝트명에 따라:

```text
https://adsense.vercel.app
```

## 수정 방식

GitHub에서 `index.html` 또는 `dashboard/index.html`을 수정하고 커밋하면 Vercel이 자동으로 다시 배포합니다.

## 현재 구조

```text
/
  index.html              # Vercel 메인 접속용
  vercel.json             # Vercel 라우팅 설정
  dashboard/
    index.html            # dashboard 경로 유지용
```

## 주의

현재는 정적 HTML 배포입니다.
Supabase 데이터를 실제로 불러오는 기능은 아직 연결되지 않았습니다.

다음 단계에서 아래 기능을 순차적으로 연결합니다.

1. Supabase 읽기 API
2. 키워드 테이블 실제 데이터
3. SNS 트렌드 실제 데이터
4. 실행 로그 실제 데이터
5. 버튼별 API 실행
