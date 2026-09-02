# Stress Convergence Threshold Backtest — v0.1

Date: 2026-09-02 KST  
Status: **PHASE-A EVENT-WINDOW BACKTEST — CALIBRATION INPUT**

## 1. Objective

Validate the provisional Stress Convergence v0.1 thresholds against:

- 2000 dot-com stress
- 2008 Global Financial Crisis
- 2020 COVID financial shock
- 2022 inflation/rates shock
- 2011 false-positive control
- 2018 false-positive control

Measures:

- detection / recall
- false positives
- false negatives
- lead time
- axis contribution / failure mode

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

The 5Y5Y series begins in 2003, so 2000 requires a compatibility proxy for inflation expectations. AI financing is not available as a meaningful historical axis before the modern AI infrastructure financing regime and is therefore treated as N/A rather than zero for pre-AI episodes.

This makes the phase-A test an **event-window validation**, not yet a full daily, all-series backtest.

## 4. Results

| Episode | v0.1 result | Estimated trigger | Anchor | Lead | Key driver | Failure / caveat |
|---|---|---|---|---:|---|---|
| 2000 dot-com | TP | 2000-09-01 | 2001-03-01 | 181d | Fed/rates + credit + volatility | pre-2003 proxy required |
| 2008 GFC | TP | 2008-01-22 | 2008-09-15 | 237d | inflation + credit + volatility | energy/rates are not sufficient alone |
| 2020 COVID | TP | 2020-03-16 | 2020-03-23 | 7d | credit + VIX + NFCI | detects acute financial shock, not inflation mechanism |
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

These statistics are **not population estimates**. The control set is deliberately small and hand-selected to attack the mechanism.

## 5. Evidence highlights

### 2008

The FRED 5Y5Y series shows values above 2.5% in early 2008, peaking at 2.76% on 2008-03-10. citehttps://fred.stlouisfed.org/data/T5YIFR

### 2020

The Federal Reserve documents a VIX peak of 82.7 during the March 2020 crash. A contemporary S&P Global analysis notes high-yield spreads above 2,000bp at the 2008 peak and describes the 2020 spread widening as the widest since the GFC. The Fed/NFCI benchmark used in the project is consistent with a distinct financial-shock leg even without inflationary confirmation.

### 2022

The FRED VIX data show repeated >25 readings beginning January 2022 and sustained episodes through the year. ICE BofA HY OAS data show 4.01% on 2022-03-07 and substantially higher levels thereafter, including 4.87% on 2022-06-13. This means the credit-confirmation gate can turn on early in the tightening cycle rather than only at the October risk-off peak. citehttps://fred.stlouisfed.org/data/VIXCLShttps://equibles.com/economicdata/bamlh0a0hym2

### 2011 false positive

J.P. Morgan data cited in an August 2011 research note show US high-yield spreads around 604bp on 2011-08-03. The FRED 5Y5Y series was also above 2.5% during much of 2011, while oil and VIX were elevated. This combination is enough to satisfy the v0.1 three-axis convergence rule even though the episode did not become a US systemic banking crisis. citeturn172339search36turn112719search0

### 2020 control interpretation

The 2020 episode should not be treated as a failure merely because Energy and Inflation were benign. The framework is intended to detect convergence across distinct stress mechanisms; a Credit + Market Stress + Financial Conditions cluster is itself a legitimate systemic-stress pattern. The framework must therefore preserve a separate financial-shock detection leg. citeturn907898search0turn907898search8

## 6. Falsification result

### What survived

1. The broad score architecture detects all four selected target episodes.
2. The framework is capable of detecting both inflationary/rates stress (2022) and non-inflationary systemic market stress (2020).
3. The 2018 control does not trigger L2 because only credit/volatility are sufficiently stressed.

### What failed

The v0.1 rule `3 independent axes + credit` is too permissive for inflationary risk-off episodes. 2011 is the clearest failure case.

The problem is not the individual thresholds. The problem is the **confirmation topology**: Energy + Inflation + Credit + VIX can be simultaneously elevated without a persistent policy/rates transmission into a systemic crisis.

## 7. Calibration decision

**Do not optimize numeric thresholds yet. Change the trigger topology first.**

The calibration priority is therefore:

1. Preserve the existing individual warning thresholds as much as possible.
2. Split L2 confirmation into two mechanisms:
   - **Inflationary convergence leg:** Energy + Inflation + (Fed or Rates) + Credit.
   - **Financial-shock leg:** Credit + VIX + NFCI/market-liquidity condition.
3. Require persistence:
   - daily indicators: 5 trading days or 2-of-3 observations within a 5-day window;
   - monthly inflation expectations: 2 consecutive monthly observations.
4. Require a deterioration condition for escalation, not only a level breach.
5. Keep AI financing as a separate axis and do not backfill it into older regimes.

## 8. Decision

**v0.1 status: REJECT AS PRODUCTION THRESHOLD SET.**

It is useful as a research baseline because it detected the target episodes, but the 2011 false positive demonstrates that the convergence rule is not sufficiently causal.

The next version should be **v0.2 topology-calibrated**, not simply a numeric threshold tweak.
