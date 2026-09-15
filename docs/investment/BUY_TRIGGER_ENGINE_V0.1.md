# BUY Trigger Engine V0.1 — Market-Aware Pre-Registered Research Contract

Date: 2026-09-15
Status: RESEARCH SPEC — NOT LIVE / NOT VALIDATED

## 1. Purpose

A buy decision must not be generated from price drawdown alone.
The engine tests whether a sufficiently attractive asset price is occurring inside a market environment whose trend, leadership, macro variables, cross-asset signals, and geopolitical risk are becoming supportive or at least no longer deteriorating.

The research chain is:

```text
Hypothesis
→ Point-in-time Data
→ Market Regime
→ Leadership
→ Asset/Fundamental State
→ Price Zone
→ Buy Trigger
→ Action
→ Forward Return / MDD / Survival
→ Falsification
```

This document is a pre-registration contract. Thresholds must not be tuned using OOS results.

## 2. Decision Layers

```text
L0 Data QA / PIT Gate
        ↓
L1 Global & Geopolitical Regime
        ↓
L2 Market Trend / Breadth / Risk
        ↓
L3 Leadership / Sector Relative Strength
        ↓
L4 Macro & Cross-Asset
        ↓
L5 Asset Fundamentals
        ↓
L6 Price / Valuation / Drawdown
        ↓
L7 Buy Strength
        ↓
Action: B0 / B1 / B2 / B3 / B4
```

A failed upstream gate is fail-closed: no higher-level buy signal is valid.

## 3. Required Market Axes

| Axis | What it answers | Candidate inputs |
|---|---|---|
| Market Trend | Is the broad market still falling? | index 1/5/20/60/120D return, MA slope/alignment, drawdown |
| Leadership | Is capital returning to leading groups? | semiconductor/AI/financial/auto relative strength, breadth, leadership persistence |
| Oil / Energy | Is an inflationary energy shock developing? | WTI/Brent trend, volatility, energy-vs-equity relative strength |
| Rates | Is the discount rate becoming less hostile? | U.S. 2Y/10Y, real-rate proxy, curve, KR rates |
| FX | Is dollar/FX pressure easing? | DXY, USD/KRW, USD/JPY, JPY/KRW |
| War / Geopolitics | Is a new supply/risk shock emerging? | event state + market confirmation through oil, volatility, FX, credit |
| Credit / Funding | Is systemic stress easing? | credit spreads, funding/liquidity stress, financial conditions |
| Price | Is the asset sufficiently dislocated? | drawdown, valuation, volatility, distance from trend |
| Fundamentals | Is the decline thesis-destroying? | earnings revisions, guidance, balance-sheet/FCF indicators |

Geopolitical labels alone are not sufficient. The engine should preferentially use observable market transmission channels and record the event source separately.

## 4. Independence / Double-Counting Control

Highly correlated indicators must be clustered before aggregation.

Examples:
- WTI and Brent should not receive duplicate full weight.
- DXY and USD/KRW may share a dollar-risk cluster.
- SOX, semiconductor ETF, and individual semiconductor leaders require correlation control.
- 10Y nominal yield and real yield must be treated as related rate signals.

Market Regime remains separate from Stock Score, consistent with MARKET_REGIME_ENGINE_V1. Market conditions affect BuyStrength/permission rather than being silently embedded twice.

## 5. Preliminary Buy States

| State | Interpretation | Minimum condition |
|---|---|---|
| B0 | No buy | Data/regime/price conditions insufficient |
| B1 | Watch | Price enters predefined interest zone, but confirmation absent |
| B2 | Scout | Price dislocation + first evidence of stabilization |
| B3 | Active buy | Price dislocation + market stabilization + leadership/fundamental support |
| B4 | Aggressive buy | B3 + extreme dislocation + asymmetric payoff + no active systemic deterioration |

These labels are research states, not recommendations.

## 6. Pre-Registered Hypothesis

### H1 — Price-only is insufficient

A price-drawdown trigger will produce more false starts during persistent bear regimes than a trigger conditioned on market trend and macro/risk stabilization.

### H2 — Leadership confirmation improves timing

For growth/semiconductor assets, a large price drawdown accompanied by improving sector relative strength should have better forward risk-adjusted outcomes than the same drawdown without leadership improvement.

### H3 — Macro shock filters reduce adverse selection

A deep equity drawdown accompanied by worsening oil + rates + FX should not automatically escalate to B3/B4 because the apparent cheapness may reflect a continuing macro shock.

### H4 — Stabilization matters more than a single reversal day

Persistence across multiple observations should outperform a one-day reversal rule after controlling for entry price and market regime.

## 7. Required Signal Construction

Every candidate signal must specify before testing:

1. exact input series;
2. observation timestamp;
3. `available_at` timestamp;
4. normalization method;
5. threshold;
6. persistence requirement;
7. entry convention;
8. holding horizon;
9. invalidation/stop condition if applicable;
10. expected failure mode.

No same-day close may use information unavailable before the decision timestamp. Default execution test is next-session open to prevent look-ahead bias.

## 8. Test Matrix

Each trigger must be evaluated across multiple dimensions, not only holding period.

### Horizon

1D / 7D / 30D / 90D / 180D / 365D / 730D

### Drawdown

0–5% / 5–10% / 10–15% / 15–20% / 20–30% / >30%

### Market Regime

R1 / R2 / R3 / R4 / R5 / R6

### Buy State

B1 / B2 / B3 / B4

### Leadership State

Improving / Neutral / Deteriorating

### Macro Shock State

Stable / Oil Shock / Rate Shock / FX Shock / Multi-shock

The primary decision table is:

`BuyState × MarketRegime × Leadership × MacroShock × Drawdown × Horizon`

## 9. Baselines

At minimum compare against:

- Baseline A: buy at every fixed drawdown threshold.
- Baseline B: buy only when broad market trend stabilizes.
- Baseline C: buy using the existing Market Regime without asset-level price confirmation.
- Candidate: full market-aware Buy Trigger Engine.

The candidate is not considered successful merely because it earns a positive return. It must demonstrate incremental value versus simple baselines.

## 10. Evaluation Metrics

Primary:

- forward return: 30/90/180/365D
- median forward return
- worst forward return
- forward maximum drawdown
- probability of positive return
- downside-tail loss
- survival / capital-loss constraint

Secondary:

- false positive (오탐)
- miss (미탐)
- lead time (조기 탐지 시간)
- trigger frequency (경보 발생 횟수)
- excess return versus baseline
- turnover / estimated execution cost

CAGR is secondary to MDD, stress loss, and survival.

## 11. Event Independence

Do not count every day inside one drawdown as an independent signal.
Signals must be clustered into independent episodes with a predefined cooldown/re-arm rule. The first valid trigger in an episode is the primary event unless the experiment explicitly tests staged entries.

## 12. Validation Protocol

Required sequence:

```text
Development
→ Validation
→ OOS
→ Walk-forward
→ Parameter sensitivity
→ Stress/event review
→ Falsification
→ Promotion decision
```

Historical crisis anchors should include, where data coverage permits, 2000, 2008, 2020, and 2022. False-positive periods must be retained; only successful crisis detections are insufficient evidence.

Minimum sample-size requirements and confidence intervals must be reported before promotion. Small-sample crisis observations are descriptive evidence, not statistical proof.

## 13. Promotion Gate

B3/B4 cannot become operational unless the candidate:

- passes PIT/Data QA;
- beats or materially improves on relevant baselines OOS;
- does not materially worsen tail loss/MDD;
- survives threshold sensitivity;
- survives walk-forward testing;
- survives false-positive and false-negative review;
- has documented data provenance;
- has no unresolved look-ahead or corporate-action issue.

A high backtest return alone is never sufficient.

## 14. Immediate Implementation Scope

V0.1 should first establish a clean price-only baseline and then add, one cluster at a time:

1. Market Trend/Breadth;
2. Leadership;
3. Rates;
4. Oil/Energy;
5. FX;
6. Credit/Risk;
7. Geopolitical transmission state;
8. Fundamentals.

This staged design permits ablation testing: if removing an axis does not reduce OOS explanatory or decision value, that axis should not remain in the production model merely because it is intuitively attractive.

## 15. Current Status

**NOT VALIDATED. NOT A LIVE TRADING RULE.**

The next empirical task is to construct the PIT datasets and run the full matrix against the baselines. No claim of predictive accuracy or expected return is permitted until that test is executed.
