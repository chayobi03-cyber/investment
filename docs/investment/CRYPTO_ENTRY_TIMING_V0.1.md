# Crypto Entry Timing V0.1

Date: 2026-09-26
Status: RESEARCH SPEC — CODED / NOT VALIDATED / NOT LIVE

## 1. Objective

Find purchase timing, not merely identify a bullish crypto asset.

The timing engine asks:

> Given information available at decision time t, is BTC in a defined price zone and has the decline stabilized enough to justify staged entry?

This is intentionally parallel to the project's stock entry-timing workflow.

## 2. Fixed Pipeline

BTC OHLCV -> Data QA / PIT -> signed shock / drawdown -> Trend -> Price Zone -> Stabilization -> Episode Clustering -> Entry State B0-B4 -> next-session execution -> Forward 1/5/20/60D + MAE/MFE -> P0-P5 -> P6 promotion gate

No same-day close is executed at the same close used to create the signal. Default research convention: next daily session open.

## 3. Deterministic Entry Variables

Initial price-only timing uses:
- MA20
- MA50
- MA200
- 3D return
- 5D return
- prior 60D high
- drawdown from prior 60D high
- prior 20D high/low

Default structural trend condition:

close > MA200 AND MA20 > MA50 AND MA50 > MA200

## 4. Interest Zones

| Zone | Drawdown from prior 60D high | Role |
|---|---:|---|
| Z0 | > -5% | no chase / watch |
| Z1 | -5% to -8% | first pullback |
| Z2 | -8% to -12% | deeper pullback |
| Z3 | <= -12% | deep dislocation; stronger confirmation |

Thresholds are pre-registered research parameters.

## 5. Stabilization

Baseline stabilization requires:
- 3D return > 0
- close >= MA20
- structural trend still valid

One green candle alone does not count as stabilization.

## 6. Entry States

B0 = no buy / data or trend gate failed.

B1 = watch / prepare. Price is near the first interest zone, but confirmation is incomplete.

B2 = scout. A predefined pullback or breakout condition is reached, but stabilization is incomplete.

B3 = active-buy research state. Pullback is in Z1/Z2 and stabilization is confirmed while structural trend remains valid. A validated breakout-continuation path may also reach B3.

B4 = aggressive-buy research state. Z3 deep dislocation + stabilization + MA20 reclaim + MA50 support + no hard macro/derivatives block in the richer model.

B4 is expected to be rare.

## 7. Episode Clustering

Repeated qualifying days inside the same pullback are one episode.

Baseline:
- episode starts on first Z1/Z2/Z3 or breakout day;
- repeated signals remain inside the episode until the re-arm/cooldown rule is satisfied;
- first B2/B3/B4 transition is the primary event;
- staged entries inside an episode are a separate secondary experiment.

## 8. Execution Convention

Signal at day t -> execute at open[t+1].

Required outcome horizons:
1D / 5D / 20D / 60D

Promotion analysis also requires 90D / 180D / 365D when sufficient history exists.

MAE uses worst low after entry. MFE uses best high.

## 9. P0-P6 Mapping

P0 Data QA / PIT: duplicate dates, ascending dates, valid OHLC, no missing required bars, availability before execution, >=200 observations.

P1 Signal: deterministic trend, zones, stabilization and candidate states.

P2 Episode: cluster repeated candidate days and identify primary events.

P3 Outcome: next-session execution and forward returns.

P4 Risk: MAE, MFE, drawdown and loss-tail statistics.

P5 Walk-forward: fixed rules across chronological development/OOS windows; no threshold retuning.

P6 Promotion: DATA_NOT_READY until richer permission-layer PIT history exists for BTC flow/ETF flow where applicable, derivatives, macro/rates/FX, liquidity/risk and geopolitical transmission.

## 10. Baselines

- periodic-buy baseline;
- every-5%-drawdown baseline;
- trend-conditioned pullback;
- trend + stabilization;
- richer permission layer.

Candidate success requires incremental OOS value versus simple baselines.

## 11. Evaluation

Primary: worst forward return, MAE, forward MDD, downside-tail loss, survival constraint, recovery time.

Secondary: median/mean return, positive-return probability, trigger frequency, false positives, missed opportunities, lead time, turnover/execution cost.

Do not tune thresholds to maximize return on the same historical sample.

## 12. Live Output Contract

CRYPTO ENTRY
ASSET: BTC
STATE: B1/B2/B3/B4
PRICE: current
ZONE: Z0/Z1/Z2/Z3
TREND: GREEN/AMBER/RED
STABILIZATION: YES/NO
ENTRY: WATCH / SCOUT / ACTIVE / BLOCKED
TRIGGER: exact condition
INVALIDATION: exact condition
DATA: timestamp + quality

No automatic order is generated.

## 13. Current Status

Coded for research and monitoring, not validated for live deployment.

Pre-promotion state: DATA_NOT_READY
