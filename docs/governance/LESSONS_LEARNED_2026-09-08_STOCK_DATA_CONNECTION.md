# Lessons Learned — Stock Data Connection / Score Separation — 2026-09-08

## Result Summary

The first data-connection pass confirms that the architecture can be grounded in official/authoritative sources, but production access differs by dataset. Korea equity price, investor flow, foreign ownership and industry classification are available from KRX Data Marketplace/Open API subject to authentication/access terms. Korean corporate financials and filings are available through OpenDART. Global market inputs can be sourced from official index publishers and authoritative public series such as Cboe/FRED, Nasdaq, S&P Dow Jones Indices, U.S. Treasury/Federal Reserve, EIA and World Gold Council.

## Newly Confirmed Problems

1. `Market Regime` must not be included as a raw Stock Score factor while also being included in BuyStrength's Market component. Doing both double-counts market conditions.
2. Trend/Momentum, Relative Strength/Sector Strength, and Supply/Demand/Institutional-foreign Flow contain potential correlated information. The engine needs a factor-level correlation audit before final weights are accepted.
3. Current global public series do not all update on the same local date/time. Data freshness and session alignment are part of the dataset contract, not a display issue.
4. KRX official data access is not equivalent to unrestricted public scraping; authentication, API service approval, licensing and distribution conditions must be recorded in the data connector configuration.

## Rule Changes / Reusable Rules

- `StockScore = company/stock evidence only.` Market regime is an external environment variable.
- `BuyStrength` combines stock opportunity, sector environment, market permission and catalyst; Risk remains a separate alarm/constraint.
- Every feature keeps `available_at`, and the engine uses only rows with `available_at <= decision_time`.
- No ranking is published when critical inputs are missing and no pre-approved missing-data policy applies.
- Fallback sources must be explicitly labeled and cannot silently replace the primary source.
- Baseline weights remain frozen until OOS validation.

## Next Session

Connect the first reproducible EOD dataset for the ten-stock universe, then calculate Long/Medium/Short factors without optimization. The first valid deliverable should be a data-quality report plus raw factor values, not a hand-tuned top-10 ranking.

## Git Decision

This session changes the canonical architecture and therefore requires a repository commit.
