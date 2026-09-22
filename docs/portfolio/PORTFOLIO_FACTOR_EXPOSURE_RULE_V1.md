# Portfolio Factor Exposure Rule v1.1

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

## 2. Locked / Restricted Holdings

Some holdings are strategically non-tradable for a multi-year period.

For such holdings:

- tradability_status = LOCKED
- no automated trim/sell recommendation may be generated
- the holding remains fully included in factor and stress exposure
- risk reduction must be sought through other holdings, new capital, cash deployment, hedges, or portfolio-level allocation
- account-level concentration may therefore remain structurally high without being treated as an execution error
- the lock period and reason must be recorded as provenance-backed portfolio constraints when available

A LOCKED holding is therefore:

risk-bearing + non-tradable

It is not equivalent to cash, a hedge, or a neutral asset.

For the current portfolio review, the Samsung Electronics position identified by the user is treated as LOCKED / multi-year.

## 3. Canonical exposure taxonomy

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

## 4. Look-through rule

For an ETF or fund:

factor exposure = direct ETF value × current/historical constituent weight × constituent factor mapping

The constituent snapshot must be point-in-time appropriate to the portfolio observation date when used for historical research.

If a valid constituent snapshot is unavailable:

- do not infer or backfill the exposure silently
- mark look-through exposure as UNKNOWN
- prevent the UNKNOWN component from being treated as zero
- allow the portfolio-level risk report to remain visible, but downgrade readiness for actions that depend on the missing exposure

## 5. Overlap aggregation

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

LOCKED holdings are included in these calculations exactly like tradable holdings; the lock changes actionability, not exposure measurement.

## 6. Correlation is a separate layer

Factor exposure is not the same as correlation.

The system must keep these separate:

- Exposure: how much capital is linked to a factor
- Correlation: how factors historically move together
- Stress contribution: estimated portfolio loss under a defined shock

Do not collapse these into a single manually assigned score.

## 7. Risk review order

Every portfolio review should follow this order:

1. Data completeness / timestamp / provenance
2. Account-level holdings
3. Tradability constraints / locked positions
4. Direct security concentration
5. ETF look-through
6. Factor aggregation
7. Cross-asset and macro overlays
8. Stress contribution
9. Available cash / dry powder
10. Action readiness

This order prevents a favorable current-market narrative from overriding exposure risk or a hard trading constraint.

## 8. Macro and cross-asset monitoring

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

## 9. Decision gate

Factor exposure is diagnostic by default.

No fixed concentration limit is introduced in v1.1 unless separately validated by historical evidence and adopted as a risk policy.

Therefore:

- exposure breach candidate = FLAG
- missing look-through = UNKNOWN
- stale constituent data = STALE
- unsupported estimate = BLOCK
- validated policy breach = ACTIONABLE
- locked position requiring risk reduction elsewhere = CONSTRAINT

This preserves the project's fail-closed principle.

A CONSTRAINT does not mean sell/trim the locked position. It means the portfolio engine must search for risk reduction outside the locked position.

## 10. Portfolio snapshot schema minimum

A portfolio snapshot should expose at least:

- as_of_timestamp
- account
- ticker
- instrument_type
- market_value
- portfolio_weight
- tradability_status
- lock_reason
- lock_horizon
- direct_factor_map
- lookthrough_factor_map
- data_freshness
- provenance_id
- unknown_exposure_value
- total_factor_exposure
- stress_contribution_status

## 11. Required test cases

At minimum, regression tests should cover:

- T1: direct Samsung + Samsung-containing ETF aggregation
- T2: direct semiconductor + semiconductor ETF aggregation
- T3: Nasdaq ETF + direct AI stock overlap
- T4: missing ETF constituent data -> UNKNOWN, not zero
- T5: stale constituent data -> STALE / action blocked
- T6: same security held across multiple accounts -> one consolidated exposure
- T7: factor exposure differs from ticker-count intuition
- T8: portfolio action remains blocked when a material required exposure is UNKNOWN
- T9: LOCKED Samsung cannot trigger automated sell/trim action
- T10: LOCKED Samsung remains fully included in factor/stress exposure
- T11: concentration constraint for a LOCKED holding is resolved through other positions/cash, not by forced liquidation
- T12: lock metadata missing -> trading action requiring the constraint is BLOCKED until status is established

## 12. Lesson learned from 2026-09-22 portfolio review

The practical unit of portfolio risk is not the number of tickers.

A portfolio can appear diversified across accounts and instruments while retaining a concentrated common-factor exposure.

In addition, tradability and exposure are separate dimensions. A position may be a large source of risk while being intentionally unavailable for sale for a multi-year period.

Therefore the portfolio engine must track:

security -> wrapper -> constituent -> factor -> macro

and independently:

security -> tradability constraint -> allowable risk action

This rule should be reused by the Market Monitor, P0-P6 entry research, and portfolio risk engine rather than maintained as a separate manual worksheet.
