# v1.24 헤드라인 List 기준 카드뉴스 패치

## 문제

v1.23 카드뉴스는 기존 헤드라인 뉴스 List를 기준으로 만든 것이 아니라, 별도 뉴스 후보를 다시 수집/군집화해서 만들었습니다.

그래서 사용자가 받은 헤드라인 목록과 카드뉴스 내용이 달라질 수 있었습니다.

## 해결

v1.24에서는 아래 구조로 변경합니다.

```text
1. 헤드라인 뉴스 List를 먼저 생성
2. 각 헤드라인을 anchor로 고정
3. anchor별 유사 기사 3개 검색
4. 해당 3개 기사 기반 3줄 요약
5. 카드뉴스 7장 생성
6. 원문 링크 텍스트 전송
```

## 교체/추가할 파일

```text
app/services/headline_anchor_service.py
app/services/headline_cardnews_summary_service.py
app/jobs/send_headline_cardnews_report.py
.github/workflows/morning-headline-news.yml
docs/morning_headline_anchor_cardnews_v1_24.md
```

> v1.23에서 추가한 아래 파일은 그대로 사용합니다.
>
> ```text
> app/services/headline_cardnews_render_service.py
> app/services/telegram_album_service.py
> ```

## 수동 테스트

```text
Actions
→ Morning Headline News Report
→ Run workflow
```

## 반드시 확인할 로그

```text
[anchor headlines]
[anchor groups]
[anchor-cardnews result]
```

여기서 `[anchor headlines]`가 카드뉴스 생성 기준입니다.

## 운영 검증 기준

카드뉴스 2~6페이지의 제목이 `[anchor headlines]` 순서와 같은 흐름이면 정상입니다.
