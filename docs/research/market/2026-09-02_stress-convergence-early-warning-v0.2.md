# Stress Convergence Early-Warning Framework v0.2

Date: 2026-09-02 KST  
Status: **CALIBRATED CANDIDATE — pending full-series backtest**

## 1. Calibration basis

v0.1 event-window backtest detected all four selected target stress episodes but generated a false positive in the 2011 US downgrade / Euro-area debt episode.

The dominant failure was not a single numeric threshold. It was the confirmation topology: Energy + Inflation + Credit + VIX can align during a non-systemic risk-off episode without a persistent policy/rates transmission.

Therefore v0.2 changes the trigger architecture first and keeps most numeric thresholds stable.

## 2. v0.2 indicators and thresholds

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

Numeric threshold changes from v0.1 are intentionally minimal. Persistence is now explicit and is itself a threshold condition.

## 3. Two-leg L2 trigger architecture

### A. Inflationary convergence leg

L2 Defensive may activate when:

- Energy is at least warning, and
- Credit is at least warning, and
- at least one of Inflation or Energy is materially worsening, and
- **Fed or Rates is confirmed**, and
- the conditions persist for the defined observation window.

Operationally: `Energy + Credit + (Inflation) + (Fed OR Rates)` with persistence.

This is the preferred detector for an inflationary macro-financial transmission such as 2022.

### B. Financial-shock leg

L2 Defensive may activate when:

- Credit is at least material stress, and
- VIX is at least material stress, and
- NFCI/financial conditions confirm stress,
- with persistence.

Operationally: `Credit + VIX + NFCI`.

This preserves detection of non-inflationary systemic shocks such as 2020.

## 4. Independence rules

- Fed and 10Y Treasury are treated as one **Policy/Rates family** for confirmation purposes.
- VIX and equity volatility are one **Market Stress family**.
- HY OAS is a distinct **Credit family**.
- NFCI is a distinct **Financial Conditions family**, but may not be counted twice with a credit-market-only signal unless the change is independently meaningful.
- AI financing is a separate **Real-Economy/Financing family** and is not backfilled into pre-AI historical periods.

The score remains 0–24, but action escalation depends on a gate, not score alone.

## 5. Action levels

| Level | Score | Gate requirement | Meaning |
|---|---:|---|---|
| L0 | 0–3 | none | Normal |
| L1 | 4–7 | none | Watch |
| L2 | 8–11 | Inflationary leg OR Financial-shock leg | Defensive |
| L3 | 12–17 | L2 gate + stronger persistence / severe confirmation | High Stress |
| L4 | 18–24 | L3 + severe Credit or systemic confirmation | Crisis Convergence |

## 6. Why 2011 should now be rejected

2011 had elevated oil, inflation expectations, high-yield spreads and VIX, which was enough to trip v0.1. However, the Policy/Rates leg was not simultaneously confirming an inflationary tightening transmission.

Under v0.2, the 2011 episode therefore remains below the inflationary-convergence gate unless an independent financial-conditions shock also reaches the separate financial-shock leg.

## 7. Why 2022 should remain detected

2022 combined:

- Energy > warning
- policy tightening / hawkish repricing
- HY OAS >400bp
- recurring VIX >25
- inflation expectations above the v0.1 warning level for part of the cycle

The inflationary leg therefore remains capable of activating before the eventual 2022 equity low. The 10Y >4.75% threshold is not required when the Fed-policy leg is independently confirmed.

## 8. Why 2020 should remain detected

COVID produced an acute financial shock with extreme VIX and sharply wider credit conditions; the Federal Reserve documents VIX reaching 82.7 during March 2020. The correct response is not to force an Energy/Inflation signal into this episode but to use the separate financial-shock leg. citeturn907898search0

## 9. 2000 and 2008 treatment

Older crises should be used primarily to validate the financial-shock and policy/rates topology, with compatibility proxies where modern series are unavailable.

The benchmark must distinguish:

- data unavailable,
- proxy used,
- genuine zero/normal reading.

A missing historical series may not be silently encoded as zero.

## 10. Falsifiers for v0.2

v0.2 should be reopened if any of the following occurs in the full-series backtest:

1. 2011 or similar risk-off episodes repeatedly trigger L2 despite no policy/rates or systemic-financial confirmation.
2. 2020-type systemic shocks fail the financial-shock leg.
3. 2022-type inflation/rates cycles fail the inflationary leg before material drawdown/credit deterioration.
4. The gate materially reduces lead time below the minimum investment-useful horizon.
5. A broader rolling sample produces an unacceptable false-positive rate.

## 11. Current validation status

**v0.2 is a candidate calibration, not a validated production model.**

The next required test is a full daily/weekly time-series backtest covering the complete sample around the selected episodes, not just hand-picked event dates.

Required outputs:

- exact first-trigger timestamps,
- signal persistence,
- FP/FN by episode and by rolling non-event window,
- lead-time distribution,
- per-axis marginal contribution,
- ablation of each gate condition,
- sensitivity to threshold perturbations.

## 12. Promotion decision

Do not promote v0.2 to production/actionable capital allocation until the full-series backtest passes.
