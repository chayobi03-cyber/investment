# Crypto Risk Engine V0.1

Date: 2026-09-26
Status: RESEARCH SPEC — CODED / NOT VALIDATED / NOT LIVE

## 1. Purpose

Extend the Investment project's capital-preservation framework to crypto assets without creating a separate decision philosophy.

The engine must:

- reuse the project's Data QA / PIT / fail-closed discipline;
- separate **Market Score**, **Opportunity Score**, and **Buy State**;
- treat derivatives and liquidity as risk controls, not return enhancers;
- use staged exposure rather than binary all-in/all-out decisions;
- keep BTC as the first validation asset;
- defer ETH/SOL/other altcoin promotion until BTC logic is empirically validated.

No live trading, leverage, margin, or automatic order execution is introduced by V0.1.

## 2. Architecture

```
Crypto Data
    ↓
Data QA / PIT Gate
    ↓
Crypto Observation Schema
    ↓
Trend / Flow / Vol-Risk / Derivatives / Macro / Breadth
    ↓
Crypto Market Score
    ↓
Market Regime R1-R6
    ↓
Permission Layer
    +
Asset / Price Opportunity
    ↓
Buy State B0-B4
    ↓
Exposure Ladder
    ↓
P0-P6 Backtest
    ↓
Falsification
    ↓
Promotion Gate
```

The engine is a market-state and risk-control layer. It does not embed market state a second time inside the asset opportunity score.

## 3. Market Score

Initial pre-registered weights:

| Axis | Weight |
|---|---:|
| Trend | 25% |
| Flow | 20% |
| Volatility / Risk | 15% |
| Derivatives | 15% |
| Macro | 15% |
| Breadth / Relative Strength | 10% |
| Total | 100% |

All axis inputs must be normalized to 0–100 using point-in-time history.

A missing required axis makes the market score **DATA_NOT_READY**.

## 4. Opportunity / Permission Separation

The decision model exposes at least three distinct outputs:

- `market_score`: health/opportunity of the crypto market context;
- `opportunity_score`: asset/price-specific opportunity;
- `buy_state`: operational research state after risk gates.

No hidden averaging is allowed that makes a high market score automatically imply a high buy score.

For capital preservation, the weaker side must be visible rather than masked:

```text
Opportunity = asset / price evidence
Permission  = market / risk / shock evidence
Action      = state machine using both
```

## 5. Regime

The existing project R1-R6 thresholds are inherited:

| Regime | Score |
|---|---:|
| R1 | 75–100 |
| R2 | 60–74.9 |
| R3 | 50–59.9 |
| R4 | 40–49.9 |
| R5 | 25–39.9 |
| R6 | 0–24.9 |

A stress override may force R6 when severe systemic stress is confirmed or at least two independent crypto shock clusters are simultaneously worsening.

Both `raw_regime` and `confirmed_regime` must be retained.

## 6. Buy State Machine

### B0 — No Buy

Hard block when any of the following is true:

- PIT/Data QA failure;
- required data missing or stale;
- severe systemic stress;
- at least two independent shock clusters worsening;
- asset structural break.

### B1 — Watch

- price reaches the pre-defined interest zone;
- no hard block;
- confirmation is insufficient.

No capital deployment is implied by B1.

### B2 — Scout

All of:

- price dislocation reaches the pre-registered zone;
- market trend is no longer accelerating downward;
- at least one independent stabilization cluster confirms;
- no hard block.

### B3 — Active Buy

All B2 conditions plus:

- stabilization persists for the pre-registered window;
- leadership is not deteriorating;
- macro shock is not active;
- asset/fundamental state is intact.

### B4 — Aggressive Buy

B3 plus:

- extreme but pre-registered dislocation;
- asymmetric downside/upside survives stress testing;
- at least two independent clusters confirm stabilization;
- geopolitical transmission is not actively worsening;
- capital-survival constraint remains satisfied.

B4 is expected to be rare. Its frequency is measured, not targeted.

## 7. Exposure Ladder

Exposure is measured as a fraction of a separately defined **crypto sleeve**, not the total portfolio.

| Buy State | Target sleeve exposure multiplier |
|---|---:|
| B0 | 0.00 |
| B1 | 0.00 |
| B2 | 0.20 |
| B3 | 0.60 |
| B4 | 1.00 |

Entry allocation research baseline:

```text
20% / 25% / 30% / 25%
```

These are staged-entry research parameters, not live account instructions.

## 8. Derivatives Risk

Required candidates:

- funding rate;
- open interest;
- OI change;
- futures basis;
- liquidation intensity.

Initial interpretation:

```text
Price ↑ + OI ↑ + funding sharply ↑
→ leverage-overheat flag
→ restrict escalation
```

Derivatives data must not be used as a direct "bullish score" without demonstrating incremental value over price/volume evidence.

## 9. Macro / Cross-Asset

The Crypto Engine inherits the project's transmission-chain concept:

```text
Geopolitics
→ Energy
→ Inflation
→ Fed
→ Rates
→ Credit / Liquidity
```

Crypto-specific monitoring should additionally cover:

- DXY;
- U.S. real yields;
- Treasury yields;
- liquidity/financial-condition proxies;
- Nasdaq / risk-asset relative strength;
- Gold;
- Oil;
- FX stress.

A geopolitical headline is not itself a numeric buy signal. The system evaluates confirmed market transmission.

## 10. Point-in-Time Contract

Every observation retains:

```text
observed_at
available_at
source_id
revision_status
raw_value
normalized_value
cluster
rule_version
```

Decision timestamp rule:

```text
available_at <= decision_timestamp
```

No revised or later-known data may be substituted into an earlier decision.

## 11. Episode / Backtest Rules

A signal occurring repeatedly inside the same drawdown is one episode unless a predefined re-arm rule is satisfied.

Required horizons:

```text
1D / 7D / 30D / 90D / 180D / 365D
```

Primary capital-allocation horizons:

```text
90D / 180D / 365D
```

The first test compares:

- P0: price-only;
- P1: price + trend/breadth;
- P2: P1 + flow/derivatives/macro/risk;
- P3: P2 + geopolitics/fundamentals.

Promotion requires incremental OOS value, not merely positive historical return.

## 12. Evaluation Priority

Primary:

1. maximum drawdown;
2. worst forward loss;
3. downside-tail loss;
4. survival constraint violations;
5. recovery time.

Secondary:

- positive-return probability;
- median/mean forward return;
- false positives;
- misses;
- trigger frequency;
- lead time;
- turnover/execution cost.

CAGR is secondary.

## 13. Promotion Gate

A rule is not promoted to live use until:

- Data QA and PIT checks pass;
- baselines are evaluated;
- OOS testing passes;
- walk-forward testing passes;
- parameter sensitivity passes;
- execution cost is included;
- false positives and misses are reviewed;
- stress/event anchors are reviewed;
- source provenance is complete;
- no look-ahead issue remains.

V0.1 is therefore **coded but NOT VALIDATED / NOT LIVE**.

## 14. Implementation Boundary

V0.1 code intentionally contains deterministic scoring and state-machine logic only.

It does not:

- place orders;
- choose an exchange;
- manage private keys;
- use leverage;
- convert a live observation into an automatic buy order.

Those capabilities require a separate validated promotion gate.
