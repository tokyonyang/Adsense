# AdSense 자동화 / Daily Hot Issue / Morning Headline 정리본

생성일: 2026-06-28 00:32:02 KST

---

## 1. 현재 프로젝트 목표

현재 자동화의 최종 목표는 다음과 같다.

```text
1. Daily AdSense SEO Hot Issue Report
   → 오늘의 전체 핫이슈 마스터 데이터 생성

2. Morning Headline News Report
   → Daily Hot Issue 데이터를 기반으로 카드뉴스형 아침 브리핑 생성

3. Telegram 전송
   → Daily 리포트는 텍스트 중심
   → Morning 리포트는 카드뉴스 이미지 앨범 + 원문 링크 텍스트
```

중요한 방향성은 **Daily와 Morning이 따로 뉴스 후보를 뽑지 않고, Daily를 마스터 소스로 삼는 것**이다.

---

## 2. 지금까지 발견한 핵심 문제

### 2.1 Morning Headline 이미지 품질 문제

초기 Morning Headline 이미지는 `Pillow`로 단순 도형과 텍스트를 직접 그리는 방식이었다.

문제점:

```text
- 카드 디자인 퀄리티가 낮음
- 한 장에 너무 많은 뉴스를 압축
- 헤드라인 제목 이외의 내용이 부족
- 기사 요약이 실제 기사 내용과 맞지 않음
- 텔레그램에서 이미지가 흐릿하거나 저퀄리티로 보임
```

해결 방향:

```text
- 한 장짜리 종합 이미지 중단
- 카드뉴스형 6~7장 구조로 변경
- HTML/CSS 기반 프리미엄 카드 디자인
- Playwright로 고해상도 PNG 렌더링
- 텔레그램 media group으로 앨범 전송
```

---

### 2.2 Morning Headline과 Daily Hot Issue 불일치 문제

사용자가 확인한 결과, Daily Hot Issue와 Morning Headline이 전혀 다른 뉴스 기준으로 움직였다.

원인:

```text
Morning Headline이 자체적으로 뉴스 후보를 다시 수집하고 있었음
Daily Hot Issue TOP 10과 별도 로직으로 움직였음
```

정상 방향:

```text
Daily AdSense SEO Hot Issue Report
= 마스터 이슈 데이터

Morning Headline News Report
= Daily Hot Issue TOP Item 기반 카드뉴스
```

즉, Morning은 새로 뉴스를 뽑는 것이 아니라 **Daily에서 이미 뽑은 이슈를 카드뉴스화**해야 한다.

---

### 2.3 Daily Hot Issue 카테고리 쏠림 문제

최근 Daily Hot Issue 결과는 다음과 같이 스포츠, 연예, 기타 키워드가 많이 상단에 노출되었다.

예시:

```text
로또1230
오스틴 딘
오십프로
농구
류승민
박영진
후지 산
이승우
비야디
신상진
```

문제점:

```text
- 애드센스/뉴스 블로그 운영 목적상 경제·금융·정책·산업 이슈가 부족
- 연예/스포츠/기타 이슈가 트렌드 점수만으로 상위권을 차지
- Morning Headline으로 활용하기에도 이슈 밀도가 낮음
```

해결 방향:

```text
- Daily TOP 10을 단순 점수순이 아니라 카테고리 정책 기반으로 선발
- 경제/금융·증권·산업·정책을 우선
- 연예/스포츠/기타는 완전 제외가 아니라 후순위 및 개수 제한
```

---

### 2.4 main.py 덮어쓰기 사고

v1.26 패치에서 `main.py`를 안내용 파일로 제공했는데, 파일명이 `main.py`라서 그대로 업로드하면 기존 실행 로직이 사라지는 문제가 발생했다.

이후 대응:

```text
v1.26.1
- main.py 제외 안전 패치 제공

v1.26.2
- 전체 교체 가능한 Daily Hot Issue용 main.py 제공
```

주의:

```text
v1.26.2 main.py는 Daily Hot Issue Report 복구/개선용 전체 교체본이다.
기존 main.py에 WordPress 자동 발행, Gemini 초안 생성 등 추가 기능이 있었다면 포함하지 않았다.
```

---

## 3. 버전별 진행 정리

## v1.13 ~ v1.14: Morning Headline 기본 기능

구현 내용:

```text
- 아침 헤드라인 뉴스 텍스트 리포트
- 텔레그램 전송
- 카드형 뉴스 이미지 PNG 생성
- 실행 시간 07:10 → 06:10으로 변경
```

한계:

```text
- 이미지가 단순함
- 기사 제목이 잘림
- 내용 요약 품질 낮음
```

---

## v1.17 ~ v1.19: Morning Headline 품질 보정

수정 내용:

```text
- 오늘의 주요뉴스, 뉴스브리핑 등 종합 기사 제외
- 제목 잘림 방지
- Gemini로 headline_text 생성
- 이미지와 텍스트가 같은 headline_text/summaries 사용
```

한계:

```text
- 오래된 뉴스가 섞임
- 이미지 bullet이 여전히 일반 문구처럼 보임
```

---

## v1.20 ~ v1.21: 최신성 필터

v1.20:

```text
- 24시간 이내 우선
- 부족하면 48시간까지 확장
- 48시간보다 오래된 뉴스 금지
```

문제:

```text
후보가 0개일 때 workflow 실패
```

v1.21:

```text
- 24h → 48h → 날짜 포함 재검색 → 72h → 날짜 불명 후보
- 후보 0개여도 workflow 실패하지 않도록 수정
```

한계:

```text
Morning 자체 수집 구조는 여전히 Daily와 분리되어 있었음
```

---

## v1.22: 프리미엄 이미지 렌더링

핵심 변경:

```text
기존: Pillow 직접 이미지 생성
변경: HTML/CSS 템플릿 → Playwright 고해상도 PNG 캡처
```

개선:

```text
- 카드 10개 → 8개
- 블랙/골드 프리미엄 디자인
- 출처/원문 링크 영역 추가
- 텍스트 메시지에 실제 뉴스 URL 포함
- HEADLINE_IMAGE_SCALE=2
```

한계:

```text
한 장에 여전히 여러 뉴스를 압축
헤드라인 제목 외 내용이 부족
```

---

## v1.23: 카드뉴스형 구조

목표:

```text
- 표지 1장
- 이슈 카드 5장
- 마무리 1장
- 총 7장 카드뉴스
```

기능:

```text
- 유사 기사 클러스터링
- 이슈당 3줄 요약
- Telegram media group 전송
- 원문 링크 텍스트 별도 전송
```

문제:

```text
Daily Hot Issue List를 기준으로 만든 것이 아니라
별도 뉴스 후보를 다시 수집해서 카드뉴스를 생성함
```

---

## v1.24: 헤드라인 List 기준 카드뉴스

수정 방향:

```text
헤드라인 뉴스 List 생성
→ 각 헤드라인을 anchor로 고정
→ anchor별 유사 기사 3개 검색
→ anchor 기준 3줄 요약
→ 카드뉴스 생성
```

한계:

```text
여전히 Daily Hot Issue Report와 Morning Headline의 기준 데이터가 완전히 통합된 것은 아님
```

---

## v1.25: Daily Hot Issue 마스터 소스화

핵심 방향:

```text
Daily AdSense SEO Hot Issue Report
= 마스터 이슈 데이터

Morning Headline News Report
= Daily HOT Issue TOP Item을 카드뉴스화
```

추가 개선:

```text
- Daily TOP 10을 카테고리별 1~2개 균형 선발
- 스포츠/연예/기타 쏠림 완화
- 카테고리 분류 보정
```

한계:

```text
균형형이라 경제/금융 우선 운영에는 다소 약함
```

---

## v1.26: 경제/금융 우선 옵션

추가한 운영 모드:

```text
finance_first  → 경제/금융·증권·산업·정책 우선
balanced       → 카테고리별 균형
all_score      → 전체 점수순
```

기본값:

```yaml
HOT_ISSUE_CATEGORY_MODE: "finance_first"

HOT_ISSUE_PRIORITY_CATEGORIES: "경제·금융,증권·투자,산업·기업,정책·지원금,부동산·주거금융,생활·제도,국제"

HOT_ISSUE_PRIORITY_MIN: 6
HOT_ISSUE_PRIORITY_MAX: 8

HOT_ISSUE_LOW_PRIORITY_CATEGORIES: "연예·문화,스포츠,기타"
HOT_ISSUE_LOW_PRIORITY_MAX: 2
HOT_ISSUE_OTHER_MAX: 1
```

더 강한 경제/금융 중심 옵션:

```yaml
HOT_ISSUE_PRIORITY_MIN: 8
HOT_ISSUE_PRIORITY_MAX: 9
HOT_ISSUE_LOW_PRIORITY_MAX: 1
HOT_ISSUE_OTHER_MAX: 0
```

---

## v1.26.2: main.py 전체 교체본

제공 파일:

```text
main.py
README_MAIN_FULL_REPLACEMENT_v1_26_2.md
```

기능:

```text
1. Google Trends RSS 키워드 수집
2. 경제/금융 우선 seed 키워드 추가
3. Naver News API 근거자료 수집
4. Google News RSS fallback
5. 기사 제목/설명 기반 카테고리 재분류
6. 경제/금융 우선 정책 적용
7. Daily HOT Issue TOP 10 생성
8. 텔레그램 전송
9. reports/*.json, reports/*.txt 저장
```

주의:

```text
Daily Hot Issue Report 복구/개선용 전체 main.py이다.
기존 WordPress 자동 발행이나 Gemini 초안 생성 등 부가 기능은 포함하지 않았다.
```

---

## 4. 현재 권장 아키텍처

최종적으로 추천하는 구조는 다음과 같다.

```text
[Daily Workflow]
main.py
→ 후보 키워드 수집
→ 경제/금융 우선 카테고리 정책 적용
→ TOP 10 선정
→ Telegram Daily Report 전송
→ reports/latest_daily_hotissue.json 저장

[Morning Workflow]
send_headline_cardnews_report.py
→ reports/latest_daily_hotissue.json 읽기
→ TOP 10 중 상위 5개 또는 설정값 선택
→ 각 이슈의 근거자료 3개로 3줄 요약
→ 표지 + 이슈 카드 + 마무리 요약 생성
→ Telegram media group 전송
→ 원문 링크 텍스트 전송
```

핵심은 이것이다.

```text
Morning은 절대 독립적으로 뉴스를 다시 뽑지 않는다.
Daily가 만든 latest_daily_hotissue.json을 기준으로만 카드뉴스를 만든다.
```

---

## 5. 현재 남은 검증 과제

## 5.1 Daily Hot Issue 정상 복구 확인

확인할 workflow:

```text
Actions
→ Daily AdSense SEO Hot Issue Report
→ Run workflow
```

정상 결과:

```text
🔥 오늘의 핫이슈 TOP 10

📊 카테고리 정책
모드=finance_first ...
카테고리 구성: 경제·금융 n개 / 증권·투자 n개 / 산업·기업 n개 ...
```

확인할 파일:

```text
reports/latest_daily_hotissue.json
reports/latest_daily_hotissue_report.txt
reports/daily_hotissue_items_YYYYMMDD.json
reports/idea_items_YYYYMMDD.json
```

---

## 5.2 Daily 결과의 카테고리 품질 확인

확인해야 할 것:

```text
- 로또/연예/스포츠/기타가 너무 많이 나오지 않는지
- 경제·금융, 증권·투자, 산업·기업, 정책·지원금이 최소 6개 이상 나오는지
- 신상진/후지산/비야디 같은 항목이 적절히 분류되는지
```

필요 시 조정:

```yaml
HOT_ISSUE_PRIORITY_MIN: 8
HOT_ISSUE_PRIORITY_MAX: 9
HOT_ISSUE_LOW_PRIORITY_MAX: 1
HOT_ISSUE_OTHER_MAX: 0
```

---

## 5.3 Morning 카드뉴스가 Daily를 기준으로 생성되는지 확인

확인할 workflow:

```text
Actions
→ Morning Headline News Report
→ Run workflow
```

정상 구조:

```text
Daily Report TOP 10
→ Morning 카드뉴스 이슈 5개
```

확인해야 할 것:

```text
- Morning 카드뉴스 제목이 Daily TOP 10 일부와 일치하는지
- Morning이 독립적으로 이상한 뉴스를 다시 뽑지 않는지
- 카드뉴스에 이슈당 3줄 요약이 충분히 들어가는지
- 원문 링크 텍스트가 함께 오는지
```

---

## 6. 다음 스텝 제안

## Step 1. main.py v1.26.2 적용 및 Daily 복구

먼저 `main.py` 전체 교체본을 적용한다.

적용 대상:

```text
/main.py
```

수동 실행:

```text
Actions
→ Daily AdSense SEO Hot Issue Report
→ Run workflow
```

결과를 보고 다음을 확인한다.

```text
- 텔레그램 리포트 발송 여부
- 카테고리 정책 표시 여부
- 경제/금융 우선 적용 여부
- reports/latest_daily_hotissue.json 생성 여부
```

---

## Step 2. Daily 결과 샘플 검토

사용자가 텔레그램 결과를 공유한다.

검토 항목:

```text
- 경제/금융 우선순위가 충분한지
- 연예/스포츠/기타 비중이 적절한지
- 카테고리 분류가 이상한 항목이 있는지
- 기사 근거자료가 최신성/관련성을 갖는지
```

---

## Step 3. Morning 카드뉴스를 Daily JSON 기준으로 고정

Daily가 안정화되면 Morning을 다음 구조로 고정한다.

```text
reports/latest_daily_hotissue.json
→ Morning Cardnews
```

필요한 수정:

```text
- send_headline_cardnews_report.py에서 독립 수집 제거
- latest_daily_hotissue.json 읽기
- items 상위 5개 선택
- articles 3개 기반 요약
- 카드뉴스 7장 생성
```

---

## Step 4. 카드뉴스 디자인 v1.27 개선

디자인 목표:

```text
- 사용자가 마음에 들어한 블랙/골드 프리미엄 스타일 유지
- 표지 1장
- 이슈 카드 5장
- 마무리 1장
- 페이지당 1개 이슈
- 3줄 요약을 크게 표시
- 하단에 관련 키워드와 출처 표시
```

추가 옵션:

```yaml
HEADLINE_CARDNEWS_ISSUES: 5
HEADLINE_IMAGE_SCALE: 2
HEADLINE_SEND_LINK_DIGEST: "true"
```

---

## 7. 현재 파일 기준 체크리스트

최근 생성된 주요 파일:

```text
daily_hotissue_finance_priority_v1_26_1_safe_patch.zip
main_full_replacement_v1_26_2.zip
```

현재 가장 중요한 파일:

```text
main_full_replacement_v1_26_2.zip
```

적용해야 할 핵심 파일:

```text
main.py
```

---

## 8. 다음 대화에서 바로 이어갈 작업

다음 단계에서 할 일:

```text
1. 사용자가 main.py v1.26.2 적용
2. Daily workflow 수동 실행
3. 텔레그램 결과 공유
4. 카테고리/근거자료 품질 검증
5. 필요하면 카테고리 룰 조정
6. Daily JSON 기반 Morning 카드뉴스 v1.27 구현
```

---

## 9. 중요한 운영 원칙

```text
Daily는 마스터 데이터
Morning은 Daily 기반 카드뉴스
경제/금융은 우선
연예/스포츠/기타는 제한
카드뉴스는 한 장에 몰아넣지 말고 6~7장으로 분할
원문 링크는 텍스트 메시지로 별도 제공
```
