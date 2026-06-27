# v1.22 아침 헤드라인 프리미엄 이미지 개선

## 문제

텔레그램으로 전송되는 이미지는 Pillow로 직접 그리는 방식이라 디자인 퀄리티가 낮았습니다.

## 해결

Pillow 직접 드로잉 대신 HTML/CSS 템플릿을 만들고 Playwright로 고해상도 PNG를 캡처합니다.

## 주요 변경

- 10개 카드 → 8개 카드로 축소
- 카드당 여백/타이포 개선
- 카테고리 색상 개선
- 출처/원문 링크 영역 포함
- HTML/CSS 기반 고해상도 렌더링
- HEADLINE_IMAGE_SCALE=2 적용
- 텍스트 메시지에 원문 URL 포함
- 원본 화질 보존용 sendDocument 옵션 추가

## 옵션

```text
HEADLINE_SEND_AS_DOCUMENT=false
```

false: 텔레그램에서 이미지로 바로 표시  
true: 원본 화질 보존용 파일로 전송

## 설치

workflow에서 자동 설치합니다.

```bash
pip install playwright
python -m playwright install --with-deps chromium
```
