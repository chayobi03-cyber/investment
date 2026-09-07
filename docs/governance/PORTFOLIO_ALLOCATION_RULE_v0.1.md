# Portfolio Allocation Rule v0.1

- Date: 2026-09-07
- Status: WORKING BASELINE
- Scope: Personal portfolio allocation and capital deployment decisions
- Source: 2026-09-07 portfolio structure review

## 1. Purpose

The portfolio is managed by functional role rather than ticker-by-ticker selection.
The primary decision unit is the **deployable portfolio excluding the fixed Samsung Electronics 79-share core**.

## 2. Portfolio decomposition

### Fixed Core

- Samsung Electronics 79 shares
- Current working value: about KRW 15.50M
- Whole-portfolio weight: about 14.6%
- Treatment: HOLD / not part of the active reallocation sandbox

### Active Allocation Sandbox

- Total working assets: about KRW 90.41M
- Whole-portfolio weight: about 85.4%

Functional buckets:

1. **Dry Powder** = CD-rate ETF + cash + SGOV
2. **Hedge** = gold + JPY
3. **US Core/Growth** = S&P 500 + Nasdaq-100 + NVIDIA
4. **US Dividend** = US Dividend Dow Jones + SCHD
5. **Domestic Equity** = KODEX 200 + KODEX semiconductor and other adjustable Korean equity positions
6. **Satellite/Risk** = India + Rigetti + other small high-risk positions

## 3. Current working snapshot

The following values are a working snapshot from the 2026-09-07 portfolio review. They are not a live market-data record.

| Bucket | Current weight in active sandbox | Approx. value |
|---|---:|---:|
| Dry Powder | 52.0% | KRW 47.01M |
| Gold | 11.4% | KRW 10.31M |
| US Core/Growth | 13.5% | KRW 12.21M |
| US Dividend | 11.5% | KRW 10.40M |
| Domestic ETF | 6.5% | KRW 5.88M |
| India | 2.3% | KRW 2.08M |
| High-risk satellite | 1.2% | KRW 1.08M |
| JPY | 0.9% | KRW 0.81M |
| Other | 0.7% | KRW 0.63M |

## 4. Calculation correction

A previous summary described the defensive allocation as about 52%.
That figure is incomplete.

- **Dry Powder only** = CD + cash + SGOV = about **52.0%** of the active sandbox.
- **Dry Powder + gold** = about **63.4%**.

Therefore, future records must not use “52% defensive” without defining whether gold is included.
The preferred terminology is:

- Dry Powder: 52.0%
- Hedge including gold/JPY: separate bucket
- Dry Powder + gold: 63.4% (JPY excluded)

## 5. Target allocation scenarios

### Conservative

Primary objective: preserve optionality and reduce the need for immediate deployment.

- Dry Powder: 55%
- Gold: 12%
- US Core/Growth: 13%
- US Dividend: 10%
- Domestic ETF: 6%
- India: 2%
- High-risk satellite: 1%
- JPY: 1%

### Balanced — Base Case

Primary objective: retain substantial optionality while progressively increasing diversified US equity exposure.

- Dry Powder: 42%
- Gold: 10%
- US Core/Growth: 22%
- US Dividend: 11%
- Domestic ETF: 7%
- India: 2%
- High-risk satellite: 3%
- JPY: 1%
- Other: 2%

Working implication from the current snapshot:

- Reduce Dry Powder by about KRW 9.04M
- Increase US Core/Growth by about KRW 7.68M
- Keep the remaining differences small and operational rather than forcing exact one-day rebalance

The Balanced scenario is the default working target unless a later research result or risk-state rule explicitly overrides it.

### Aggressive

Primary objective: materially increase equity exposure while accepting larger drawdown risk.

- Dry Powder: 28%
- Gold: 8%
- US Core/Growth: 34%
- US Dividend: 11%
- Domestic ETF: 8%
- India: 3%
- High-risk satellite: 3%
- JPY: 2%
- Other: 3%

This scenario is not the default and should require an explicit risk-state justification.

## 6. Concentration rules

### Korea semiconductor overlap

Samsung Electronics is already a fixed 14.6% of the whole portfolio.
KODEX 200 and KODEX semiconductor contain overlapping Korean large-cap/semiconductor exposure.

Rule:

> Do not increase Korean semiconductor exposure mechanically while the fixed Samsung core remains this large, unless a separate thesis and risk budget justify the increase.

### NVIDIA overlap

NVIDIA is already indirectly held through broad US indices.

Rule:

> Treat direct NVIDIA exposure as a satellite allocation, not as an independent core bucket.

## 7. Capital deployment rule — next implementation layer

Target allocation alone is insufficient. Deployment must be conditioned on market state.

For the Balanced base case, the initial capital to be moved from Dry Powder is approximately KRW 9.0M, but it should not be deployed in one transaction by default.

Working staging rule:

- Stage 0: 0–20% of planned deployment
- Stage 1 correction: additional 20%
- Stage 2 correction: additional 25%
- Stage 3 correction: additional 25%
- Stress/panic regime: final 30%

The exact trigger conditions are to be defined separately using the project's market-stress, long-rate, FX/JPY and risk-appetite signals.

## 8. Decision hierarchy

The operating sequence is:

**Market state → risk/early-warning signals → deployable percentage → target bucket → residual Dry Powder**

Ticker selection comes after this sequence.

## 9. Lessons learned

1. Portfolio decisions should be made on functional buckets before individual tickers.
2. Fixed, non-sellable core holdings must be excluded from the active reallocation denominator.
3. Dry Powder and Hedge must remain separate concepts; otherwise defensive-capacity measurements become ambiguous.
4. Capital deployment needs a predeclared rule. Without it, the same cash reserve produces discretionary “buy now vs wait” decisions in both rising and falling markets.
5. Overlap risk must be tracked economically, not only by ticker labels.

## 10. Governance status

This document is a working baseline, not a permanent investment mandate.
Changes to target weights or deployment rules should record:

- the triggering evidence,
- the old rule,
- the new rule,
- the reason for change,
- and the expected failure mode / risk introduced.
