# v1.10.1 GitHub Actions workflow 수정 안내

## 왜 필요한가?

GitHub Actions 화면에 아래 단계가 보이지 않는다면 workflow yml 파일이 아직 구버전입니다.

```text
Preview event boost config
Run daily dashboard pipeline and Telegram report
```

## 교체해야 할 파일

아래 경로의 파일을 이 패치의 파일로 교체하세요.

```text
.github/workflows/adsense-dashboard-cron.yml
```

## GitHub 웹에서 교체하는 방법

1. GitHub 레포 접속
2. `.github` 폴더 클릭
3. `workflows` 폴더 클릭
4. `adsense-dashboard-cron.yml` 클릭
5. 연필 아이콘 클릭
6. 전체 내용을 이 패치의 파일 내용으로 교체
7. Commit changes

## 만약 다른 workflow 파일이 실제로 실행 중이라면?

기존 레포에 아래 파일도 있을 수 있습니다.

```text
.github/workflows/daily-adsense-seo.yml
```

Actions에서 실제 실행되는 workflow가 이 파일이라면, 같은 내용으로 이 파일도 교체하거나, 중복 실행 방지를 위해 하나만 남기는 것이 좋습니다.

추천:

```text
사용할 파일: .github/workflows/adsense-dashboard-cron.yml
구버전 파일: .github/workflows/daily-adsense-seo.yml 은 비활성화 또는 삭제
```

## 적용 후 확인

GitHub Actions에서 수동 실행:

```text
Actions
→ AdSense Dashboard Cron
→ Run workflow
```

정상이라면 실행 단계에 아래 두 줄이 보입니다.

```text
Preview event boost config
Run daily dashboard pipeline and Telegram report
```
