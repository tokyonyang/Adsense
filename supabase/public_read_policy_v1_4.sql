-- v1.4 Vercel 정적 대시보드 읽기 전용 정책
-- 목적:
-- 브라우저에서 Supabase anon public key로 목업/자동수집 데이터를 읽기 위해 사용합니다.
--
-- 중요:
-- service_role key는 절대 브라우저에 노출하지 마세요.
-- 이 정책은 user_id가 null인 공용 운영 데이터만 읽을 수 있게 합니다.
-- 개인 회원 데이터 연결 전까지의 운영자 단일모드용입니다.

grant usage on schema public to anon;

grant select on trend_keywords to anon;
grant select on sns_trends to anon;
grant select on dashboard_runs to anon;
grant select on economic_events to anon;
grant select on content_ideas to anon;
grant select on generated_articles to anon;
grant select on cardnews_drafts to anon;
grant select on publish_logs to anon;
grant select on content_calendar to anon;

alter table trend_keywords enable row level security;
alter table sns_trends enable row level security;
alter table dashboard_runs enable row level security;
alter table economic_events enable row level security;
alter table content_ideas enable row level security;
alter table generated_articles enable row level security;
alter table cardnews_drafts enable row level security;
alter table publish_logs enable row level security;
alter table content_calendar enable row level security;

drop policy if exists "public_read_null_user_trend_keywords_v14" on trend_keywords;
create policy "public_read_null_user_trend_keywords_v14"
on trend_keywords for select
to anon
using (user_id is null);

drop policy if exists "public_read_null_user_sns_trends_v14" on sns_trends;
create policy "public_read_null_user_sns_trends_v14"
on sns_trends for select
to anon
using (user_id is null);

drop policy if exists "public_read_null_user_dashboard_runs_v14" on dashboard_runs;
create policy "public_read_null_user_dashboard_runs_v14"
on dashboard_runs for select
to anon
using (user_id is null);

drop policy if exists "public_read_null_user_economic_events_v14" on economic_events;
create policy "public_read_null_user_economic_events_v14"
on economic_events for select
to anon
using (user_id is null);

drop policy if exists "public_read_null_user_content_ideas_v14" on content_ideas;
create policy "public_read_null_user_content_ideas_v14"
on content_ideas for select
to anon
using (user_id is null);

drop policy if exists "public_read_null_user_generated_articles_v14" on generated_articles;
create policy "public_read_null_user_generated_articles_v14"
on generated_articles for select
to anon
using (user_id is null);

drop policy if exists "public_read_null_user_cardnews_drafts_v14" on cardnews_drafts;
create policy "public_read_null_user_cardnews_drafts_v14"
on cardnews_drafts for select
to anon
using (user_id is null);

drop policy if exists "public_read_null_user_publish_logs_v14" on publish_logs;
create policy "public_read_null_user_publish_logs_v14"
on publish_logs for select
to anon
using (user_id is null);

drop policy if exists "public_read_null_user_content_calendar_v14" on content_calendar;
create policy "public_read_null_user_content_calendar_v14"
on content_calendar for select
to anon
using (user_id is null);
