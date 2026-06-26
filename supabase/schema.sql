create extension if not exists "pgcrypto";

create table if not exists user_profiles (
  id uuid primary key default gen_random_uuid(),
  user_id uuid unique,
  email text unique,
  nickname text,
  plan text default 'free',
  role text default 'user',
  preferred_categories text[] default array['economy', 'stock'],
  content_goal text default 'revenue',
  writing_tone text default 'friendly',
  publish_channel text default 'wordpress',
  daily_idea_count int default 3,
  site_memo text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

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

create table if not exists dashboard_runs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid,
  run_type text not null,
  category_filter text default 'all',
  lookback_hours int default 24,
  status text default 'pending',
  summary jsonb default '{}'::jsonb,
  error_message text,
  raw_log text,
  started_at timestamptz default now(),
  finished_at timestamptz
);

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
  adsense_safety text default 'safe',
  commerce_score numeric default 0,
  content_score numeric default 0,
  status text default 'candidate',
  created_at timestamptz default now()
);

create index if not exists idx_trend_keywords_user_created on trend_keywords(user_id, created_at desc);
create index if not exists idx_trend_keywords_category on trend_keywords(category);
create index if not exists idx_trend_keywords_keyword on trend_keywords(keyword);

create table if not exists news_evidence (
  id uuid primary key default gen_random_uuid(),
  keyword_id uuid references trend_keywords(id) on delete cascade,
  title text not null,
  source_name text,
  source_type text default 'media',
  url text,
  published_at timestamptz,
  reliability_score numeric default 50,
  link_status text default 'unknown',
  usage_note text,
  summary text,
  created_at timestamptz default now()
);

create table if not exists sns_trends (
  id uuid primary key default gen_random_uuid(),
  run_id uuid references dashboard_runs(id) on delete set null,
  user_id uuid,
  platform text not null,
  keyword text not null,
  hashtag text,
  category text default 'other',
  rank int,
  trend_score numeric default 0,
  spread_signal text default 'normal',
  content_usage text default 'article',
  commerce_score numeric default 0,
  adsense_safety text default 'safe',
  source_url text,
  raw_payload jsonb default '{}'::jsonb,
  collected_at timestamptz default now()
);

create index if not exists idx_sns_trends_user_collected on sns_trends(user_id, collected_at desc);
create index if not exists idx_sns_trends_platform on sns_trends(platform);
create index if not exists idx_sns_trends_keyword on sns_trends(keyword);

create table if not exists economic_events (
  id uuid primary key default gen_random_uuid(),
  user_id uuid,
  event_date date not null,
  event_time time,
  timezone text default 'Asia/Seoul',
  country text,
  currency text,
  event_name text not null,
  event_type text default 'macro',
  importance text default 'medium',
  previous_value text,
  forecast_value text,
  actual_value text,
  content_usage text default 'watch',
  status text default 'scheduled',
  source text default 'manual',
  source_url text,
  note text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create index if not exists idx_economic_events_date on economic_events(event_date);
create index if not exists idx_economic_events_importance on economic_events(importance);

create table if not exists content_ideas (
  id uuid primary key default gen_random_uuid(),
  user_id uuid,
  keyword_id uuid references trend_keywords(id) on delete set null,
  sns_trend_id uuid references sns_trends(id) on delete set null,
  economic_event_id uuid references economic_events(id) on delete set null,
  idea_type text not null,
  title text,
  hook_point text,
  writing_angle text,
  meta_description text,
  tags text[] default '{}',
  category text,
  priority int default 0,
  status text default 'candidate',
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

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

create table if not exists ab_candidates (
  id uuid primary key default gen_random_uuid(),
  user_id uuid,
  idea_id uuid references content_ideas(id) on delete cascade,
  candidate_type text not null,
  variant_label text,
  text_value text not null,
  click_score numeric default 0,
  seo_score numeric default 0,
  safety_score numeric default 0,
  selected boolean default false,
  created_at timestamptz default now()
);

create table if not exists publish_logs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid,
  article_id uuid references generated_articles(id) on delete set null,
  target text not null,
  target_site_id uuid references user_sites(id) on delete set null,
  status text default 'pending',
  scheduled_at timestamptz,
  published_at timestamptz,
  external_id text,
  external_url text,
  error_message text,
  created_at timestamptz default now()
);

create table if not exists content_calendar (
  id uuid primary key default gen_random_uuid(),
  user_id uuid,
  idea_id uuid references content_ideas(id) on delete set null,
  article_id uuid references generated_articles(id) on delete set null,
  cardnews_id uuid references cardnews_drafts(id) on delete set null,
  title text not null,
  calendar_type text default 'publish',
  scheduled_at timestamptz not null,
  status text default 'scheduled',
  category text,
  note text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table if not exists support_tickets (
  id uuid primary key default gen_random_uuid(),
  user_id uuid,
  email text,
  ticket_type text,
  title text,
  message text,
  status text default 'open',
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

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
