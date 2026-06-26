-- v1.8 economic_events 중복 정리 SQL
-- 기준: 같은 event_date + country + currency + event_name이면 중복으로 간주
-- 남길 데이터 우선순위:
-- 1) importance가 높은 데이터
-- 2) actual_value가 있는 데이터
-- 3) forecast/previous 값이 있는 데이터
-- 4) updated_at/created_at이 최신인 데이터

-- 1. 중복 후보 확인
select
  event_date,
  country,
  currency,
  lower(regexp_replace(coalesce(event_name, ''), '\s+', '', 'g')) as normalized_event_name,
  count(*) as duplicate_count
from economic_events
group by event_date, country, currency, lower(regexp_replace(coalesce(event_name, ''), '\s+', '', 'g'))
having count(*) > 1
order by duplicate_count desc, event_date desc;

-- 2. 중복 삭제
with ranked as (
  select
    id,
    row_number() over (
      partition by
        event_date,
        coalesce(country, ''),
        coalesce(currency, ''),
        lower(regexp_replace(coalesce(event_name, ''), '\s+', '', 'g'))
      order by
        case importance
          when 'critical' then 4
          when 'high' then 3
          when 'medium' then 2
          when 'low' then 1
          else 0
        end desc,
        case when actual_value is not null and actual_value <> '' then 1 else 0 end desc,
        case when forecast_value is not null and forecast_value <> '' then 1 else 0 end desc,
        case when previous_value is not null and previous_value <> '' then 1 else 0 end desc,
        coalesce(updated_at, created_at) desc nulls last,
        created_at desc nulls last
    ) as rn
  from economic_events
)
delete from economic_events
where id in (
  select id from ranked where rn > 1
);

-- 3. 중복 방지용 unique index
-- 같은 날짜/국가/통화/지표명은 1개만 등록되도록 제한
create unique index if not exists economic_events_unique_daily_event_v18
on economic_events (
  event_date,
  coalesce(country, ''),
  coalesce(currency, ''),
  lower(regexp_replace(coalesce(event_name, ''), '\s+', '', 'g'))
);

-- 4. 확인
select
  event_date,
  country,
  currency,
  event_name,
  importance,
  previous_value,
  forecast_value,
  actual_value,
  content_usage,
  status
from economic_events
order by event_date asc, event_time asc;
