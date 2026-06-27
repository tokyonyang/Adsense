# v1.30.1 업로드 체크리스트

## 1. 업로드 전 확인

ZIP 압축을 풀었을 때 아래 파일이 실제로 보여야 합니다.

```text
.github/workflows/daily-adsense-seo.yml
.github/workflows/morning-headline-news.yml
.github/workflows/adsense-dashboard-cron.yml
.github/workflows/telegram-send-test.yml
```

## 2. GitHub 업로드

GitHub 저장소 루트에서 파일을 업로드합니다.

주의:
- `.github` 폴더는 저장소 루트에 있어야 합니다.
- `.github/workflows`가 아니라 `github/workflows`로 올라가면 안 됩니다.
- workflow 파일명 확장자는 `.yml`이어야 합니다.

## 3. Actions 확인

업로드 후 Actions 탭에서 아래 workflow가 보이는지 확인합니다.

```text
Daily AdSense SEO Hot Issue Report
Morning Headline News Report
AdSense Dashboard Pipeline Report
Telegram Send Test
```

## 4. 수동 실행 순서

먼저 Daily:

```text
Actions → Daily AdSense SEO Hot Issue Report → Run workflow
```

그다음 Morning:

```text
Actions → Morning Headline News Report → Run workflow
```

## 5. 정상 로그

Daily:

```text
[Daily AdSense SEO Hot Issue Report · Editorial Engine v1.28]
[selected slot mix]
[reports] saved
[telegram] sent
```

Morning:

```text
[daily-hotissue-cardnews result]
issues_preview
chart
insight
```
