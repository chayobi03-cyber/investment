# Stress Convergence Threshold Backtest — v0.1

Date: 2026-09-02 KST  
Status: **PHASE-A EVENT-WINDOW BACKTEST — CALIBRATION INPUT**

## 1. Objective

Validate the provisional Stress Convergence v0.1 thresholds against 2000 dot-com stress, 2008 GFC, 2020 COVID financial shock, 2022 inflation/rates shock, 2011 false-positive control, and 2018 false-positive control.

Measures: detection/recall, false positives, false negatives, lead time, and axis failure mode.

The purpose is calibration, not retrospective proof of predictive power.

## 2. v0.1 threshold under test

| Axis | Warning | Severe |
|---|---:|---:|
| Energy / Brent | >$90 | >$100 |
| Inflation / US 5Y5Y forward | >2.5% | >3.0% |
| Fed / policy repricing | >50% near-term hike probability or strong hawkish repricing | extreme repricing |
| Rates / US 10Y | >4.75% | >5.0% |
| Credit / US HY OAS | >400bp | >500bp |
| Financial conditions / NFCI | >0 | >0.5 |
| Market stress / VIX | >25 | >35 |
| AI financing | 2+ independent financing stress signals | severe/refinancing or credit event |

L2 requires at least three economically distinct stressed axes and at least one Credit/Private Credit confirmation.

## 3. Benchmark protocol

### 3.1 No hindsight threshold fitting

The v0.1 thresholds are evaluated first. Threshold changes are allowed only after the event-window results are recorded.

### 3.2 Event anchor

Lead time is measured from the first estimated L2 trigger in the selected event window to the event anchor. Event anchors are defined per episode and are not chosen after seeing signal timing.

### 3.3 Historical comparability control

The 5Y5Y series begins in 2003, so 2000 requires a compatibility proxy for inflation expectations. AI financing is not meaningful for pre-modern-AI regimes and is treated as N/A rather than zero.

This makes the phase-A test an event-window validation, not yet a full daily all-series backtest.

## 4. Results

| Episode | v0.1 | Estimated trigger | Anchor | Lead | Key driver | Caveat |
|---|---|---|---|---:|---|---|
| 2000 dot-com | TP | 2000-09-01 | 2001-03-01 | 181d | Fed/rates + credit + volatility | pre-2003 proxy required |
| 2008 GFC | TP | 2008-01-22 | 2008-09-15 | 237d | inflation + credit + volatility | policy/rates and energy are not sufficient alone |
| 2020 COVID | TP | 2020-03-16 | 2020-03-23 | 7d | credit + VIX + NFCI | acute financial shock, not inflationary mechanism |
| 2022 inflation/rates | TP | 2022-03-07 | 2022-10-12 | 219d | energy + Fed + credit | 10Y >4.75% not required for early warning |
| 2011 debt/Euro stress | **FP** | 2011-08-03 | 2011-08-05 | 2d | energy + inflation + credit + VIX | no policy/rates transmission confirmation |
| 2018 Q4 selloff | TN | — | 2018-12-24 | — | credit + VIX | insufficient independent axes for L2 |

### Observed metrics

- Target stress episodes evaluated: **4**
- Target stress episodes detected: **4 / 4**
- Selected target-event recall: **100%**
- False-positive controls: **2**
- False positives: **1 / 2**
- Selected-control false-positive rate: **50%**
- False negatives: **0 / 4**
- Median lead time: **~200 days**
- Mean lead time: **~161 days**

These statistics are not population estimates. The control set is deliberately small and mechanism-focused.

## 5. Evidence highlights

### 2008

The FRED 5Y5Y series shows values above 2.5% in early 2008, including 2.76% on 2008-03-10. See FRED series T5YIFR.

### 2020

The Federal Reserve documents a VIX peak of 82.7 during March 2020. S&P Global notes that 2020 corporate spreads widened to the widest level since the GFC, while the GFC peak was above 2,000bp for high yield. This supports a separate financial-shock leg.

### 2022

FRED VIX data show repeated >25 readings beginning January 2022. ICE BofA HY OAS was 4.01% on 2022-03-07 and reached 4.87% on 2022-06-13, so credit confirmation was available early in the tightening cycle.

### 2011 false positive

A J.P. Morgan research note showed US high-yield spreads around 604bp on 2011-08-03. FRED 5Y5Y inflation expectations were above 2.5% for parts of 2011, while oil and VIX were elevated. This satisfies the v0.1 three-axis convergence logic without producing a US systemic banking crisis.

## 6. Falsification result

### Survived

1. The broad score architecture detects all four selected target episodes.
2. The framework detects both inflationary/rates stress (2022) and non-inflationary systemic market stress (2020).
3. The 2018 control does not reach L2.

### Failed

The v0.1 rule `3 independent axes + credit` is too permissive for inflationary risk-off episodes. 2011 is the clearest failure case.

The failure is primarily **confirmation topology**, not an obviously incorrect individual threshold.

## 7. Calibration decision

Do not optimize numeric thresholds first. Change the trigger topology first.

1. Preserve the individual numeric thresholds unless the full-series sample disproves them.
2. Split L2 into two mechanisms:
   - **Inflationary convergence:** Energy + Credit + (Inflation) + (Fed OR Rates).
   - **Financial shock:** Credit + VIX + NFCI.
3. Add explicit persistence: daily 5 trading days or 2-of-3 within 5 days; monthly inflation 2 consecutive observations; weekly NFCI 2 consecutive observations.
4. Require deterioration over a lookback window for L3/L4 escalation.
5. Keep AI financing as a separate axis and do not backfill it into older regimes.

## 8. Decision

**v0.1: REJECT AS PRODUCTION THRESHOLD SET.**

It is accepted as the frozen research baseline for v0.2 calibration.
