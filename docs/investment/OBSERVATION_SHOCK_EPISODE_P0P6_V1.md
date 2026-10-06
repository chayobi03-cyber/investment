# Observation → Signed Shock → Freshness → RS/Breadth → Attribution → Episode → P0~P6 v1

Date: 2026-09-22  
Status: RESEARCH IMPLEMENTATION — NOT OPERATIONAL

## Pipeline contract
`Observation Schema → signed shock → freshness → relative strength/breadth → attribution → episode engine → P0~P6 backtest`

### Observation Schema v3.0
Every observation stores `observed_at`, `available_at`, `source`, `revision_status`, historical returns (1/3/5/20/60/120/252D), MA distances/slopes, drawdowns, consecutive sessions, structure fields, quality state, and evidence-first attribution. Missing fields remain null/unknown.

### Signed shock
Store both raw move and stress-signed move. The sign is controlled by a series-specific research polarity. Positive signed shock means stress-increasing. Polarity is an explicit hypothesis, not a promoted rule.

### Freshness
Freshness is evaluated per series. `FRESH`, `LATE_AVAILABLE`, and `STALE` are separate. Stale inputs are fail-closed; a fresh series cannot mask a stale one.

### Relative strength / breadth
RS is `asset_return - benchmark_return`. Breadth carries `true_universe` or `watchlist_proxy` source type. The existing leader basket remains proxy breadth until a full-universe provider is available.

### Attribution
For a material move, direct evidence can yield `VERIFIED`; multi-source sector evidence plus RS can yield `CORROBORATED`; synchronized macro shock can yield `INFERRED`; otherwise `UNRESOLVED / UNKNOWN`. Causality is never manufactured from price alone.

### Episode engine
Observations are clustered by `(cluster, asset_id)`. A stress trigger starts an episode; recovery below re-arm closes it; cooldown prevents repeated counting of the same shock.

### P0~P6
| Level | Added information |
|---|---|
| P0 | price-only |
| P1 | + price location |
| P2 | + extension/chase |
| P3 | + RS / breadth / leadership |
| P4 | + signed macro / cross-asset |
| P5 | + attribution evidence |
| P6 | + fundamentals |

Report 5/20/60D forward return, positive rate, median, worst return, MAE, post-entry drawdown, false-positive/miss metrics, trigger frequency, time-to-rebound, and incremental lift. Use development/validation/OOS and walk-forward evaluation.

## Fail-closed / promotion
The harness returns `DATA_NOT_READY` until the PIT history and forward outcomes are complete. No threshold fitting or live BuyStrength/MarketScore changes are included here.

Promotion remains `RESEARCH → VALIDATED → SHADOW → OPERATIONAL` only after PIT reproducibility, episode deduplication, data QA, OOS consistency, and walk-forward robustness are demonstrated.
