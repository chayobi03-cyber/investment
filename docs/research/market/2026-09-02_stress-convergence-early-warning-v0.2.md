# Stress Convergence Early-Warning Framework v0.2

Date: 2026-09-02 KST  
Status: **CALIBRATED CANDIDATE — pending full-series backtest**

## 1. Calibration basis

v0.1 detected all four selected target stress episodes but generated a false positive in the 2011 US downgrade / Euro-area debt episode.

The dominant failure was confirmation topology: Energy + Inflation + Credit + VIX can align during a non-systemic risk-off episode without persistent policy/rates transmission.

v0.2 therefore changes the trigger architecture first and keeps most numeric thresholds stable.

## 2. v0.2 thresholds

| Axis | Warning | Severe | Persistence |
|---|---:|---:|---|
| Energy / Brent | >$90 | >$100 | 5 trading days or 2-of-3 observations in 5 days |
| Inflation / US 5Y5Y | >2.5% | >3.0% | 2 consecutive monthly observations |
| Fed / policy repricing | >50% near-term hike probability or strong hawkish repricing | >75% or extreme repricing | 2 observations within 5 trading days |
| Rates / US 10Y | >4.75% | >5.0% | 5 trading days or 2-of-3 observations in 5 days |
| Credit / US HY OAS | >400bp | >500bp | 5 trading days or 2-of-3 observations in 5 days |
| Financial conditions / NFCI | >0 | >0.5 | 2 consecutive weekly observations |
| Market stress / VIX | >25 | >35 | 5 trading days or 2-of-3 observations in 5 days |
| AI financing | 2+ independent financing stress signals | refinancing/default/guarantee failure | evidence must persist or repeat |

Numeric thresholds are intentionally close to v0.1. Persistence is now explicit and therefore testable.

## 3. Two-leg L2 trigger architecture

### A. Inflationary convergence leg

L2 Defensive requires:

- Energy at least warning;
- Credit at least warning;
- Inflation materially worsening OR Energy materially worsening;
- **Fed or Rates confirmed**;
- persistence satisfied.

Operational form: `Energy + Credit + (Inflation) + (Fed OR Rates)`.

### B. Financial-shock leg

L2 Defensive requires:

- Credit at least material stress;
- VIX at least material stress;
- NFCI / financial conditions confirms stress;
- persistence satisfied.

Operational form: `Credit + VIX + NFCI`.

This preserves detection of non-inflationary systemic shocks such as COVID while rejecting the 2011-style inflation/energy/credit/VIX-only cluster.

## 4. Independence rules

- Fed and US 10Y are one Policy/Rates family for confirmation purposes.
- VIX and equity volatility are one Market Stress family.
- HY OAS is a separate Credit family.
- NFCI is a separate Financial Conditions family and should not be counted twice from mechanically linked observations.
- AI financing is a separate Real-Economy/Financing family and is not backfilled into older regimes.

Score remains 0–24, but action escalation requires a gate.

## 5. Action levels

| Level | Score | Gate | Meaning |
|---|---:|---|---|
| L0 | 0–3 | none | Normal |
| L1 | 4–7 | none | Watch |
| L2 | 8–11 | Inflationary leg OR Financial-shock leg | Defensive |
| L3 | 12–17 | L2 + stronger persistence / severe confirmation | High Stress |
| L4 | 18–24 | L3 + severe Credit or systemic confirmation | Crisis Convergence |

## 6. Calibration rationale

2011 is the primary v0.1 failure case. It had high-yield spreads around 604bp on 2011-08-03 and other elevated risk indicators, demonstrating that raw multi-axis level counts can overfire during non-systemic risk-off events.

The adjustment is therefore structural rather than a simple increase of the HY or VIX thresholds. Raising those thresholds would damage the desired sensitivity to 2020 and 2022.

## 7. Falsifiers

Reopen v0.2 if:

1. 2011-like episodes repeatedly pass L2 without policy/rates or systemic-financial confirmation.
2. 2020-like shocks fail `Credit + VIX + NFCI`.
3. 2022-like inflation/rates cycles fail the inflationary gate before material drawdown/credit deterioration.
4. Gate logic reduces lead time below the investment-useful horizon.
5. A rolling full-series backtest produces an unacceptable false-positive rate.

## 8. Validation status

v0.2 is a calibrated research candidate, **not a validated production model**.

The required next test is a full daily/weekly historical backtest over complete windows around the benchmark episodes, including non-event rolling controls.

Required outputs:

- exact first-trigger timestamps;
- persistence states;
- FP/FN by episode and rolling non-event windows;
- lead-time distribution;
- axis marginal contribution;
- gate ablation;
- threshold sensitivity grid.

Promotion to actionable capital allocation is blocked until that test passes.
