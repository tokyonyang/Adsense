@echo off
chcp 65001 > nul
echo ========================================
echo AdSense Dashboard 파일 복사 안내
echo ========================================
echo.
echo 이 폴더의 파일들을 기존 GitHub 레포 루트에 복사하세요.
echo.
echo 권장 순서:
echo 1. 기존 레포에서 새 브랜치 생성
echo    git checkout -b dashboard-supabase-v1
echo.
echo 2. 이 패키지의 폴더/파일 복사
echo    docs
echo    supabase
echo    app
echo    dashboard
echo    .github
echo    .env.example.dashboard
echo    requirements.dashboard.txt
echo.
echo 3. 커밋
echo    git add .
echo    git commit -m "Add dashboard Supabase API blueprint"
echo.
echo 4. 푸시
echo    git push origin dashboard-supabase-v1
echo.
pause
