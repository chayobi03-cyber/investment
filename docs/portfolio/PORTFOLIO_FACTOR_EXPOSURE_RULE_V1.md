# Portfolio Factor Exposure Rule v1.2

Status: ACTIVE / POLICY DRAFT FOR VALIDATION
Effective date: 2026-10-13
Scope: Portfolio snapshot, multi-account reconciliation, risk review, entry/trim decisions, Market Monitor integration

## 1. Purpose

Portfolio risk is not measured only by security count or account-level allocation.

The canonical risk view must include:

1. direct security exposure
2. ETF look-through exposure
3. shared factor/theme exposure
4. cross-asset and macro exposure
5. concentration after overlap aggregation
6. native-currency valuation and FX conversion provenance

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

## 4. Multi-account and multi-currency ledger rules

The canonical ledger must store instrument-level positions and account-summary values as separate concepts.

- An account aggregate is a reconciliation control total, not an additional holding.
- If an account summary includes foreign-currency securities converted to the reporting currency, do not add both the summary amount and the separately itemized securities.
- Reconcile the aggregate by replacing the summary with its underlying instrument rows, or retain the summary as a control total excluded from portfolio-value sums.
- Store native-currency value and reporting-currency value separately.
- A foreign-currency amount must not be converted using a guessed, current, or unrelated FX rate.
- FX conversion requires the rate, rate timestamp, source/provenance, and conversion direction.
- If the required FX observation is unavailable, preserve the native-currency amount, mark reporting-currency value as UNKNOWN or NOT_READY, and block final cross-currency weights or combined stress-loss percentages that depend on it.
- Cash, cash-like funds, short-duration sovereign bills, and currency futures are separate instrument/risk types even when all can be described informally as liquidity reserves.

## 5. ETF look-through rule

For an ETF or fund:

factor exposure = position value × point-in-time constituent weight × constituent factor mapping

The constituent snapshot must be point-in-time appropriate to the portfolio observation date when used for historical research.

If a valid constituent snapshot is unavailable:

- do not infer or backfill the exposure silently
- mark look-through exposure as UNKNOWN
- prevent the UNKNOWN component from being treated as zero
- allow the portfolio-level risk report to remain visible, but downgrade readiness for actions that depend on the missing exposure

A recent live constituent snapshot can support a present-day diagnostic, but must not be substituted into a historical portfolio observation without an explicit stale/PIT warning.

## 6. Overlap aggregation

For each factor:

factor_value = sum(direct exposure + ETF/fund look-through exposure)

The system must report both:

- raw factor value / portfolio weight
- overlap-adjusted concentration indicator

Examples:

Samsung exposure includes direct Samsung holdings plus Samsung exposure embedded in relevant ETFs. Common and preferred share classes must remain distinct instruments but may share a parent-issuer factor.

Semiconductor exposure includes direct semiconductor holdings plus semiconductor ETF/index exposure and other identified semiconductor constituents.

US Growth / AI exposure includes direct AI/technology holdings plus look-through exposure from relevant broad/growth ETFs.

The purpose is to prevent false diversification caused by holding the same economic exposure through multiple wrappers.

### Exact security overlap vs strategy/index overlap

These must be reported separately:

- Exact security overlap: same instrument identifier held across multiple accounts. Sum positions across accounts once; do not also add account aggregate totals.
- Same ETF across accounts: sum the value of each real position under one canonical instrument, while preserving account-level sub-ledger detail.
- Index/strategy-family overlap: different products that track the same or substantially similar index/strategy (for example, a locally listed ETF and a US-listed ETF). Keep each product as a separate instrument but flag the common underlying strategy and use constituent snapshots to calculate overlap. Do not label these as the same security.
- Partial constituent overlap: broad-market and sector/growth ETFs may contain the same issuer. Add the constituent's look-through values to its issuer/factor exposure without adding the look-through value again to total portfolio assets.

LOCKED holdings are included in these calculations exactly like tradable holdings; the lock changes actionability, not exposure measurement.

## 7. Correlation is a separate layer

Factor exposure is not the same as correlation.

The system must keep these separate:

- Exposure: how much capital is linked to a factor
- Correlation: how factors historically move together
- Stress contribution: estimated portfolio loss under a defined shock

Do not collapse these into a single manually assigned score.

## 8. Risk review order

Every portfolio review should follow this order:

1. Data completeness / timestamp / provenance
2. Account-level holdings and reconciliation control totals
3. Native currency, reporting currency, and FX provenance
4. Tradability constraints / locked positions
5. Direct security concentration
6. ETF look-through
7. Exact instrument and strategy/index overlap
8. Factor aggregation
9. Cross-asset and macro overlays
10. Stress contribution
11. Available cash / dry powder
12. Action readiness

This order prevents a favorable current-market narrative from overriding exposure risk, currency uncertainty, or a hard trading constraint.

## 9. Macro and cross-asset monitoring

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

## 10. Decision gate

Factor exposure is diagnostic by default.

No fixed concentration limit is introduced in v1.2 unless separately validated by historical evidence and adopted as a risk policy.

Therefore:

- exposure breach candidate = FLAG
- missing look-through = UNKNOWN
- stale constituent data = STALE
- unsupported estimate = BLOCK
- unresolved material currency conversion = DATA_NOT_READY
- validated policy breach = ACTIONABLE
- locked position requiring risk reduction elsewhere = CONSTRAINT

This preserves the project's fail-closed principle.

A CONSTRAINT does not mean sell/trim the locked position. It means the portfolio engine must search for risk reduction outside the locked position.

## 11. Portfolio snapshot schema minimum

A portfolio snapshot should expose at least:

- as_of_timestamp
- account
- account_summary_flag
- ticker / canonical_instrument_id
- instrument_type
- native_currency
- market_value_native
- reporting_currency
- fx_rate_to_reporting_currency
- fx_as_of_timestamp
- fx_source_id
- market_value_reporting_currency
- valuation_method
- portfolio_weight
- tradability_status
- lock_reason
- lock_horizon
- direct_factor_map
- lookthrough_factor_map
- constituent_snapshot_as_of
- data_freshness
- provenance_id
- unknown_exposure_value
- total_factor_exposure
- stress_contribution_status

## 12. Required test cases

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
- T13: account summary plus itemized foreign-currency securities is not double-counted
- T14: missing FX provenance keeps native-currency positions but blocks unsupported reporting-currency totals
- T15: identical ETF held across accounts is consolidated without losing account-level traceability
- T16: same-index strategy wrappers are flagged as strategy overlap, not mislabeled as the same instrument
- T17: common constituent across multiple ETFs is counted once per actual position for assets and aggregated across wrappers only for factor exposure
- T18: constituent weights used in historical analysis match the observation's PIT date; stale or mismatched weights reduce readiness

## 13. Lesson learned from 2026-10-13 portfolio reconciliation

A portfolio total displayed in reporting currency may already include foreign-currency positions. Adding the individually listed USD holdings on top of that aggregate double-counts assets; replacing the aggregate with native-currency instrument rows avoids this error.

Cross-account exact-ETF duplication, overlapping underlying constituents, and same-index strategy overlap are related but different concepts. They must be reported separately.

Portfolio values should be reconciled in native currency first, then converted through a timestamped and provenance-backed FX layer. If FX or constituent snapshots are missing, keep the missing value explicit and do not publish a falsely precise total concentration or stress-loss ratio.

Therefore the portfolio engine must track:

account summary -> instrument -> native currency -> FX valuation -> wrapper -> constituent -> factor -> macro

and independently:

security -> tradability constraint -> allowable risk action

This rule should be reused by the Market Monitor, P0-P6 entry research, and portfolio risk engine rather than maintained as a separate manual worksheet.
