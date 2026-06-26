# 03. 배포 가이드

## 1. GitHub Actions만 사용하는 단순 운영

기존 자동화처럼 GitHub Actions에서 Python 스크립트를 실행합니다.

장점:

- 별도 서버 비용 적음
- 기존 구조와 유사
- 하루 4회 자동 실행에 적합

단점:

- 실시간 대시보드 API는 제한적
- 긴 작업/수동 버튼 실행에는 불리

## 2. Railway/Render에 FastAPI 배포

추천 구조:

```text
FastAPI Backend → Railway
Supabase DB/Auth
Dashboard Frontend → Vercel
```

장점:

- 수동 실행 버튼 가능
- API 서버 운영 가능
- 대시보드와 실시간 연결 가능

단점:

- 서버 비용 가능성
- 환경변수 관리 필요

## 3. Vercel + Supabase 중심 운영

정적/Next.js 대시보드를 Vercel에 배포하고,
긴 작업은 GitHub Actions 또는 Railway로 분리합니다.

## 4. 환경변수 관리

GitHub Secrets:

```text
SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY
NAVER_CLIENT_ID
NAVER_CLIENT_SECRET
GEMINI_API_KEY
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
WP_BASE_URL
WP_USERNAME
WP_APP_PASSWORD
```

절대 GitHub에 직접 커밋하면 안 되는 값:

- API Key
- Bot Token
- WordPress App Password
- Supabase Service Role Key

## 5. 운영 순서

1. Supabase DB 생성
2. GitHub Actions로 수집 자동화
3. FastAPI로 수동 실행 API 연결
4. 대시보드 프론트 연결
5. WordPress/Telegram 발행 자동화
