# Crypto Market Regime + Entry Engine V0.2

Date: 2026-09-26
Status: PREREGISTERED RESEARCH SPEC — NOT VALIDATED / NOT LIVE

## 1. Purpose

Freeze one integrated threshold contract for crypto market regime, BTC entry timing, and P0-P6 evaluation without changing the project's capital-preservation philosophy.

Rules:
- fail closed on P0/PIT failure;
- keep Market Score, Opportunity Score, and Buy State separate;
- BTC is the primary validation asset;
- thresholds are frozen before the next OOS run;
- any threshold change requires a new rule version and fresh OOS/walk-forward evaluation.

## 2. Pipeline

Macro/Liquidity → Observation → P0 Data QA/PIT → P1 Regime/Signal → P2 Episode → P3 Execution/Outcome → P4 Risk → P5 Walk-forward → P6 Promotion

Execution convention: signal at daily close t; research entry at next daily open t+1. The signal close is never reused as the executable entry price.

## 3. Market Score

| Axis | Weight |
|---|---:|
| Trend | 20% |
| Flow / Institutional | 20% |
| Macro / Liquidity | 20% |
| Breadth / Relative Strength | 15% |
| Derivatives | 10% |
| Volatility / Risk | 10% |
| Regulation / Market Structure | 5% |

Normalize each axis to 0-100 with point-in-time history. Higher always means healthier/safer. Retain raw evidence and normalization metadata.

Market gates:
- GREEN: 70-100
- YELLOW: 55-69.99
- RED: 0-54.99

Stress overrides:
- severe systemic stress → confirmed R6;
- two or more independent shock clusters worsening → confirmed R6;
- P0 failure → DATA_NOT_READY, not a trade-state downgrade.

Regime bands remain inherited from the prior R1-R6 contract:

| Regime | Score |
|---|---:|
| R1 | 75-100 |
| R2 | 60-74.99 |
| R3 | 50-59.99 |
| R4 | 40-49.99 |
| R5 | 25-39.99 |
| R6 | 0-24.99 |

Retain raw_regime and confirmed_regime.

## 4. BTC Entry Thresholds

Structural trend PASS requires:
- close > MA200;
- MA20 > MA50;
- MA50 > MA200.

Pullback drawdown is measured from the prior 60-day high, excluding the current decision bar:

| Zone | Drawdown |
|---|---:|
| Z0 | > -5% |
| Z1 | -5% to > -8% |
| Z2 | -8% to > -12% |
| Z3 | <= -12% |

Stabilization PASS requires all:
- 3-day return > 0%;
- close >= MA20;
- structural trend PASS;
- at least 2 positive closes in the latest 3 daily bars.

Breakout confirmation requires all:
- close >= prior 60-day high × 1.005;
- close above the prior 60-day high;
- 20-day volume ratio >= 1.20;
- 3-day return > 0%;
- no hard macro or derivatives block.

## 5. Macro / Liquidity Thresholds

Soft warnings:
- DXY 20-day change > +1.5%;
- U.S. 10Y 10-day change > +20 bp;
- U.S. real yield 10-day change > +15 bp;
- WTI 5-day change > +8%;
- USDKRW 20-day change > +2%.

Hard extreme:
- DXY 20-day change > +3%;
- U.S. 10Y 10-day change > +35 bp;
- U.S. real yield 10-day change > +25 bp;
- WTI 5-day change > +12%;
- USDKRW 20-day change > +3.5%.

Hard macro block = any hard extreme OR at least two soft warnings active and worsening simultaneously.

## 6. Derivatives Thresholds

Normal reference:
- absolute 8h funding <= 0.010%;
- 24h OI change between -5% and +5%;
- top-trader L/S ratio between 0.70 and 1.50.

Crowding warning:
- positive 8h funding > +0.030% or negative < -0.030%;
- 24h OI change > +8% while price change > +2%;
- top-trader L/S > 1.50 or < 0.70.

Hard derivatives block:
- positive 8h funding > +0.050% or negative < -0.050%;
- 24h OI change > +12% with price change > +3%;
- top-trader L/S > 1.80 or < 0.55.

A derivatives block prevents escalation to B3/B4. It is not itself a sell signal.

## 7. Volatility / Breadth

7-day realized volatility / 60-day realized volatility:
- <= 1.25 normal;
- >1.25 to 1.50 warning;
- >1.50 risk-off restriction.

Additional hard risk flag = 1-day high-low range >= 10% AND volatility ratio > 1.50.

Breadth:
- GREEN >= 65% of permissioned universe above MA20;
- YELLOW 50%-64.99%;
- RED <50%.

Alt rotation confirmation additionally requires ETH/BTC 20-day relative return >0% and >=60% of the permissioned alt universe above MA20, with no BTC hard block and no R6 override.

## 8. Buy State

| State | Core condition | Sleeve multiplier |
|---|---|---:|
| B0 | hard block / P0 fail / trend fail | 0.00 |
| B1 | zone reached, confirmation incomplete | 0.00 |
| B2 | zone or breakout + early stabilization | 0.20 |
| B3 | Z1/Z2 + stabilization, or validated breakout continuation | 0.60 |
| B4 | Z3 + stabilization + MA20 reclaim + MA50 support + 2 independent confirmation clusters + no hard macro/derivatives block | 1.00 |

Four-tranche research baseline: 20% / 25% / 30% / 25%.

## 9. Episode Rule

Repeated qualifying days are one episode unless all re-arm conditions are met:
- >=5 daily bars since prior primary event;
- price exited the previous zone;
- prior hard block is resolved.

The first B2/B3/B4 transition is the primary event.

## 10. P0-P6 Contract

P0 Data QA/PIT: duplicate check, timestamp order, OHLC validity, missing required series, freshness, available_at <= decision_timestamp, look-ahead check, >=200 BTC daily observations, and provenance.

P1 Signal: market score/gate, raw and confirmed regime, trend, drawdown, zone, stabilization, breakout, macro/derivatives blocks, breadth, opportunity score, and buy state.

P2 Episode: episode_id, start, day index, primary-event flag, re-arm status, trigger state, and independent confirmation clusters.

P3 Execution/Outcome: signal timestamp, next-open entry timestamp/price, cost bps, and forward returns for 1/5/20/60/90/180/365D where available.

P4 Risk: MAE, MFE, forward MDD, worst forward return, downside-tail loss, recovery days, survival violation, and stress loss.

P5 Walk-forward: chronological train/test windows, rule version/hash, threshold_retuned=false, execution cost included, baseline metrics, and OOS metrics.

P6 Promotion: only PROMOTE when P0, OOS, walk-forward, sensitivity, provenance, and look-ahead gates all pass and FP/FN/stress review is complete. Otherwise DATA_NOT_READY or BLOCKED.

Canonical machine-readable contract: `schemas/crypto_p0_p6_v0.2.schema.json`.

## 11. Evaluation Priority

Primary: MDD, worst forward loss, downside-tail loss, survival violations, recovery time.

Secondary: median/mean return, positive-return probability, trigger frequency, FP/FN, lead time, turnover/execution cost. CAGR remains secondary.

## 12. Freeze

These thresholds are frozen as `crypto-market-regime-entry-v0.2`. The current version is research-only and not live. Threshold changes require a new version and a complete re-evaluation.