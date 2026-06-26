-- Supabase RLS 정책
-- 실제 Supabase Auth 연결 후 사용하세요.
-- user_id 컬럼에 auth.uid() 값을 저장하는 구조 기준입니다.

alter table user_profiles enable row level security;
alter table user_sites enable row level security;
alter table dashboard_runs enable row level security;
alter table trend_keywords enable row level security;
alter table sns_trends enable row level security;
alter table economic_events enable row level security;
alter table content_ideas enable row level security;
alter table generated_articles enable row level security;
alter table cardnews_drafts enable row level security;
alter table publish_logs enable row level security;
alter table content_calendar enable row level security;
alter table support_tickets enable row level security;
alter table usage_limits enable row level security;

drop policy if exists "user_profiles_select_own" on user_profiles;
create policy "user_profiles_select_own"
on user_profiles for select
using (auth.uid() = user_id);

drop policy if exists "user_profiles_update_own" on user_profiles;
create policy "user_profiles_update_own"
on user_profiles for update
using (auth.uid() = user_id);

drop policy if exists "user_profiles_insert_own" on user_profiles;
create policy "user_profiles_insert_own"
on user_profiles for insert
with check (auth.uid() = user_id);

-- 공통 owner 정책 예시
-- 필요한 테이블마다 동일하게 적용합니다.

drop policy if exists "user_sites_owner_all" on user_sites;
create policy "user_sites_owner_all"
on user_sites for all
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

drop policy if exists "trend_keywords_owner_all" on trend_keywords;
create policy "trend_keywords_owner_all"
on trend_keywords for all
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

drop policy if exists "sns_trends_owner_all" on sns_trends;
create policy "sns_trends_owner_all"
on sns_trends for all
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

drop policy if exists "economic_events_owner_all" on economic_events;
create policy "economic_events_owner_all"
on economic_events for all
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

drop policy if exists "content_ideas_owner_all" on content_ideas;
create policy "content_ideas_owner_all"
on content_ideas for all
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

drop policy if exists "generated_articles_owner_all" on generated_articles;
create policy "generated_articles_owner_all"
on generated_articles for all
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

drop policy if exists "cardnews_drafts_owner_all" on cardnews_drafts;
create policy "cardnews_drafts_owner_all"
on cardnews_drafts for all
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

drop policy if exists "publish_logs_owner_all" on publish_logs;
create policy "publish_logs_owner_all"
on publish_logs for all
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

drop policy if exists "content_calendar_owner_all" on content_calendar;
create policy "content_calendar_owner_all"
on content_calendar for all
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

drop policy if exists "support_tickets_owner_all" on support_tickets;
create policy "support_tickets_owner_all"
on support_tickets for all
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

drop policy if exists "usage_limits_owner_all" on usage_limits;
create policy "usage_limits_owner_all"
on usage_limits for all
using (auth.uid() = user_id)
with check (auth.uid() = user_id);
