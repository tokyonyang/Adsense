-- v1.5 테스트용 추가 샘플 데이터
-- 데이터가 비어 있을 때만 실행해도 됩니다.
-- user_id is null 상태로 들어가므로 v1.4.1 public read policy에서 읽을 수 있습니다.

insert into economic_events
(event_date, event_time, country, currency, event_name, event_type, importance, previous_value, forecast_value, actual_value, content_usage, status, note)
values
(current_date, '21:30', '미국', 'USD', 'PCE 물가지수', 'inflation', 'critical', '2.8%', '2.7%', null, 'article', 'scheduled', '금리/환율/증시 후속글 소재'),
(current_date + 1, '23:00', '미국', 'USD', '소비자신뢰지수', 'sentiment', 'high', '102.0', '101.5', null, 'watch', 'scheduled', '경기심리 콘텐츠 후보'),
(current_date + 2, '08:00', '한국', 'KRW', '소비자물가지수', 'inflation', 'high', '2.7%', '2.6%', null, 'cardnews', 'scheduled', '생활물가 카드뉴스 후보');

insert into content_ideas
(idea_type, title, hook_point, writing_angle, meta_description, tags, category, priority, status)
values
('article', 'PCE 물가지수 발표, 금리와 환율에 미치는 영향은?', '연준이 주목하는 물가지표', 'PCE 발표 전후로 금리·환율·증시 흐름을 쉽게 정리', 'PCE 물가지수 발표가 금리와 환율에 미치는 영향을 정리합니다.', array['PCE','금리','환율'], 'economy', 92, 'candidate'),
('cardnews', '전기요금 절약 방법 7가지', '여름철 전기요금 부담 줄이기', '생활비 부담을 줄이는 실천형 절약 팁', '전기요금 절약 방법을 쉽게 정리했습니다.', array['전기요금','생활정보','절약'], 'living', 84, 'candidate'),
('article', 'AI 반도체 이슈 한눈에 보기', '시장 주도주를 이해하는 쉬운 설명', 'AI 수요와 반도체 기업 실적을 연결한 해설형 콘텐츠', 'AI 반도체 이슈와 시장 흐름을 정리합니다.', array['AI','반도체','기업분석'], 'business', 78, 'candidate');

insert into content_calendar
(title, calendar_type, scheduled_at, status, category, note)
values
('PCE 물가지수 발표 전 전망 글', 'draft', now() + interval '3 hours', 'scheduled', 'economy', '발표 전 전망형 콘텐츠'),
('전기요금 절약 카드뉴스', 'cardnews', now() + interval '6 hours', 'scheduled', 'living', '생활정보 카드뉴스 제작'),
('AI 반도체 이슈 발행', 'publish', now() + interval '1 day', 'scheduled', 'business', '워드프레스 발행 예정');
