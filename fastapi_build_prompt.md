너는 기존 Python 자동화 코드를 FastAPI 백엔드 서비스로 전환하는 시니어 백엔드 개발자다.

목표:
AdSense SEO 자동화 대시보드에서 호출할 수 있는 API 서버를 만든다.

기존 기능:
- Google Trends RSS 키워드 수집
- Naver News API 뉴스 후보/근거자료 수집
- Naver DataLab 상대지수 반영
- Gemini API SEO 글 초안 생성
- Telegram 전송
- WordPress REST API 발행

추가 기능:
- SNS 트렌드 수집
- 경제지표 캘린더 관리
- SEO 검수
- 제목/썸네일 A/B 후보 생성
- 사용자별 최적화
- 발행 캘린더

구조:
app/
  main.py
  core/
    config.py
    security.py
    logger.py
  routers/
    dashboard.py
    keywords.py
    issues.py
    evidence.py
    sns_trends.py
    economic_events.py
    content.py
    publish.py
    profile.py
    logs.py
    support.py
  services/
    keyword_service.py
    sns_trend_service.py
    economic_calendar_service.py
    evidence_service.py
    article_service.py
    cardnews_service.py
    seo_check_service.py
    publish_service.py
  repositories/
    supabase_client.py
  schemas/
    common.py
    keyword.py
    sns.py
    economic_event.py
    content.py
    profile.py

요구사항:
- 모든 API는 JSON 반환
- user_id 기준 데이터 분리
- Supabase service role key는 서버에서만 사용
- 외부 API 실패 시 전체 파이프라인이 중단되지 않도록 방어
- 실행 기록은 dashboard_runs에 저장
- 오류 메시지는 한국어로 변환
- 긴 작업은 BackgroundTasks 또는 별도 worker로 분리 가능하게 설계
