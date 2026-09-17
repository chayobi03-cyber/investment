-- Preconditions
-- 1) Deploy function: collect-market-observations
-- 2) Enable pg_cron and pg_net
-- 3) Store these Vault secrets on the INVESTMENT Supabase project:
--      market_collector_secret
--      supabase_publishable_key
-- 4) Configure Edge Function secrets:
--      KIS_APP_KEY
--      KIS_APP_SECRET
--      MARKET_COLLECTOR_SECRET  (same value as Vault market_collector_secret)
--      KIS_SYMBOLS (optional comma-separated override)
--      SUPABASE_SERVICE_ROLE_KEY is supported for compatibility; prefer current
--      SUPABASE_SECRET_KEYS if the deployment surface provides it.
--
-- Database remains UTC. Collection window starts at 08:30 KST (23:30 UTC)
-- to preserve the existing pre-open checkpoint, then continues through
-- Korea regular session close at 15:35 KST (06:35 UTC), Mon-Fri.

select cron.unschedule(jobid)
from cron.job
where jobname in (
  'investment-market-collector-v1',
  'investment-market-collector-v1-close',
  'investment-market-collector-v1-preopen'
);

select cron.schedule(
  'investment-market-collector-v1-preopen',
  '30-59 23 * * 1-5',
  $$
    select net.http_post(
      url := current_setting('app.settings.market_collector_url', true),
      headers := jsonb_build_object(
        'Content-Type', 'application/json',
        'apikey', (select decrypted_secret from vault.decrypted_secrets where name = 'supabase_publishable_key'),
        'x-market-collector-secret', (select decrypted_secret from vault.decrypted_secrets where name = 'market_collector_secret')
      ),
      body := jsonb_build_object('scheduled_at', now()),
      timeout_milliseconds := 10000
    ) as request_id;
  $$
);

select cron.schedule(
  'investment-market-collector-v1',
  '* 0-5 * * 1-5',
  $$
    select net.http_post(
      url := current_setting('app.settings.market_collector_url', true),
      headers := jsonb_build_object(
        'Content-Type', 'application/json',
        'apikey', (select decrypted_secret from vault.decrypted_secrets where name = 'supabase_publishable_key'),
        'x-market-collector-secret', (select decrypted_secret from vault.decrypted_secrets where name = 'market_collector_secret')
      ),
      body := jsonb_build_object('scheduled_at', now()),
      timeout_milliseconds := 10000
    ) as request_id;
  $$
);

select cron.schedule(
  'investment-market-collector-v1-close',
  '0-35 6 * * 1-5',
  $$
    select net.http_post(
      url := current_setting('app.settings.market_collector_url', true),
      headers := jsonb_build_object(
        'Content-Type', 'application/json',
        'apikey', (select decrypted_secret from vault.decrypted_secrets where name = 'supabase_publishable_key'),
        'x-market-collector-secret', (select decrypted_secret from vault.decrypted_secrets where name = 'market_collector_secret')
      ),
      body := jsonb_build_object('scheduled_at', now()),
      timeout_milliseconds := 10000
    ) as request_id;
  $$
);
