# main.py 복구 및 수동 패치 가이드

## 먼저 해야 할 일

v1.26 ZIP 안의 `main.py`를 그대로 업로드했다면, 기존 자동화 본문이 사라졌을 가능성이 큽니다.

반드시 GitHub에서 이전 `main.py`로 되돌린 뒤 아래 수동 패치만 반영하세요.

## GitHub에서 main.py 복구 방법

1. GitHub 저장소로 이동
2. `main.py` 파일 클릭
3. 우측 상단 `History` 클릭
4. v1.26 적용 전 커밋 선택
5. 해당 시점의 `main.py` 내용을 복사
6. 현재 `main.py`에 붙여넣고 Commit

또는 최근 커밋 자체를 Revert해도 됩니다.

## 복구 후 main.py에 추가할 코드

### 1. import 추가

`main.py` 상단 import 영역에 아래를 추가하세요.

```python
from app.services.hotissue_category_policy import (
    apply_hotissue_category_policy,
    category_mix_text,
    policy_debug_text,
)
```

### 2. TOP 10 선발 부분만 교체

기존 코드에서 아래와 비슷한 부분을 찾으세요.

```python
top_items = sorted(scored_items, key=lambda x: x["score"], reverse=True)[:10]
```

또는

```python
items = items[:10]
```

또는

```python
report_items = scored_items[:10]
```

이 부분을 아래처럼 바꾸세요.

```python
top_items = apply_hotissue_category_policy(scored_items)
```

변수명이 다를 수 있으므로 기존 코드 변수명에 맞춰야 합니다.

예를 들어 기존 변수가 `items`라면:

```python
items = apply_hotissue_category_policy(items)
```

기존 변수가 `report_items`라면:

```python
report_items = apply_hotissue_category_policy(scored_items)
```

### 3. 텔레그램 리포트에 검증 문구 추가

리포트 메시지를 만드는 `lines` 또는 `message_lines` 아래쪽에 추가하세요.

```python
lines.append("")
lines.append("📊 카테고리 정책")
lines.append(policy_debug_text())
lines.append(f"카테고리 구성: {category_mix_text(top_items)}")
```

여기서 `top_items`는 실제 리포트에 사용되는 TOP 10 변수명으로 맞춰야 합니다.

## 주의

`main.py`는 프로젝트의 핵심 실행 파일이므로 전체 교체하면 안 됩니다.
v1.26.1부터 ZIP에는 `main.py`를 포함하지 않습니다.
