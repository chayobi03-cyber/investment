create table if not exists public.market_observations (
  id uuid primary key default gen_random_uuid(),
  run_id uuid not null,
  source_id text not null,
  source_version text not null,
  feed text not null,
  instrument_type text not null,
  symbol text not null,
  market_session text not null,
  observed_at timestamptz not null,
  available_at timestamptz not null,
  raw_value numeric,
  price numeric,
  change_pct numeric,
  volume numeric,
  turnover numeric,
  open_price numeric,
  high_price numeric,
  low_price numeric,
  vwap numeric,
  bid1 numeric,
  ask1 numeric,
  revision_status text not null default 'initial',
  rule_version text not null,
  raw_payload jsonb not null,
  created_at timestamptz not null default now(),
  constraint market_observations_timing_chk check (available_at >= observed_at),
  constraint market_observations_identity_uq unique (source_id, feed, symbol, observed_at, rule_version)
);

create index if not exists market_observations_lookup_idx
  on public.market_observations (symbol, observed_at desc);

create index if not exists market_observations_decision_idx
  on public.market_observations (available_at desc, symbol);

alter table public.market_observations enable row level security;

revoke all on table public.market_observations from anon, authenticated;
