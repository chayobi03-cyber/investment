# Dry Powder Deployment Trigger Table v0.1

- **Date:** 2026-10-13
- **Status:** PROPOSAL — amends [Allocation Rule v0.1 §7](../governance/PORTFOLIO_ALLOCATION_RULE_v0.1.md). Takes effect only when the user adopts it.
- **Evidence:** [Deployment ladder backtest v0.1](../../research/deployment-ladder-v0.1-backtest-2026-10-13.md)
- **Trigger:** [2026-10-13 portfolio review](2026-10-13_portfolio_review.md) F1 / P1

## 1. Rule change record (Allocation Rule §10)

| Field | Content |
|---|---|
| Triggering evidence | Dry Powder rose 52.0% → 59.7% while KOSPI fell ~30% from its record and §7 never fired. In the backtest, a drawdown-only ladder still holds 38% of the tranche as cash after 36 months on average, and holds more than half in 36% of starts. |
| Old rule | Stage 0 0–20%, then +20% / +25% / +25% / +30% on "corrections", triggers undefined (the stages add up to 120%). |
| New rule | **Time floor + drawdown accelerator.** Each month the cumulative deployed share is the larger of a 6-month time schedule and a drawdown ladder (§3). |
| Reason | The time floor guarantees deployment. Accelerators front-load buying when the destination market is already falling. Median cost vs a lump sum is about −2% over 36 months, against about −10% for the current ladder. |
| Failure mode introduced | The floor keeps buying through a crash such as 2008. Staging does **not** cap tail loss: P5 tranche drawdown is about −42% vs −45% for a lump sum. The real loss limit is the tranche size (§2), which keeps Dry Powder ≥ 45% after full deployment. |

## 2. Tranche

From the 2026-10-13 review, measured against the Balanced target:

| Destination | Gap | Instrument | Account |
|---|---:|---|---|
| US Core | ₩15.17M | TIGER US S&P500 | Pension |
| US Dividend | ₩3.17M | TIGER US Dividend Dow Jones | Pension |
| **Tranche total** | **₩18.34M** | split 83% / 17% on every buy | |

Not in this tranche:

- **Domestic Equity** is overweight (+₩3.5M). Allocation Rule §6 applies.
- **Hedge** (−₩3.6M) waits for the gold role review (review F7).
- **Satellite** is discretionary.
- **Nasdaq-100** is excluded because of AI/semiconductor overlap (review F3).

Funding order: pension cash ₩12.49M first, then sell KODEX CD Rate Active in the pension account. Toss cash is not used.

## 3. Trigger table

`k` counts months from adoption. Month 0 is the first scheduled buy date after adoption.

**Cumulative target(k) = max(time floor(k), accelerator level)**

Buy amount = target × ₩18.34M − amount already deployed (never negative).

### 3.1 Time floor — fires on schedule, no market condition

| Month k | Floor (cumulative) | Cumulative ₩ | This month ₩ (if no accelerator fired) |
|---:|---:|---:|---:|
| 0 (Stage 0) | 20% | 3.67M | 3.67M |
| 1 | 33% | 6.11M | 2.45M |
| 2 | 50% | 9.17M | 3.06M |
| 3 | 67% | 12.23M | 3.06M |
| 4 | 83% | 15.28M | 3.06M |
| 5 | 100% | 18.34M | 3.06M |

Scheduled buy date: first KRX trading day of each month.

### 3.2 Drawdown accelerator — fires on the destination market

Input: **S&P 500 index drawdown** = last close ÷ highest close over the trailing 252 trading days − 1, from a verified close (Data QA, §4).

| Level | S&P 500 drawdown touched | Cumulative target | Cumulative ₩ |
|---|---:|---:|---:|
| A1 | ≤ −10% | 40% | 7.34M |
| A2 | ≤ −15% | 60% | 11.00M |
| A3 | ≤ −20% | 80% | 14.67M |
| A4 | ≤ −30% | 100% | 18.34M |

- Each level fires **once**, on the next KRX trading day after the close that first touches it. Accelerators do not wait for the scheduled date.
- No stabilization or up-day condition: the backtest found it changed nothing once a time floor exists.
- If several levels are touched before execution, execute the deepest one.

### 3.3 What does *not* gate this table

- The KOSPI market monitor's `BUY_ALLOWED` and the Market Regime R1–R6. These are Korean / stock-level permissions. Gating the time floor on a regime brings back the never-deploy failure. They still govern every buy outside this table.
- USD/KRW. It was not tested (§6), so no FX gate is invented.

## 4. Hard stops (process, not market view)

| Condition | Effect |
|---|---|
| S&P 500 close cannot be verified | Accelerators do not fire. The time floor still executes, because it uses no market data. |
| Destination would push US Core above the Balanced 22% target | Cap the buy at the target. The remainder stays in Dry Powder. |
| User suspends the table in writing (repository record) | Stop all buys. Record the reason, and the date to resume or re-plan. |
| Recorded thesis break in broad US equity (structural, not price) | Escalate to the user. No automatic action. |

A falling market by itself is **not** a stop condition. A falling market is when the floor is designed to keep buying.

## 5. Monthly operating checklist

1. Record the S&P 500 close, its 252-day high and the drawdown, with source and timestamp.
2. Compute target(k). Buy = target × ₩18.34M − deployed.
3. Execute 83% in TIGER US S&P500 and 17% in TIGER US Dividend Dow Jones, in the pension account.
4. Log the date, amounts, fill prices, and the level or floor that fired.
5. After month 5, or once 100% is reached: recompute bucket weights and close this tranche.

## 6. Known gaps

- **FX:** buys are in KRW into unhedged S&P 500 exposure at USD/KRW ≈ 1,335. A strong-KRW reversal would lower KRW returns. This was not tested; candidate for v0.2.
- **Monthly vs daily data:** the backtest used monthly average prices, while live triggers use daily closes. Live accelerators will fire slightly earlier and more often than tested, which errs toward faster deployment.
- **Floor length is a preference:** a 12-month floor costs about 2 pp more median over 36 months with almost the same tail. The 6-month floor is the default here. The user may choose 12 months; the levels in §3.2 stay the same.
- **Domestic / Hedge tranches** need their own table once their gaps are justified.
