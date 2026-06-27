# v1.19 헤드라인 뉴스 이미지 정합성 개선 패치

## 교체할 파일

```text
app/jobs/send_headline_news_report.py
app/services/headline_news_image_service.py
docs/morning_headline_image_alignment_v1_19.md
```

## 해결하는 문제

- 헤드라인 이미지 카드 내용이 실제 기사와 잘 맞지 않는 문제
- placeholder 문구가 반복되는 문제
- 텍스트 메시지와 이미지 카드가 다른 데이터를 쓰는 문제

## 핵심 변경

1. 이미지 카드 제목 = `headline_text` 우선
2. 카드 bullet = 기사 내용 기반 `summaries`
3. 상투 문구 자동 제거
4. fallback도 기사 description 기반 생성
5. 실행 로그에 `briefs preview` 출력

## 테스트 방법

```text
Actions
→ Morning Headline News Report
→ Run workflow
```

실행 후:
1. 텔레그램 텍스트 메시지 확인
2. 텔레그램 이미지 카드 확인
3. GitHub Actions 로그에서 `briefs preview` 확인

세 결과가 서로 비슷한 내용이면 정상입니다.
