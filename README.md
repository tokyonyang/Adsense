# AdSense SEO 자동화 스타터

트렌드 키워드를 수집하고, Gemini로 SEO 초안을 만든 뒤 WordPress에 `draft` 상태로 업로드하는 자동화 패키지입니다.

## 기본 원칙
- 기본값은 자동 게시가 아니라 WordPress `draft` 생성입니다.
- 대량 자동 생성/복붙 글이 아니라 사람이 검수할 수 있는 초안을 만듭니다.
- Google 정책상 순위 조작 목적의 대량 저가치 페이지 생성은 위험합니다.
- AdSense 승인/수익을 보장하지 않습니다.

## 로컬 실행
```bash
pip install -r requirements.txt
cp .env.example .env
python main.py --max-keywords 10 --max-posts 3
```

## GitHub Secrets
```text
GEMINI_API_KEY
WP_SITE_URL
WP_USERNAME
WP_APP_PASSWORD
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

## 운영 추천
1. 매일 오전 트렌드 후보 수집
2. 민감/위험 키워드 제외
3. 키워드별 글 초안 생성
4. WordPress draft 업로드
5. 텔레그램으로 초안 링크 알림
6. 사람이 검수 후 발행
