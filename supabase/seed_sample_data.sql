-- 테스트용 샘플 데이터
-- 실제 사용자 인증 전에는 user_id를 null로 둔 공용 샘플로 테스트할 수 있습니다.

insert into dashboard_runs (run_type, status, summary)
values
('sample_seed', 'success', '{"message":"sample data inserted"}');

insert into trend_keywords
(keyword, category, source, approx_traffic, naver_news_count, datalab_score, interest_score, evidence_count, adsense_safety, commerce_score, content_score, status)
values
('기준금리 전망', 'economy', 'google/naver', 5000, 18, 83, 92, 18, 'caution', 20, 90, 'selected'),
('원달러 환율', 'economy', 'google/naver', 10000, 21, 88, 91, 21, 'caution', 25, 88, 'selected'),
('전기요금 절약', 'living', 'naver/google', 4200, 11, 76, 84, 11, 'safe', 50, 86, 'candidate');

insert into sns_trends
(platform, keyword, hashtag, category, rank, trend_score, spread_signal, content_usage, commerce_score, adsense_safety)
values
('youtube', '원달러 환율', null, 'economy', 1, 91, 'hot', 'article', 20, 'caution'),
('tiktok', '여름쿨링템', '#여름쿨링템', 'commerce', 2, 88, 'hot', 'commerce', 95, 'safe'),
('naver', '전기요금 절약', null, 'living', 3, 84, 'rising', 'article', 55, 'safe');

insert into economic_events
(event_date, event_time, country, currency, event_name, event_type, importance, previous_value, forecast_value, content_usage, status, note)
values
(current_date, '21:30', '미국', 'USD', 'PCE 물가지수', 'inflation', 'critical', '2.8%', '2.7%', 'article', 'scheduled', '금리/환율/증시 후속글 소재'),
(current_date + 1, '23:00', '미국', 'USD', '소비자신뢰지수', 'sentiment', 'high', '102.0', '101.5', 'watch', 'scheduled', '경기심리 콘텐츠 후보');

insert into content_ideas
(idea_type, title, hook_point, writing_angle, meta_description, tags, category, priority, status)
values
('article', '기준금리 인하 가능성, 시장에 미치는 영향은?', '내 대출 이자는 언제 내려갈까?', '대출·예금·부동산·주식시장 영향 정리', '기준금리 전망과 생활경제 영향을 쉽게 정리합니다.', array['기준금리','대출금리','경제전망'], 'economy', 1, 'candidate');
