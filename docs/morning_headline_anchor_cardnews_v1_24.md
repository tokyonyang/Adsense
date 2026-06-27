# v1.24 헤드라인 List 기준 카드뉴스

## 왜 수정했나

v1.23은 카드뉴스를 만들 때 별도 뉴스 수집/클러스터링 결과를 기준으로 이슈를 다시 뽑았습니다.  
그래서 실제 텔레그램에 먼저 전송된 `아침 헤드라인 뉴스 List`와 카드뉴스 내용이 달라질 수 있었습니다.

## v1.24 핵심

카드뉴스 생성 기준을 아래처럼 바꿨습니다.

```text
헤드라인 뉴스 List 생성
→ 각 헤드라인을 anchor로 고정
→ anchor별 유사 기사 3개 검색
→ anchor 기준 3줄 요약
→ 카드뉴스 7장 생성
→ 원문 링크 전송
```

## 검증 로그

Actions 로그에 아래가 출력됩니다.

```text
[anchor headlines]
1. [산업] 미 정부, 앤트로픽...
2. [정치] 총리 청문회...
...

[anchor groups]
1. 미 정부, 앤트로픽... · related_articles=3
2. 총리 청문회... · related_articles=3

[anchor-cardnews result]
anchor_preview
issues_preview
```

`anchor_preview`가 실제 카드뉴스 기준 목록입니다.

## 기대 효과

- 카드뉴스가 헤드라인 뉴스 List와 따로 놀지 않음
- 기존 List의 순위와 제목을 기준으로 카드뉴스 생성
- 유사 기사 3개는 보조 자료로만 사용
- 원문 링크는 마지막 텍스트 메시지로 제공
