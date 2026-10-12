-- PROPOSAL ONLY: not yet applied to any database.
-- Intended for a dedicated PostgreSQL investment database.
-- Keep this schema out of the browser-facing Data API. Configure service-side privileges
-- and verify RLS/security advisors in an isolated development environment before use.
-- All records are designed for insert-only history; corrections use new versions/records.

create schema if not exists investment_learning;

create table investment_learning.il_rule_versions (
    rule_version_id uuid primary key default gen_random_uuid(),
    rule_set_name text not null,
    version_label text not null,
    parent_rule_version_id uuid references investment_learning.il_rule_versions(rule_version_id) on delete restrict,
    content_sha256 text not null unique check (content_sha256 ~ '^[0-9a-f]{64}$'),
    payload jsonb not null check (jsonb_typeof(payload) = 'object' and octet_length(payload::text) <= 200000),
    diff_payload jsonb not null default '{}'::jsonb check (jsonb_typeof(diff_payload) = 'object'),
    rationale text not null,
    created_by text not null,
    created_at timestamptz not null default now()
);

create table investment_learning.il_market_runs (
    run_id uuid primary key default gen_random_uuid(),
    idempotency_key text not null unique,
    analysis_asof timestamptz not null,
    session_date date not null,
    session text not null check (session in ('KOREA', 'US', 'OVERLAP', 'GLOBAL_TRANSITION')),
    run_kind text not null check (run_kind in ('INTRADAY_MONITOR', 'PREOPEN_ANALYSIS', 'EOD_ANALYSIS', 'MANUAL_ANALYSIS', 'BACKFILL')),
    run_status text not null check (run_status in ('COMPLETED', 'DATA_NOT_READY', 'BLOCKED', 'FAILED')),
    quality_status text not null check (quality_status in ('GREEN', 'AMBER', 'RED', 'N_A')),
    code_sha text not null,
    config_version text not null,
    prompt_version text not null,
    calculation_version text not null,
    rule_version_id uuid references investment_learning.il_rule_versions(rule_version_id) on delete restrict,
    input_sha256 text not null check (input_sha256 ~ '^[0-9a-f]{64}$'),
    result_payload jsonb not null check (jsonb_typeof(result_payload) = 'object' and octet_length(result_payload::text) <= 500000),
    artifact_uri text,
    created_at timestamptz not null default now()
);

create table investment_learning.il_evidence_observations (
    evidence_id uuid primary key default gen_random_uuid(),
    source_id text not null,
    series_id text not null,
    domain text not null,
    observed_at timestamptz not null,
    published_at timestamptz,
    available_at timestamptz not null,
    unit text,
    numeric_value numeric,
    text_value text,
    quality_status text not null check (quality_status in ('VALID', 'STALE', 'MISSING', 'REJECTED', 'REVISED')),
    freshness_status text not null check (freshness_status in ('FRESH_ACTIVE_SESSION', 'VALID_CLOSED_SESSION', 'STALE', 'MISSING', 'UNKNOWN')),
    revision_key text not null default 'original',
    content_sha256 text not null check (content_sha256 ~ '^[0-9a-f]{64}$'),
    source_uri text,
    failure_code text,
    metadata jsonb not null default '{}'::jsonb check (jsonb_typeof(metadata) = 'object'),
    ingested_at timestamptz not null default now(),
    unique (source_id, series_id, observed_at, revision_key, content_sha256)
);

create table investment_learning.il_run_evidence (
    run_id uuid not null references investment_learning.il_market_runs(run_id) on delete restrict,
    evidence_id uuid not null references investment_learning.il_evidence_observations(evidence_id) on delete restrict,
    evidence_role text not null,
    required_for_decision boolean not null default false,
    primary key (run_id, evidence_id, evidence_role)
);

create table investment_learning.il_dimension_scores (
    run_id uuid not null references investment_learning.il_market_runs(run_id) on delete restrict,
    dimension_key text not null,
    score numeric check (score is null or (score >= 0 and score <= 100)),
    state text not null check (state in ('GREEN', 'AMBER', 'RED', 'N_A', 'DATA_NOT_READY', 'BLOCKED')),
    confidence numeric check (confidence is null or (confidence >= 0 and confidence <= 1)),
    sample_count integer not null default 0 check (sample_count >= 0),
    calculation_version text not null,
    component_payload jsonb not null default '{}'::jsonb check (
        jsonb_typeof(component_payload) = 'object' and octet_length(component_payload::text) <= 100000
    ),
    primary key (run_id, dimension_key)
);

create table investment_learning.il_forecasts (
    forecast_id uuid primary key default gen_random_uuid(),
    run_id uuid not null references investment_learning.il_market_runs(run_id) on delete restrict,
    forecast_type text not null,
    subject_type text not null check (subject_type in ('MARKET', 'INDEX', 'SECTOR', 'STOCK', 'ETF', 'CRYPTO', 'FX', 'COMMODITY', 'PORTFOLIO')),
    subject_key text not null,
    target_key text not null,
    horizon_value integer not null check (horizon_value > 0),
    horizon_unit text not null check (horizon_unit in ('INTRADAY_MINUTES', 'TRADING_SESSIONS', 'CALENDAR_DAYS')),
    forecast_direction text not null check (forecast_direction in ('UP', 'DOWN', 'NEUTRAL', 'EVENT', 'DISTRIBUTION')),
    probability_up numeric check (probability_up is null or (probability_up >= 0 and probability_up <= 1)),
    probability_down numeric check (probability_down is null or (probability_down >= 0 and probability_down <= 1)),
    probability_event numeric check (probability_event is null or (probability_event >= 0 and probability_event <= 1)),
    expected_return_pct numeric,
    downside_q05_pct numeric,
    confidence numeric check (confidence is null or (confidence >= 0 and confidence <= 1)),
    permission_state text not null check (permission_state in ('DATA_NOT_READY', 'BLOCKED', 'RESEARCH_ONLY', 'SHADOW')),
    buy_allowed boolean not null default false check (buy_allowed = false),
    execution_allowed boolean not null default false check (execution_allowed = false),
    model_version text not null,
    rule_version_id uuid references investment_learning.il_rule_versions(rule_version_id) on delete restrict,
    target_payload jsonb not null default '{}'::jsonb check (jsonb_typeof(target_payload) = 'object'),
    created_at timestamptz not null default now(),
    unique (run_id, forecast_type, subject_type, subject_key, target_key, horizon_value, horizon_unit, model_version)
);

create table investment_learning.il_forecast_outcomes (
    outcome_id uuid primary key default gen_random_uuid(),
    forecast_id uuid not null references investment_learning.il_forecasts(forecast_id) on delete restrict,
    calculation_version text not null,
    outcome_status text not null check (outcome_status in ('COMPLETE', 'INSUFFICIENT_DATA', 'INVALIDATED')),
    evaluated_at timestamptz not null,
    reference_at timestamptz,
    reference_value numeric,
    endpoint_at timestamptz,
    endpoint_value numeric,
    realized_return_pct numeric,
    benchmark_return_pct numeric,
    max_adverse_excursion_pct numeric,
    max_favorable_excursion_pct numeric,
    target_hit boolean,
    result_payload jsonb not null default '{}'::jsonb check (jsonb_typeof(result_payload) = 'object'),
    evidence_ids uuid[] not null default '{}'::uuid[],
    source_manifest_sha256 text check (source_manifest_sha256 is null or source_manifest_sha256 ~ '^[0-9a-f]{64}$'),
    failure_code text,
    created_at timestamptz not null default now(),
    unique (forecast_id, calculation_version),
    check (outcome_status <> 'COMPLETE' or (reference_at is not null and endpoint_at is not null and realized_return_pct is not null))
);

create table investment_learning.il_diagnoses (
    diagnosis_id uuid primary key default gen_random_uuid(),
    run_id uuid references investment_learning.il_market_runs(run_id) on delete restrict,
    forecast_id uuid references investment_learning.il_forecasts(forecast_id) on delete restrict,
    outcome_id uuid references investment_learning.il_forecast_outcomes(outcome_id) on delete restrict,
    supersedes_diagnosis_id uuid references investment_learning.il_diagnoses(diagnosis_id) on delete restrict,
    primary_cause_code text not null check (primary_cause_code in (
        'DATA_MISSING_OR_STALE', 'PIT_OR_REVISION_LEAKAGE', 'SOURCE_OR_ADJUSTMENT_ERROR',
        'FEATURE_OR_NORMALIZATION', 'THRESHOLD_OR_STATE_TRANSITION', 'REGIME_OR_CROSS_ASSET',
        'HORIZON_OR_SETTLEMENT', 'MODEL_OR_CALIBRATION', 'EXECUTION_OR_COST',
        'CONFLICT_OR_REASONING', 'PROCESS_OR_HUMAN_OVERRIDE', 'UNKNOWN_OR_INTERACTION'
    )),
    secondary_causes text[] not null default '{}'::text[],
    conclusion_level text not null check (conclusion_level in ('HYPOTHESIS', 'SUPPORTED', 'CONFIRMED', 'REJECTED', 'UNKNOWN')),
    hypothesis text not null,
    counterfactual text,
    confidence numeric check (confidence is null or (confidence >= 0 and confidence <= 1)),
    evidence_ids uuid[] not null default '{}'::uuid[],
    created_by text not null,
    created_at timestamptz not null default now(),
    check (run_id is not null or forecast_id is not null or outcome_id is not null)
);

create table investment_learning.il_countermeasures (
    countermeasure_id uuid primary key default gen_random_uuid(),
    diagnosis_id uuid not null references investment_learning.il_diagnoses(diagnosis_id) on delete restrict,
    proposed_rule_version_id uuid references investment_learning.il_rule_versions(rule_version_id) on delete restrict,
    proposal_sha256 text not null unique check (proposal_sha256 ~ '^[0-9a-f]{64}$'),
    intervention_type text not null check (intervention_type in (
        'DATA_FIX', 'FEATURE_FIX', 'THRESHOLD_CHANGE', 'MODEL_CHANGE', 'PROCESS_CHANGE', 'MONITORING_CHANGE'
    )),
    hypothesis text not null,
    validation_plan jsonb not null check (jsonb_typeof(validation_plan) = 'object'),
    acceptance_criteria jsonb not null check (jsonb_typeof(acceptance_criteria) = 'object'),
    rollback_criteria jsonb not null check (jsonb_typeof(rollback_criteria) = 'object'),
    expected_tradeoffs jsonb not null default '{}'::jsonb check (jsonb_typeof(expected_tradeoffs) = 'object'),
    created_by text not null,
    expires_at timestamptz,
    created_at timestamptz not null default now()
);

create table investment_learning.il_evaluations (
    evaluation_id uuid primary key default gen_random_uuid(),
    countermeasure_id uuid references investment_learning.il_countermeasures(countermeasure_id) on delete restrict,
    rule_version_id uuid references investment_learning.il_rule_versions(rule_version_id) on delete restrict,
    reference_run_id uuid references investment_learning.il_market_runs(run_id) on delete restrict,
    evaluation_type text not null check (evaluation_type in ('BASELINE', 'IN_SAMPLE', 'VALIDATION', 'OOS', 'WALK_FORWARD', 'SHADOW', 'REGRESSION')),
    dataset_start timestamptz not null,
    dataset_end timestamptz not null,
    sample_count integer not null check (sample_count >= 0),
    verdict text not null check (verdict in ('PASS', 'FAIL', 'NOT_ENOUGH_DATA', 'INCONCLUSIVE')),
    metrics_payload jsonb not null check (jsonb_typeof(metrics_payload) = 'object'),
    guardrail_payload jsonb not null default '{}'::jsonb check (jsonb_typeof(guardrail_payload) = 'object'),
    calculation_version text not null,
    artifact_uri text,
    artifact_sha256 text check (artifact_sha256 is null or artifact_sha256 ~ '^[0-9a-f]{64}$'),
    created_at timestamptz not null default now(),
    check (dataset_end >= dataset_start),
    check (countermeasure_id is not null or rule_version_id is not null)
);

create table investment_learning.il_governance_events (
    governance_event_id uuid primary key default gen_random_uuid(),
    event_type text not null check (event_type in (
        'PROPOSED', 'REJECTED', 'DEFERRED', 'APPROVED_FOR_SHADOW',
        'APPROVED_FOR_RELEASE', 'RULE_ACTIVATED', 'RULE_ROLLED_BACK', 'RULE_RETIRED'
    )),
    actor_type text not null check (actor_type in ('HUMAN', 'SYSTEM', 'AGENT')),
    actor_id text not null,
    subject_type text not null check (subject_type in ('RULE_VERSION', 'COUNTERMEASURE', 'DIAGNOSIS', 'EVALUATION', 'MARKET_RUN')),
    subject_id uuid not null,
    rule_version_id uuid references investment_learning.il_rule_versions(rule_version_id) on delete restrict,
    rationale text not null,
    evidence_ids uuid[] not null default '{}'::uuid[],
    gate_results jsonb not null default '{}'::jsonb check (
        jsonb_typeof(gate_results) = 'object' and octet_length(gate_results::text) <= 100000
    ),
    created_at timestamptz not null default now(),
    check (event_type <> 'RULE_ACTIVATED' or (actor_type = 'HUMAN' and rule_version_id is not null)),
    check (event_type <> 'APPROVED_FOR_RELEASE' or actor_type = 'HUMAN')
);

create index il_market_runs_asof_idx on investment_learning.il_market_runs (analysis_asof desc, session_date desc);
create index il_evidence_series_time_idx on investment_learning.il_evidence_observations (series_id, observed_at desc);
create index il_evidence_availability_idx on investment_learning.il_evidence_observations (available_at);
create index il_forecasts_settlement_idx on investment_learning.il_forecasts (horizon_unit, horizon_value, created_at);
create index il_outcomes_forecast_idx on investment_learning.il_forecast_outcomes (forecast_id, created_at desc);
create index il_diagnoses_cause_idx on investment_learning.il_diagnoses (primary_cause_code, created_at desc);
create index il_evaluations_verdict_idx on investment_learning.il_evaluations (evaluation_type, verdict, created_at desc);
create index il_governance_subject_idx on investment_learning.il_governance_events (subject_type, subject_id, created_at desc);

alter table investment_learning.il_rule_versions enable row level security;
alter table investment_learning.il_market_runs enable row level security;
alter table investment_learning.il_evidence_observations enable row level security;
alter table investment_learning.il_run_evidence enable row level security;
alter table investment_learning.il_dimension_scores enable row level security;
alter table investment_learning.il_forecasts enable row level security;
alter table investment_learning.il_forecast_outcomes enable row level security;
alter table investment_learning.il_diagnoses enable row level security;
alter table investment_learning.il_countermeasures enable row level security;
alter table investment_learning.il_evaluations enable row level security;
alter table investment_learning.il_governance_events enable row level security;

-- Before use, configure service-side INSERT/SELECT permissions only and verify access/security advisors.
-- Do not grant browser/client access. No RLS policies are created by this proposal.
-- Writes must be append-only; corrections create new records. Use conflict-safe insert semantics.
