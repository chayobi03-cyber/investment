# BUY Trigger Engine V0.1 — Market Vector & Gate Contract

Date: 2026-09-15
Status: RESEARCH CONTRACT — FROZEN FOR INITIAL BACKTEST / NOT LIVE

## 1. Objective

The buy engine must distinguish an asset that is merely cheap from an asset that is cheap **while the surrounding market transmission system is stabilizing**.

The minimum market vector is:

```text
Global/Geopolitical
→ Energy/Oil
→ Inflation/Fed
→ Rates
→ FX
→ Credit/Liquidity
→ Market Trend/Breadth
→ Leadership
→ Asset Fundamentals
→ Asset Price
```

Price is therefore a downstream condition, not the sole trigger.

## 2. Market Vector

| Cluster | Core signals | Direction for buy permission |
|---|---|---|
| Geopolitics | event state + confirmed market transmission | worsening = block escalation; stabilizing = neutral/positive |
| Energy | WTI/Brent level, trend, shock velocity, energy relative strength | acute oil shock = block B3/B4 |
| Rates | U.S. 2Y/10Y, real-rate proxy, curve, KR rates | falling/peaking stress = positive |
| FX | DXY, USD/KRW, USD/JPY, JPY/KRW | dollar/FX shock easing = positive |
| Credit/Liquidity | credit spread, funding stress, VIX/realized risk | stress contraction = positive |
| Market Trend | 1/5/20/60/120D return, MA slope/alignment, drawdown | stabilization/reversal = positive |
| Breadth | A/D, % above MA, new highs/lows, sector participation | improving breadth = positive |
| Leadership | semiconductor/AI/financial/auto relative strength + persistence | improving leadership = positive |
| Fundamentals | EPS/estimate revisions, guidance, margins, FCF/leverage where applicable | intact/improving = positive |
| Price | drawdown, valuation percentile, trend distance | deeper dislocation = opportunity, but never sufficient alone |

## 3. Independence Rules

Indicators are grouped into economic clusters before scoring.

- WTI and Brent: one Energy cluster.
- DXY and USD/KRW: related Dollar/FX cluster; do not award duplicate full weight.
- U.S. 10Y nominal and real yield: one Rates stress cluster unless empirical correlation justifies separation.
- SOX, semiconductor ETF and semiconductor leaders: Leadership cluster with correlation control.
- VIX and realized volatility: Risk cluster; retain distinct information only when incremental value is demonstrated.

The initial study uses equal weight within a cluster after correlation review. Cluster weights are frozen for the first test and are not optimized on OOS data.

## 4. Pre-Registered Permission Logic

Market conditions create a **permission layer**, not a hidden StockScore factor.

### B0 — No Buy

Any of the following:

- PIT/Data QA failure.
- Severe unresolved systemic stress.
- Active multi-shock deterioration (at least two independent shock clusters worsening).
- Asset structural impairment or fundamental break.

### B1 — Watch

- Price enters the predefined interest zone.
- No hard risk block.
- Market/leadership confirmation is insufficient.

### B2 — Scout

All of:

- Price dislocation reaches the preregistered zone.
- Market trend is no longer accelerating downward.
- At least one of leadership, rates, FX, credit, or breadth shows stabilization.
- No active hard-block condition.

### B3 — Active Buy

All of:

- B2 conditions remain valid.
- Market Trend and Breadth are stable/improving for the predefined persistence window.
- Leadership is not deteriorating and preferably improving.
- No active Energy/Rate/FX multi-shock.
- Fundamental state is intact.

### B4 — Aggressive Buy

B3 plus:

- extreme but preregistered price dislocation;
- asymmetric payoff after downside stress testing;
- at least two independent market clusters confirming stabilization;
- geopolitical transmission is not actively worsening;
- capital-survival constraint remains satisfied.

B4 is intentionally rare. Frequency is measured, not targeted.

## 5. Shock Block Rules

The study must explicitly test these cases:

| Shock | Example state | Initial rule treatment |
|---|---|---|
| Oil shock | sharp WTI/Brent acceleration + energy strength | prevent automatic escalation from B2 to B3/B4 |
| Rate shock | rapid 10Y/real-rate rise | prevent automatic escalation from price drawdown alone |
| FX shock | sharp DXY/USD-KRW pressure | reduce buy permission until stabilization |
| Credit shock | spread widening + volatility stress | block B4; test whether B3 should also be blocked |
| Multi-shock | >=2 independent worsening clusters | B0/B1 only until stabilization |

These are research gates, not live trading rules until validated.

## 6. Geopolitical Data Rule

A war/geopolitical label cannot directly create a numeric buy score.

Each event must be stored with:

- event timestamp;
- source and publication timestamp;
- event classification;
- geographic/commodity exposure;
- expected transmission channel;
- observed confirmation in oil/rates/FX/credit/volatility;
- availability timestamp.

The model evaluates **market transmission**, not headline sentiment.

## 7. Decision Separation

The existing Market Regime Engine remains the market-state engine.

`Market Regime → permission/risk constraint → BuyStrength → Action`

The existing StockScore remains separate.

`StockScore → company/asset opportunity`

The final decision must expose both dimensions:

```text
Opportunity = Stock / Sector / Price
Permission = Market / Risk / Shock
Action = f(Opportunity, Permission)
```

A high opportunity score cannot override a failed permission layer.

## 8. Required Point-in-Time Fields

Every market-vector observation must retain:

`observed_at`
`available_at`
`source_id`
`revision_status`
`raw_value`
`normalized_value`
`cluster`
`rule_version`

Decision timestamp rule:

`available_at <= decision_timestamp`

No later revision may be substituted into an earlier decision.

## 9. First Experiment

The first empirical experiment compares four progressively richer models:

- P0: Price-only drawdown baseline.
- P1: P0 + Market Trend/Breadth.
- P2: P1 + Leadership + Rates + Oil + FX + Credit.
- P3: P2 + Geopolitical transmission + Fundamentals.

For each model, report incremental change in:

- positive-return probability;
- median/mean forward return;
- worst forward return;
- forward MDD;
- downside-tail loss;
- survival constraint violations;
- false positives / misses;
- trigger frequency;
- lead time.

A more complex model is rejected when it fails to provide meaningful OOS improvement or materially worsens tail risk.

## 10. Horizon Matrix

Every signal is evaluated at:

`1D / 7D / 30D / 90D / 180D / 365D`

The primary capital-allocation horizons are 90D / 180D / 365D.

Short horizons are retained to detect falling-knife behavior.

## 11. Status

**FROZEN FOR INITIAL BACKTEST. NOT VALIDATED. NOT LIVE.**

No accuracy, expected return, or active-buy claim may be made until PIT data, execution convention, corporate-action normalization, OOS validation, sensitivity analysis, and falsification are completed.
