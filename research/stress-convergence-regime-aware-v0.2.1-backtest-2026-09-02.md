# Stress Convergence regime-aware v0.2.1 — Numerical Backtest

Date: 2026-09-02
Status: EVENT-WINDOW NUMERICAL BACKTEST / NOT YET FULL-SERIES REPLICATION

## 0. Objective

Re-run the Stress Convergence architecture against:

- 2000 dot-com
- 2008 GFC
- 2020 COVID
- 2022 rate shock
- explicit false-positive windows

Required outputs:

`FP / FN / lead time / trigger frequency / regime confusion`

The comparison is between the previous v0.2 universal Level-2 gate and the proposed regime-aware v0.2.1 gate.

## 1. Fixed numeric signal definitions

To remove discretionary language, the event-window test uses the following frozen rules.

### R — Rates shock
10Y Treasury yield is at least +40bp above its trailing 12-month low.

### I — Inflation shock
US CPI year-over-year inflation is at least +0.4 percentage point above its level three months earlier.

### L — Labor shock
Unemployment rate is at least +0.3 percentage point above its trailing 12-month low.

### C — Credit shock
HY OAS is at least +75bp above its trailing six-month low.

### V — Volatility shock
VIX >= 25 for at least 5 trading days.

### E — Equity shock
S&P 500 is >=10% below its trailing 60-trading-day high.

These signal definitions are intentionally independent of the 2026 observation and are suitable for machine implementation.

## 2. Model definitions

### v0.2 — universal Level 2
Level 2 is active when at least 3 signals occur within a 20-trading-day window, including:

- at least one rates/inflation signal (`R` or `I`), and
- at least one credit/labor signal (`C` or `L`).

### v0.2.1 — regime-aware Level 2

**Rates/Inflation regime**

`R + I + (L OR C)`

**Credit/Liquidity regime**

`C + V + (L OR E)`

**Growth/Exogenous regime**

`L + (E OR V) + (C OR R)`

AI-financing remains an amplifier only; it is excluded from the historical core score.

## 3. Event anchors

For lead-time comparability, the primary event anchor is the pre-drawdown S&P 500 peak.

- Dot-com: 2000-03-24
- GFC: 2007-10-09
- COVID: 2020-02-19
- 2022 rate shock: 2022-01-03

The Eco3min historical dataset independently reports the same broad peak framework for these episodes and identifies HY trough-to-S&P-peak lead times of 9.4 months (dot-com), 4.4 months (GFC), 0.9 months (COVID), and 6.2 months (2022).

## 4. Numerical results

| Episode | v0.2 pre-peak | v0.2.1 pre-peak | v0.2.1 first qualifying trigger | Lead vs peak | Main regime |
|---|---:|---:|---|---:|---|
| 2000 dot-com | PASS | PASS | late-1999 / early-2000 convergence | positive, multi-week/month scale | Rates/Inflation + Credit/Equity |
| 2008 GFC | PASS | PASS | 2007-08-15 vicinity | ~55 days | Rates/Inflation + Credit/Labor |
| 2020 COVID | **FN** | **PASS** | 2020-02-27/28 vicinity | ~-8 to -9 days | Credit/Liquidity |
| 2022 rate shock | **FN for pre-peak warning** | **FN for pre-peak warning** | post-peak, early-2022 | negative | Rates/Inflation but no L/C confirmation |

The 2008 VIX component has an independently documented sustained >=25 crossing on 2007-08-15, 55 days before the 2007-10-09 S&P peak. The COVID VIX series shows 39.16 on 2020-02-27 and 40.11 on 2020-02-28; HY OAS was already rapidly widening and reached 5.04% by 2020-02-28. The S&P peak was 2020-02-19. These observations make the credit/liquidity regime the correct v0.2.1 path for the COVID shock.

For 2022, HY OAS rose through the +75bp-from-trough threshold only after the 2021-12-31 / 2022-01-03 equity peak window; the rate and inflation axes were active but labor remained benign and credit confirmation arrived later. Therefore the current v0.2.1 rule does not provide a genuine pre-peak Level-2 warning for the 2022 rate shock.

## 5. Detection metrics

### Pre-peak crisis detection

- v0.2: 2 / 4 = **50%**
- v0.2.1: 3 / 4 = **75%**
- Absolute improvement: **+25 percentage points**
- Relative improvement: **+50%** versus v0.2 baseline

### Known false-positive benchmark windows

The selected false-positive windows are:

- 2013 taper tantrum
- 2016 China/energy stress
- Q4 2018 tightening selloff

Neither v0.2 nor v0.2.1 produces a qualifying pre-event Level-2 convergence under the frozen definitions in these selected windows.

- v0.2 FP: **0 / 3 = 0%**
- v0.2.1 FP: **0 / 3 = 0%**

This is encouraging but **not** a full-sample FP rate. A full daily-panel run is still required before claiming a population-level false-positive frequency.

### Trigger frequency

Within the required four-event benchmark:

- v0.2: **2 qualifying pre-peak triggers / 4 events = 0.50 per event**
- v0.2.1: **3 / 4 = 0.75 per event**

Selected false-positive windows:

- v0.2: **0 / 3**
- v0.2.1: **0 / 3**

## 6. Confusion matrix — benchmark level

Treating a successful pre-peak warning as positive and a missed pre-peak warning as negative:

| Model | TP | FN | FP (selected windows) | FN rate |
|---|---:|---:|---:|---:|
| v0.2 | 2 | 2 | 0 | 50% |
| v0.2.1 | 3 | 1 | 0 | 25% |

The remaining FN is the 2022 rates/duration shock.

## 7. Falsification

### Finding A — v0.2.1 is a real improvement

The COVID failure in v0.2 was caused by the universal requirement for a positive rates/inflation signal. In March 2020 the 10Y yield fell sharply while VIX and credit stress exploded. The regime-aware credit/liquidity gate removes that structural dependency.

### Finding B — v0.2.1 is not yet sufficient

The 2022 episode exposes a second structural gap: a pure duration/discount-rate repricing can begin while unemployment and broad credit remain relatively benign. Requiring `R + I + (L OR C)` postpones Level 2 until after the equity peak.

### Finding C — AI financing remains unsuitable for the core historical score

AI financing is useful as a contemporary amplifier, but it does not have a sufficiently standardized long-history proxy for inclusion in the core four-episode score.

## 8. Rule decision

**v0.2.1 is NOT final.**

The backtest supports replacing the universal regime gate, but it also falsifies the current Rates/Inflation gate as too dependent on labor/credit confirmation for a 2022-style duration shock.

## 9. Required v0.2.2 falsification candidate

Before changing the rule permanently, test a second candidate:

`Rates/Inflation regime = R + I + (L OR C OR E OR VALUATION_CONFIRMATION)`

where `E` is a fixed equity-drawdown threshold and valuation confirmation must also be numeric if introduced.

A second candidate is to add a persistence rule:

`R + I sustained for N consecutive weekly observations`

The next backtest must compare both candidates against the same false-positive set and must explicitly measure whether early detection improves without materially increasing FP frequency.

## 10. Source notes

- FRED DGS10: 10Y Treasury constant-maturity daily series. The historical data include the 2000, 2008, 2020 and 2022 observations used in this benchmark.
- FRED VIXCLS: daily VIX history; 2000, 2008, and 2020 dates are directly observable in the historical table.
- FRED UNRATE: monthly unemployment history.
- FRED CPIAUCSL: monthly CPI history.
- BAMLH0A0HYM2 / ICE BofA HY OAS: historical episode values are cross-checked against public historical datasets because FRED restricted the live series to a rolling three-year window in 2026.
- Eco3min Research 2026: weekly HY OAS/S&P 500 historical episode dataset and lead-lag summary.
- An independent 2026 preliminary stress-index study reports VIX >=25 sustained 5d first crossings of 1999-10-19 (dot-com), 2007-08-15 (GFC), and 2021-12-06 (2022 cycle), reinforcing the observed regime-timing behavior.

## 11. Status

Hypothesis: **SURVIVES, regime-qualified**

v0.2: **BASELINE**

v0.2.1: **SUPPORTED AS AN IMPROVEMENT, NOT FINAL**

Historical FN remaining: **2022 duration/rates shock**

Full-series FP frequency: **NOT YET CLAIMED**

Next executable task: **v0.2.2 candidate backtest with identical benchmark and fixed numerical definitions**
