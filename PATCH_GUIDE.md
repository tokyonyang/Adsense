# v1.26.1 안전 패치

## 왜 다시 만들었나

v1.26 ZIP에 포함된 `main.py`는 전체 교체용이 아니라 패치 안내용이었습니다.  
그런데 파일명이 `main.py`라서 그대로 업로드하면 기존 자동화 코드가 사라질 수 있습니다.

v1.26.1에서는 `main.py`를 제외했습니다.

## 먼저 할 일

이미 v1.26의 `main.py`를 그대로 업로드했다면:

```text
GitHub → main.py → History → v1.26 적용 전 main.py로 복구
```

복구 후 아래 파일만 적용하세요.

## 적용할 파일

```text
app/services/hotissue_category_policy.py
.github/workflows/daily-adsense-seo.yml
.github/workflows/morning-headline-news.yml
docs/daily_hotissue_finance_priority_v1_26.md
docs/MAIN_PY_RESTORE_AND_PATCH_GUIDE.md
```

## main.py는 수동 수정

`docs/MAIN_PY_RESTORE_AND_PATCH_GUIDE.md`를 보고 기존 main.py 안에 아래 3가지만 반영하세요.

1. import 추가
2. TOP 10 자르는 부분을 `apply_hotissue_category_policy(...)`로 변경
3. 리포트에 카테고리 정책/구성 문구 추가

## 테스트

```text
Actions
→ Daily AdSense SEO Hot Issue Report
→ Run workflow
```

정상 결과에 아래가 보여야 합니다.

```text
📊 카테고리 정책
모드=finance_first ...
카테고리 구성: 경제·금융 2개 / 증권·투자 2개 ...
```
