# Lessons Learned — Observation → Shock → Episode → P0~P6
Date: 2026-09-22

## 1. Core lesson
Entry-timing research must begin with an auditable Observation contract, not a buy signal. The fixed sequence is:
Observation Schema → signed shock → freshness → relative strength/breadth → attribution → episode engine → P0~P6 backtest.

## 2. Data lessons
- observed_at and available_at must remain separate to preserve PIT correctness.
- source and revision_status are mandatory provenance fields.
- Missing information stays null/UNKNOWN; it must not be imputed into a positive signal.
- STALE is fail-closed. Fresh data from another series cannot mask a stale required input.

## 3. Shock lessons
- Raw movement and stress-signed movement must both be retained.
- Stress polarity is series-specific research metadata and remains a hypothesis until validated.
- Macro/cross-asset variables must be represented as directional stress information, not merely absolute price changes.

## 4. Market-structure lessons
- Relative strength is benchmark-relative, not raw return.
- Breadth must distinguish true-universe breadth from watchlist proxy breadth.
- Leadership should not be inferred from a small basket and then presented as market breadth.

## 5. Attribution lessons
- Price movement alone is insufficient for causal attribution.
- Direct evidence can support VERIFIED; corroborating sector evidence + RS can support CORROBORATED; synchronized macro evidence can support INFERRED.
- Insufficient evidence remains UNRESOLVED/UNKNOWN.

## 6. Episode lessons
- Backtesting individual observations can overcount one shock many times.
- Episode clustering plus re-arm/cooldown is required before measuring trigger frequency, hit rate, MAE, rebound time, or return.
- Episode boundaries are part of the model and must be frozen before OOS evaluation.

## 7. P0~P6 lessons
- P0 is the price-only baseline.
- Each higher level must add information without changing the underlying observation universe or outcome definition.
- Report incremental lift, not only period-end return.
- Evaluate development, validation, OOS and walk-forward; do not promote a threshold because it works in one split.
- Forward outcome horizons should include at least 5D/20D/60D and downside/MAE metrics.

## 8. Guardrail
Until PIT history, forward outcomes, episode labels and required evidence are complete, the backtest status is DATA_NOT_READY. No live MarketScore/BuyStrength change follows from this research branch.

## 9. Execution lessons from 2026-09-22
- The existing Market Monitor can transport Observation Schema v3.0 without pretending that a 5-minute payload contains daily features.
- Live 5-minute change must remain separate from d1/d5/d20 daily features; missing daily features stay NULL and quality remains AMBER.
- The historical pipeline can execute end-to-end on vendor history, but `VENDOR_HISTORY_PROXY` is not equivalent to strict archival PIT.
- Adjusted historical OHLC can embed future corporate-action/dividend information. It must not be silently labeled as strict PIT evidence.
- P0→P5 can be measured with forward next-session-open outcomes while P6 remains fail-closed until PIT fundamentals are connected.
- P1 produced the same episode set as P0 in this run, so the current P1 condition is not discriminating on this dataset.
- P5 has only 20 OOS episodes and its validation result differs materially from OOS; both are reasons to treat the observed OOS lift as provisional.
- A metric named `false_positive_rate` must have a separately defined classification target. A complement of positive 20D return is not automatically a classification false-positive rate.

## 10. Current state
The end-to-end research path is now executable:
Market Monitor → Observation v3.0 → historical vendor-history proxy → episode clustering → P0→P5 outcomes → walk-forward diagnostics.

P6 remains DATA_NOT_READY. Strict PIT remains NOT_GREEN. No live MarketScore/BuyStrength rule has been changed.

## 11. Next action
1. Replace the vendor-history proxy with strict PIT/as-published or action-aware historical vintages.
2. Connect archival PIT fundamentals and complete P6.
3. Add costs/slippage/execution constraints and formal falsification/sensitivity tests.
4. Correct the `false_positive_rate` semantics before the next research release.
5. Rerun P0→P6 and freeze the evidence artifact before any rule revision.

## 12. PIT hardening after the first backtest
- Raw vendor OHLC must be preserved without adjusted-price factors. This removes a known corporate-action leakage path but does not create archival revision history.
- Strict PIT is now an explicit manifest contract: archival revisions, vintage policy, source version, and immutable artifact hash are mandatory.
- `VENDOR_HISTORY_PROXY` remains a valid research transport state, but it can never satisfy the strict PIT gate.
- `false_positive_rate` is a classification metric, not the complement of forward-return positive rate. Without explicit prediction and realized labels over a defined target universe, classification status is DATA_NOT_READY.

## 13. Next PIT acquisition layer
- OpenDART disclosure search must use `last_reprt_at=N` so correction filings are not silently excluded.
- Filing-level identity is `rcept_no`; the capture layer stores `rcept_dt`, raw artifact bytes, and SHA-256.
- P6 must consume the filing-time capture/lineage rather than a later "latest financials" endpoint result.
- Missing OpenDART credentials or missing filing artifacts are DATA_NOT_READY, never an imputed fundamental state.


## 14. Opening-gap / flow / intraday validation — 2026-09-23
- The proposed `Opening Gap → Foreign Net Flow → Intraday Hold` rule cannot be validated from the current P0~P6 historical artifact because foreign-flow and intraday-bar fields are absent.
- The current artifact contains daily OHLC only. `entry_open` permits an opening-gap calculation, while `entry_day_close >= entry_day_open` is only a coarse daily proxy and must not be labeled intraday hold.
- Descriptive gap stratification showed unstable results as the gap cutoff increased; small validation/OOS samples make post-hoc cutoff selection especially unsafe.
- A defining rule component that is absent from the historical evidence layer is a hard DATA_NOT_READY condition, not a reason to substitute a proxy silently.
- Future validation must compare price-only → +opening gap → +foreign flow → +intraday hold with frozen definitions across development, validation, OOS and walk-forward, using 5D/20D/60D returns plus MAE/drawdown and explicit FP/FN labels.
- No live MarketScore/BuyStrength change follows from this study.

## 15. Governance rule added
**A research rule is not eligible for promotion unless every defining component has PIT-safe historical evidence and the incremental component contribution survives OOS/walk-forward falsification.**
