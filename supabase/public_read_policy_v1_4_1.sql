-- v1.4.1 Vercel 정적 대시보드 읽기 전용 정책
-- 이미 v1.4 SQL을 실행했다면 다시 실행해도 됩니다.

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
