# v1.29.1 Morning Headline Workflow 누락 수정

## 문제

v1.29 패치에 `.github/workflows/morning-headline-news.yml` 파일이 누락되었습니다.

원인:
- 기존 저장소에 해당 workflow 파일이 있는 경우만 수정하도록 처리되어 있었습니다.
- 현재 GitHub 저장소에는 파일이 없어서 새로 생성되지 않았습니다.

## 해결

아래 파일을 새로 추가하세요.

```text
.github/workflows/morning-headline-news.yml
```

## 적용 후 확인

GitHub Actions 왼쪽 목록에 아래 workflow가 나타나야 합니다.

```text
Morning Headline News Report
```

## 수동 테스트

```text
Actions
→ Morning Headline News Report
→ Run workflow
```

정상 로그:

```text
[daily-hotissue-cardnews result]
issues_preview
chart
insight
```
