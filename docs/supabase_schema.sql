-- AdSense SEO 자동화 대시보드 Supabase Schema v1
-- 목적: 사용자별 최적화, 키워드 수집, SNS 트렌드, 경제지표, 콘텐츠 제작/발행 흐름 저장

create extension if not exists "pgcrypto";

-- 1. 사용자 프로필
create table if not exists user_profiles (
  id uuid primary key default gen_random_uuid(),
  user_id uuid unique,
  email text unique,
  nickname text,
  plan text default 'free', -- free, pro, business
  role text default 'user', -- user, admin
  preferred_categories text[] default array['economy', 'stock'],
  content_goal text default 'revenue', -- approval, revenue, cardnews, news
  writing_tone text default 'friendly',
  publish_channel text default 'wordpress', -- wordpress, telegram, manual, both
  daily_idea_count int default 3,
  site_memo text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- 2. 사용자 사이트 정보
create table if not exists user_sites (
  id uuid primary key default gen_random_uuid(),
  user_id uuid,
  site_name text not null,
  site_url text,
  site_type text default 'wordpress',
  site_description text,
  contact_email text,
  wp_status text default 'not_connected',
  telegram_status text default 'not_connected',
  is_default boolean default false,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- 3. 자동화 실행 기록
create table if not exists dashboard_runs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid,
  run_type text not null, -- collect, full_pipeline, article, publish, sns, economic_calendar
  category_filter text default 'all',
  lookback_hours int default 24,
  status text default 'pending', -- pending, running, success, partial_success, failed
  summary jsonb default '{}'::jsonb,
  error_message text,
  raw_log text,
  started_at timestamptz default now(),
  finished_at timestamptz
);

-- 4. 트렌드 키워드
create table if not exists trend_keywords (
  id uuid primary key default gen_random_uuid(),
  run_id uuid references dashboard_runs(id) on delete set null,
  user_id uuid,
  keyword text not null,
  category text default 'other',
  source text,
  approx_traffic int default 0,
  naver_news_count int default 0,
  datalab_score numeric default 0,
  interest_score numeric default 0,
  evidence_count int default 0,
  adsense_safety text default 'safe', -- safe, caution, risky, official_check
  commerce_score numeric default 0,
  content_score numeric default 0,
  status text default 'candidate', -- candidate, selected, excluded, converted
  created_at timestamptz default now()
);

create index if not exists idx_trend_keywords_user_created on trend_keywords(user_id, created_at desc);
create index if not exists idx_trend_keywords_category on trend_keywords(category);
create index if not exists idx_trend_keywords_keyword on trend_keywords(keyword);

-- 5. 뉴스 근거자료
create table if not exists news_evidence (
  id uuid primary key default gen_random_uuid(),
  keyword_id uuid references trend_keywords(id) on delete cascade,
  title text not null,
  source_name text,
  source_type text default 'media', -- official, major_media, niche_media, blog, community, unknown
  url text,
  published_at timestamptz,
  reliability_score numeric default 50,
  link_status text default 'unknown', -- unknown, ok, broken, blocked
  usage_note text,
  summary text,
  created_at timestamptz default now()
);

-- 6. SNS/플랫폼 트렌드
create table if not exists sns_trends (
  id uuid primary key default gen_random_uuid(),
  run_id uuid references dashboard_runs(id) on delete set null,
  user_id uuid,
  platform text not null, -- google, youtube, x, tiktok, instagram, naver, community
  keyword text not null,
  hashtag text,
  category text default 'other',
  rank int,
  trend_score numeric default 0,
  spread_signal text default 'normal', -- normal, rising, hot
  content_usage text default 'article', -- article, cardnews, shorts, commerce, exclude
  commerce_score numeric default 0,
  adsense_safety text default 'safe',
  source_url text,
  raw_payload jsonb default '{}'::jsonb,
  collected_at timestamptz default now()
);

create index if not exists idx_sns_trends_user_collected on sns_trends(user_id, collected_at desc);
create index if not exists idx_sns_trends_platform on sns_trends(platform);
create index if not exists idx_sns_trends_keyword on sns_trends(keyword);

-- 7. 경제지표 캘린더
create table if not exists economic_events (
  id uuid primary key default gen_random_uuid(),
  user_id uuid,
  event_date date not null,
  event_time time,
  timezone text default 'Asia/Seoul',
  country text,
  currency text,
  event_name text not null,
  event_type text default 'macro', -- inflation, employment, rate, growth, housing, manufacturing, sentiment, macro
  importance text default 'medium', -- low, medium, high, critical
  previous_value text,
  forecast_value text,
  actual_value text,
  content_usage text default 'watch', -- watch, article, cardnews, telegram, followup
  status text default 'scheduled', -- scheduled, released, followup_needed, done
  source text default 'manual',
  source_url text,
  note text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create index if not exists idx_economic_events_date on economic_events(event_date);
create index if not exists idx_economic_events_importance on economic_events(importance);

-- 8. 콘텐츠 아이디어
create table if not exists content_ideas (
  id uuid primary key default gen_random_uuid(),
  user_id uuid,
  keyword_id uuid references trend_keywords(id) on delete set null,
  sns_trend_id uuid references sns_trends(id) on delete set null,
  economic_event_id uuid references economic_events(id) on delete set null,
  idea_type text not null, -- article, cardnews, shorts, commerce
  title text,
  hook_point text,
  writing_angle text,
  meta_description text,
  tags text[] default '{}',
  category text,
  priority int default 0,
  status text default 'candidate', -- candidate, draft_created, review_needed, scheduled, published, excluded
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- 9. 생성된 글 초안
create table if not exists generated_articles (
  id uuid primary key default gen_random_uuid(),
  user_id uuid,
  idea_id uuid references content_ideas(id) on delete set null,
  title text,
  slug text,
  meta_description text,
  category text,
  tags text[] default '{}',
  html text,
  faq jsonb default '[]'::jsonb,
  review_checklist jsonb default '[]'::jsonb,
  seo_score numeric default 0,
  adsense_safety text default 'safe',
  wp_post_id text,
  wp_status text,
  status text default 'review_needed',
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- 10. 카드뉴스 초안
create table if not exists cardnews_drafts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid,
  idea_id uuid references content_ideas(id) on delete set null,
  title text,
  thumbnail_copy text,
  tone text default 'informative',
  cards jsonb default '[]'::jsonb,
  image_prompt text,
  status text default 'draft',
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- 11. 제목/썸네일 A/B 후보
create table if not exists ab_candidates (
  id uuid primary key default gen_random_uuid(),
  user_id uuid,
  idea_id uuid references content_ideas(id) on delete cascade,
  candidate_type text not null, -- title, meta, thumbnail, hook
  variant_label text, -- A, B, C
  text_value text not null,
  click_score numeric default 0,
  seo_score numeric default 0,
  safety_score numeric default 0,
  selected boolean default false,
  created_at timestamptz default now()
);

-- 12. 발행/전송 이력
create table if not exists publish_logs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid,
  article_id uuid references generated_articles(id) on delete set null,
  target text not null, -- wordpress, telegram, manual
  target_site_id uuid references user_sites(id) on delete set null,
  status text default 'pending',
  scheduled_at timestamptz,
  published_at timestamptz,
  external_id text,
  external_url text,
  error_message text,
  created_at timestamptz default now()
);

-- 13. 콘텐츠 캘린더
create table if not exists content_calendar (
  id uuid primary key default gen_random_uuid(),
  user_id uuid,
  idea_id uuid references content_ideas(id) on delete set null,
  article_id uuid references generated_articles(id) on delete set null,
  cardnews_id uuid references cardnews_drafts(id) on delete set null,
  title text not null,
  calendar_type text default 'publish', -- draft, review, publish, cardnews, telegram, economic_event
  scheduled_at timestamptz not null,
  status text default 'scheduled',
  category text,
  note text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- 14. 문의/지원
create table if not exists support_tickets (
  id uuid primary key default gen_random_uuid(),
  user_id uuid,
  email text,
  ticket_type text,
  title text,
  message text,
  status text default 'open', -- open, in_progress, resolved, closed
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- 15. 회원 사용량
create table if not exists usage_limits (
  id uuid primary key default gen_random_uuid(),
  user_id uuid,
  plan text default 'free',
  usage_date date default current_date,
  article_generations int default 0,
  cardnews_generations int default 0,
  sns_collections int default 0,
  wp_publishes int default 0,
  telegram_sends int default 0,
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  unique(user_id, usage_date)
);

-- Row Level Security 권장
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

-- 실제 Supabase Auth 연결 시 auth.uid() 기반 정책 추가 필요
-- 예:
-- create policy "Users can read own profile" on user_profiles
-- for select using (auth.uid() = user_id);
