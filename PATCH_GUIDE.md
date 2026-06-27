# v1.15 최종 통합본 안내

이번 통합본은 지금까지 분리해서 적용하던 패치를 한 번에 모은 최종본입니다.

## 포함 기능
- 기존 핫이슈 TOP 10 텔레그램 자동 전송
- 대시보드 파이프라인 자동 전송
- 아침 헤드라인 뉴스 이미지 + 텍스트 자동 전송
- 텔레그램 수동 연결 테스트

## GitHub 업로드 대상
ZIP 전체를 기준으로 동일 경로에 업로드/교체하면 됩니다.

## 수동 검수 순서
1. Telegram Send Test
2. Morning Headline News Report
3. Daily AdSense SEO Hot Issue Report
4. AdSense Dashboard Pipeline Report

## 참고
자동 실행 안정성을 위해 정각 대신 07분/10분/17분 스케줄을 사용합니다.
