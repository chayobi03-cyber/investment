# Portfolio Factor Exposure Rule v1.0

Status: ACTIVE / POLICY DRAFT FOR VALIDATION
Effective date: 2026-09-22
Scope: Portfolio snapshot, risk review, entry/trim decisions, Market Monitor integration

## 1. Purpose

Portfolio risk is not measured only by security count or account-level allocation.

The canonical risk view must include:

1. direct security exposure
2. ETF look-through exposure
3. shared factor/theme exposure
4. cross-asset and macro exposure
5. concentration after overlap aggregation

The system must prefer factor exposure over simple ticker count when the two views disagree.

## 2. Canonical exposure taxonomy

Each holding must be mapped to one or more exposure buckets.

Initial taxonomy:

- Samsung
- Korean Semiconductor
- US Growth / AI
- US Broad Equity
- US Dividend
- Gold
- Cash / Cash-like
- Short-duration Treasury
- FX / JPY
- Energy / Commodity sensitivity
- Geopolitical sensitivity
- Other / Unclassified

A holding may belong to multiple buckets. Exposure weights must therefore support fractional allocation rather than forcing one exclusive category.

## 3. Look-through rule

For an ETF or fund:

factor exposure = direct ETF value × current/historical constituent weight × constituent factor mapping

The constituent snapshot must be point-in-time appropriate to the portfolio observation date when used for historical research.

If a valid constituent snapshot is unavailable:

- do not infer or backfill the exposure silently
- mark look-through exposure as UNKNOWN
- prevent the UNKNOWN component from being treated as zero
- allow the portfolio-level risk report to remain visible, but downgrade readiness for actions that depend on the missing exposure

## 4. Overlap aggregation

For each factor:

factor_value = sum(direct exposure + look-through exposure)

The system must report both:

- raw factor value / portfolio weight
- overlap-adjusted concentration indicator

Examples:

Samsung exposure includes direct Samsung holdings plus Samsung exposure embedded in relevant ETFs.

Semiconductor exposure includes direct semiconductor holdings plus semiconductor ETF/index exposure and other identified semiconductor constituents.

US Growth / AI exposure includes direct AI/technology holdings plus look-through exposure from relevant broad/growth ETFs.

The purpose is to prevent false diversification caused by holding the same economic exposure through multiple wrappers.

## 5. Correlation is a separate layer

Factor exposure is not the same as correlation.

The system must keep these separate:

- Exposure: how much capital is linked to a factor
- Correlation: how factors historically move together
- Stress contribution: estimated portfolio loss under a defined shock

Do not collapse these into a single manually assigned score.

## 6. Risk review order

Every portfolio review should follow this order:

1. Data completeness / timestamp / provenance
2. Account-level holdings
3. Direct security concentration
4. ETF look-through
5. Factor aggregation
6. Cross-asset and macro overlays
7. Stress contribution
8. Available cash / dry powder
9. Action readiness

This order prevents a favorable current-market narrative from overriding exposure risk.

## 7. Macro and cross-asset monitoring

The factor layer should link to the Market Monitor variables:

- Trend
- Breadth / leadership
- Volatility / risk
- Rates / liquidity
- USD/KRW
- JPY/KRW or relevant JPY proxy
- WTI / Brent
- Gold
- Geopolitical stress
- semiconductor relative strength

These variables are monitoring inputs, not automatic buy/sell signals.

## 8. Decision gate

Factor exposure is diagnostic by default.

No fixed concentration limit is introduced in v1.0 unless separately validated by historical evidence and adopted as a risk policy.

Therefore:

- exposure breach candidate = FLAG
- missing look-through = UNKNOWN
- stale constituent data = STALE
- unsupported estimate = BLOCK
- validated policy breach = ACTIONABLE

This preserves the project's fail-closed principle.

## 9. Portfolio snapshot schema minimum

A portfolio snapshot should expose at least:

- as_of_timestamp
- account
- ticker
- instrument_type
- market_value
- portfolio_weight
- direct_factor_map
- lookthrough_factor_map
- data_freshness
- provenance_id
- unknown_exposure_value
- total_factor_exposure
- stress_contribution_status

## 10. Required test cases

At minimum, regression tests should cover:

- T1: direct Samsung + Samsung-containing ETF aggregation
- T2: direct semiconductor + semiconductor ETF aggregation
- T3: Nasdaq ETF + direct AI stock overlap
- T4: missing ETF constituent data -> UNKNOWN, not zero
- T5: stale constituent data -> STALE / action blocked
- T6: same security held across multiple accounts -> one consolidated exposure
- T7: factor exposure differs from ticker-count intuition
- T8: portfolio action remains blocked when a material required exposure is UNKNOWN

## 11. Lesson learned from 2026-09-22 portfolio review

The practical unit of portfolio risk is not the number of tickers.

A portfolio can appear diversified across accounts and instruments while retaining a concentrated common-factor exposure.

Therefore the next portfolio-engine revision should treat:

security -> wrapper -> constituent -> factor -> macro

as a traceable exposure chain.

This rule should be reused by the Market Monitor, P0-P6 entry research, and portfolio risk engine rather than maintained as a separate manual worksheet.
