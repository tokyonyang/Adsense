# v1.32.1 간밤의 핫이슈 긴급 수정

## 수정 원인

`Overnight Hot Issue Report` 실행 중 아래 에러로 실패했습니다.

```text
NameError: name 'weekday_ko' is not defined
```

## 수정 내용

```text
1. app/services/overnight_hotissue_service.py에 weekday_ko 함수 추가
2. Gemini 모델명을 gemini-1.5-flash 고정값에서 GEMINI_MODEL 환경변수 기반으로 변경
3. 기본 Gemini 모델을 gemini-2.0-flash로 변경
4. 날씨 API timeout을 12초에서 환경변수 기반 20초로 완화
5. 날씨 조회 지역을 13개에서 7개로 축소하여 실행 안정성 개선
6. workflow 파일 5개를 패치에 강제 포함
```

## 변경된 workflow env

```yaml
GEMINI_MODEL: "gemini-2.0-flash"
OVERNIGHT_WEATHER_TIMEOUT: 20
OVERNIGHT_WEATHER_REGIONS: "서울,인천,대전,대구,부산,광주,제주"
```

## 테스트 방법

```text
Actions
→ Overnight Hot Issue Report
→ Run workflow
```

정상 로그:

```text
[overnight-hotissue result]
us_news
korea_news
market_indices
popular_keywords
realtime_keywords
weather_regions
quote
pages
```

## 참고

Gemini 요약이 실패해도 기본 요약 로직으로 fallback 되도록 되어 있습니다.  
날씨 API가 일부 지역에서 timeout 되어도 전체 리포트는 계속 진행됩니다.
