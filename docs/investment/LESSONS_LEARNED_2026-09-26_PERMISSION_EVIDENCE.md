# Lesson Learned — 2026-09-26 Permission Evidence

## Findings

1. Historical permission validation must never depend on the machine's current wall-clock time. Historical datasets are evaluated against an explicit decision/as-of cutoff.
2. Permission evidence is a separate control layer from asset signals. Evidence availability must not rewrite frozen entry thresholds.
3. A multi-asset permission layer needs an explicit evidence registry covering cross-asset spot, macro/liquidity, derivatives, regulation/market structure, and geopolitical transmission.
4. Economic and event data require source-specific availability semantics. An observation timestamp is not automatically a valid historical availability timestamp.
5. Derivatives provider splicing must be explicit. Archive/provider transitions require provenance and an overlap policy; silent splicing is forbidden.
6. Source structure alone is not historical validation. The registry remains SCHEMA_DEFINED_NOT_VALIDATED until real observations, available_at, provenance and coverage are empirically checked.

## Rule Revisions

- Historical validators must use explicit as_of / decision clocks.
- BUY_ALLOWED=false and EXECUTION_ALLOWED=false remain hard locks until promotion.
- Missing or unverified permission evidence maps to DATA_NOT_READY.
- Permission is an overlay; it does not mutate asset-specific signal thresholds.
- Provider changes require explicit provenance and overlap validation.
- The evidence registry status must not be promoted by configuration alone.

## Next Boundary

Acquire and normalize real historical evidence for:
- macro/liquidity
- BTC/ETH/SOL spot cross-asset
- derivatives
- regulation/market structure
- geopolitical transmission

Then run PIT coverage, provenance, chronology, and cross-provider validation before connecting permission history to P0-P6/OOS/walk-forward evaluation.

## Source Basis

The registry design is aligned with documented source characteristics: FRED exposes daily DGS10, DFII10 and DCOILWTICO series; Binance documents historical perpetual funding-rate retrieval; Coin Metrics documents funding-rate catalog/time-range metadata and authenticated access; SEC maintains official crypto press-release and enforcement archives.
