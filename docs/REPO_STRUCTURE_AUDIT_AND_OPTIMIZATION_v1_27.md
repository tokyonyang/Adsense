# AdSense Repository 구조 진단 및 v1.27 최적화안

## 1. 현재 업로드 ZIP에서 확인한 구조

현재 저장소는 크게 4개 축으로 섞여 있습니다.

```text
1. Daily AdSense SEO Hot Issue Report
   - root/main.py
   - trend_sources.py, news_sources.py, naver_sources.py
   - content_generator.py, wp_publisher.py, telegram_notify.py

2. Morning Headline / Cardnews
   - app/jobs/send_headline_cardnews_report.py
   - app/services/daily_hotissue_source.py
   - app/services/headline_cardnews_*.py
   - app/services/telegram_album_service.py

3. Dashboard / FastAPI
   - app/main.py
   - app/routers/*
   - app/repositories/*
   - app/services/dashboard_service.py 등

4. Vercel 정적 대시보드
   - index.html
   - dashboard/index.html
   - dashboard_config.js
```

즉, 하나의 저장소 안에 `Daily 자동화`, `Morning 카드뉴스`, `FastAPI 대시보드`, `정적 대시보드`, `WordPress 초안 생성` 코드가 함께 들어 있습니다.

---

## 2. 가장 큰 구조 문제

### 문제 1. Morning이 호출하는 Daily 소스가 깨져 있음

현재 `app/services/daily_hotissue_source.py`는 과거 `main.py`에 있던 내부 함수에 의존합니다.

```python
_daily_main._env_true(...)
_daily_main._safe_int_env(...)
_daily_main._build_idea_digest_with_fallback(...)
_daily_main._select_hot_issue_items(...)
```

하지만 현재 루트 `main.py`는 v1.26.2 전체 교체본이라 위 함수들이 없습니다.

따라서 Morning workflow는 다음 지점에서 실패할 가능성이 높습니다.

```text
python -m app.jobs.send_headline_cardnews_report
→ build_daily_hotissue_payload()
→ main._env_true 없음
```

### 문제 2. Daily item 구조와 Morning 변환 구조가 맞지 않음

현재 `main.py`가 생성하는 Daily item은 대략 아래 구조입니다.

```json
{
  "keyword": "환율",
  "category": "경제·금융",
  "score": 123.4,
  "articles": [...]
}
```

그런데 기존 `hot_items_to_anchor_groups()`는 구버전 구조인 `news`, `category_label` 중심으로 되어 있습니다.

```python
news = item.get("news") or []
category = item.get("category_label") or item.get("category_id")
```

그래서 Daily에는 근거자료가 있어도 Morning 카드뉴스 변환 단계에서 기사 3개가 제대로 넘어가지 않을 수 있습니다.

### 문제 3. 같은 카테고리 정책이 두 군데에 중복됨

- `main.py` 안에 카테고리 정책 로직 존재
- `app/services/hotissue_category_policy.py`에도 유사 로직 존재

이 구조는 시간이 지나면 서로 다르게 변할 가능성이 큽니다.

### 문제 4. 저장소에 `__pycache__`가 포함됨

현재 ZIP에는 아래와 같은 캐시 파일이 들어 있습니다.

```text
__pycache__/*.pyc
```

GitHub에는 올리지 않는 것이 좋습니다.

### 문제 5. Morning이 Daily 결과를 그대로 쓰는 구조가 아직 완전히 고정되지 않음

운영 원칙은 다음이어야 합니다.

```text
Daily = 마스터 HOT Issue 데이터
Morning = Daily HOT Issue 기반 카드뉴스
```

이를 위해서는 Daily와 Morning이 같은 엔진을 호출해야 합니다.

---

## 3. v1.27 최적화 방향

### 핵심 원칙

```text
Daily HOT Issue 엔진을 단일화한다.
Morning은 이 엔진의 결과만 사용한다.
main.py는 실행 진입점만 담당한다.
```

### 변경 후 구조

```text
main.py
→ app.services.daily_hotissue_engine.main()

app/services/daily_hotissue_engine.py
→ Daily HOT Issue 수집/분류/점수/리포트/저장 전체 담당

app/services/daily_hotissue_source.py
→ Morning 카드뉴스용 payload adapter

app/jobs/send_headline_cardnews_report.py
→ Daily payload 기반 카드뉴스 생성
```

---

## 4. v1.27 패치 내용

### 새 파일

```text
app/services/daily_hotissue_engine.py
```

루트 `main.py`에 있던 Daily HOT Issue 실행 로직을 서비스 엔진으로 분리했습니다.

### 교체 파일

```text
main.py
app/services/daily_hotissue_source.py
app/services/hotissue_category_policy.py
app/services/headline_cardnews_render_service.py
```

### 보강 파일

```text
.gitignore
```

---

## 5. v1.27에서 해결되는 것

### Daily와 Morning 기준 통합

기존:

```text
Daily: main.py 자체 로직
Morning: daily_hotissue_source.py가 과거 main.py 내부 함수 호출
```

변경:

```text
Daily: daily_hotissue_engine 호출
Morning: daily_hotissue_engine 호출
```

### Morning 카드뉴스 기사 누락 개선

기존에는 Daily item의 `articles`를 제대로 읽지 못할 수 있었습니다.

변경 후에는 아래 구조를 모두 지원합니다.

```text
v1.26.2 구조: item["articles"]
구버전 구조: item["news"]
```

### 카테고리 표시 개선

카드뉴스 렌더러가 `경제·금융`, `증권·투자`, `산업·기업`, `정책·지원금` 같은 현재 카테고리명을 직접 인식하도록 보강했습니다.

### GitHub 업로드 정리

`.gitignore`를 추가해 다음 파일이 더 이상 올라가지 않도록 했습니다.

```text
__pycache__/
*.pyc
reports/
tmp/
.env
```

---

## 6. 적용 순서

1. v1.27 ZIP의 파일을 같은 경로에 업로드/교체합니다.
2. GitHub에서 기존 `__pycache__` 폴더는 삭제합니다.
3. Daily workflow를 수동 실행합니다.
4. Morning workflow를 수동 실행합니다.

---

## 7. 테스트 순서

### 1차: Daily 테스트

```text
Actions
→ Daily AdSense SEO Hot Issue Report
→ Run workflow
```

확인할 로그:

```text
[Daily AdSense SEO Hot Issue Report]
Policy: 모드=finance_first ...
[candidates]
[selected category mix]
[reports] saved
[telegram] sent
```

확인할 텔레그램 문구:

```text
🔥 오늘의 핫이슈 TOP 10
📊 카테고리 정책
카테고리 구성: ...
```

### 2차: Morning 테스트

```text
Actions
→ Morning Headline News Report
→ Run workflow
```

확인할 로그:

```text
[daily-hotissue-cardnews result]
hot_items
cardnews_issues
pages
issues_preview
```

확인할 텔레그램 결과:

```text
카드뉴스 이미지 앨범
원문 링크 텍스트 메시지
```

---

## 8. 다음 단계 제안

v1.27 적용 후 결과가 정상이라면 다음 단계는 다음입니다.

```text
v1.28: Daily HOT Issue 품질 개선
- 경제/금융 seed 고도화
- 저품질 언론/잡음 키워드 제외
- 로또/연예/스포츠 상한 더 정교화
- 같은 이슈 중복 제거 강화

v1.29: Morning 카드뉴스 디자인 고도화
- 페이지당 요약 가독성 향상
- 링크/출처 표기 개선
- 카테고리별 아이콘/색상 세분화
```
