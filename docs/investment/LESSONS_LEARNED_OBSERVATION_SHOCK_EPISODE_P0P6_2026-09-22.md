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

## 9. Next action
Wire the existing market-monitor collector to Observation Schema v3.0, build the historical PIT panel, freeze episode rules, then run P0→P6 across development/validation/OOS and walk-forward splits.
