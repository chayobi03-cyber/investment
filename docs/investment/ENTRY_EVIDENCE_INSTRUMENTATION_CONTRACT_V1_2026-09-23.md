# Entry Evidence Instrumentation Contract v1

Date: 2026-09-23
Status: RESEARCH DATA ACQUISITION — NOT OPERATIONAL

## Purpose
Secure PIT-safe evidence for:
Opening Gap -> Foreign Flow -> Intraday Hold -> Forward Outcome

## Canonical components
- previous_close + first_regular_session_bar
- opening_gap_derived
- foreign_flow_estimate (KIS HHPTJ04160200)
- foreign_flow_daily_confirmed (KIS FHKST01010900; after-close only)
- intraday_1m (KIS FHKST03010230)
- forward 5D/20D/60D + MAE/drawdown

## Source facts
KIS documents the investor-trend estimate endpoint /uapi/domestic-stock/v1/quotations/investor-trend-estimate, TR HHPTJ04160200, with dealer-entered cumulative estimate checkpoints around 09:30, 11:20, 13:20 and 14:30. Timing can vary by roughly +/-10 minutes; this remains ESTIMATED evidence.
KIS documents /uapi/domestic-stock/v1/quotations/inquire-investor, TR FHKST01010900, for investor history; the official example notes that same-day data is supplied after the session close.
KIS documents /uapi/domestic-stock/v1/quotations/inquire-time-dailychartprice, TR FHKST03010230, for historical intraday bars; the official example states up to 120 rows per production call and historical dates within the provider's retained range, up to one year.

## PIT rules
- available_at = collector capture/persistence time.
- observed_at = source bar time when explicit; otherwise collector capture with explicit timestamp_semantics.
- Provider event fields remain in raw_payload.
- A decision at time T may use only records with available_at <= T.
- Final daily investor flow is forbidden as evidence for a pre-close decision.

## Gap definition
gap_pct = (session_open / previous_close - 1) * 100
The first regular-session minute bar is canonical. Missing inputs => DATA_NOT_READY.

## Intraday hold
Collector stores raw 1-minute OHLCV. It does not choose a hold threshold. The backtest must preregister the exact confirmation window and rule.

## Quality
GREEN = captured + PIT timestamp valid + hash
AMBER = explicit estimate/proxy or collector-derived timestamp
RED = invalid/missing required source evidence
DATA_NOT_READY = defining component absent for the requested decision

## Required artifact
observations.jsonl
raw source payloads
manifest.json
SHA-256 per artifact
source/TR IDs
symbols and requested date
counts/failures/acquisition time

## Promotion gate
No rule promotion until all defining components exist in PIT-safe history and the incremental chain
price-only -> +gap -> +foreign-flow -> +intraday-hold
survives development/validation/OOS, walk-forward, falsification and sensitivity.

## Blocker
Real capture requires KIS_APP_KEY and KIS_APP_SECRET. The collector must fail closed when credentials are absent.
