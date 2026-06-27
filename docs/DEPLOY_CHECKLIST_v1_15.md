# 배포 체크리스트 v1.15

## 1. 파일 업로드
통합본 ZIP 안의 파일을 GitHub main 브랜치에 업로드/교체합니다.

## 2. Secrets 확인
Settings → Secrets and variables → Actions

아래 키가 비어 있지 않은지 확인:
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID
- NAVER_CLIENT_ID
- NAVER_CLIENT_SECRET
- GEMINI_API_KEY
- SUPABASE_URL
- SUPABASE_SERVICE_ROLE_KEY

## 3. Actions 목록 확인
Actions 화면에 아래 4개가 보여야 합니다.
- Morning Headline News Report
- Daily AdSense SEO Hot Issue Report
- AdSense Dashboard Pipeline Report
- Telegram Send Test

## 4. 수동 테스트 권장 순서
1) Telegram Send Test
2) Morning Headline News Report
3) Daily AdSense SEO Hot Issue Report
4) AdSense Dashboard Pipeline Report

## 5. 자동 발송 시간
- 06:07 → 핫이슈
- 06:10 → 아침 헤드라인 이미지 + 텍스트
- 09:17 → 대시보드 리포트
- 11:07 → 핫이슈
- 15:07 → 핫이슈
- 17:17 → 대시보드 리포트
- 19:07 → 핫이슈
