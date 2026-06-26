# AdSense SEO 자동화 스타터

트렌드 키워드를 수집하고, Gemini로 SEO 초안을 만든 뒤 WordPress에 `draft` 상태로 업로드하는 자동화 패키지입니다.

## 이번 수정 사항
- 텔레그램 채널 메시지에 `\n\n`이 그대로 노출되던 문제를 수정했습니다.
- Gemini 프롬프트 템플릿의 JSON 예시 중괄호 때문에 `KeyError('\n  "title"')`가 발생하던 문제를 수정했습니다.
- Gemini 응답이 ```json 코드블록으로 와도 JSON만 추출하도록 보강했습니다.
- `日本 対 スウェーデン`, `cuaca besok` 같은 비한국어 트렌드 키워드가 섞이지 않도록 기본 필터를 추가했습니다.
- 텔레그램 HTML 파싱 오류를 줄이기 위해 제목/키워드/오류 메시지를 escape 처리했습니다.

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

WordPress 업로드 없이 로컬 리포트와 텔레그램 테스트만 하려면:

```bash
python main.py --max-keywords 10 --max-posts 3 --no-wordpress
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

## TELEGRAM_CHAT_ID 설정
채널로 보내려면 봇 개인 대화 ID가 아니라 채널 ID를 넣어야 합니다.

공개 채널이면:
```text
TELEGRAM_CHAT_ID=@채널사용자명
```

비공개 채널이면:
```text
TELEGRAM_CHAT_ID=-100xxxxxxxxxx
```

봇은 해당 채널의 관리자여야 하며, 메시지 게시 권한이 필요합니다.

## 한국어 키워드 필터
기본값은 한글이 포함된 키워드만 허용합니다.
영어 키워드도 허용하려면 GitHub Actions 변수 또는 환경변수에 아래 값을 넣으세요.

```text
ALLOW_ENGLISH_KEYWORDS=true
```

## 운영 추천
1. 매일 오전 트렌드 후보 수집
2. 민감/위험 키워드 제외
3. 키워드별 글 초안 생성
4. WordPress draft 업로드
5. 텔레그램으로 초안 링크 알림
6. 사람이 검수 후 발행
