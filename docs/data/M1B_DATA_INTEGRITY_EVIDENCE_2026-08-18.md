# M1-B Data Integrity Evidence — 2026-08-18

## Scope

This record is an evidence-oriented remediation note for the two explicit blockers carried from the prior session: the SPY February 2026 low of `69.005` and the BIL price discontinuity around November 2017.

## SPY — February 2026 suspicious low

Repository fixture currently records:

- timestamp: `2026-02`
- open: `689.58`
- high: `697.14`
- low: `69.005`
- close: `685.99`

The fixture is synthetic and intentionally models the suspicious source observation; it is not treated as market-performance evidence.

Independent market-history checks show that the `697.14` high is a real February 2026 observation, but the `69.005` low is not consistent with neighboring daily observations. Yahoo Finance reports February 2, 2026 as open `689.58`, high `696.93`, low `689.42`, close `695.41`; February 5 is `680.94 / 683.69 / 675.79 / 677.62`; February 11 is `696.39 / 697.14 / 689.18 / 691.96`. Financecharts reports the same neighboring observations. ChartExchange separately exposes the exact `69.005` value on February 2, confirming that the anomaly is present in at least one historical-data feed rather than being invented by the repository.

### M1-B classification

`69.005` is classified as `REVIEW` / **BLOCKING FOR HISTORICAL INTEGRATION** until the source-level provenance is repaired or the observation is explicitly quarantined and replaced by an independently verified value.

Required rule: do not silently delete or overwrite the raw observation. Preserve the source record, quarantine it from return calculations, and record the independent replacement evidence and transformation history.

## BIL — November 2017 price discontinuity

Independent SEC evidence states that a scheduled reverse stock split for BIL was effective November 30, 2017. State Street's contemporaneous announcement specifies a `1:2` reverse split, increasing the indicative share price from about `$45.74` to `$91.48` while reducing shares outstanding proportionally; aggregate market value was not impacted by the split.

Therefore, a step change around November 30, 2017 is a **corporate-action event**, not automatically a market loss.

### M1-B classification

BIL historical series must carry an explicit corporate-action record:

- effective date: `2017-11-30`
- action: reverse split
- ratio: `1:2`
- treatment: use a consistently split-adjusted price basis for continuity, or apply an explicit pre/post transformation before calculating returns
- dividends/distributions remain separate from split adjustment unless the selected vendor's adjusted-close definition explicitly includes them

## Critical series provenance requirements

Before M1-B can become GREEN, each baseline series (SPY, IEF, TLT, GLD, BIL) must record:

1. source/vendor and dataset identifier
2. retrieval timestamp
3. observation timestamp and timezone/frequency
4. raw vs adjusted status
5. corporate-action treatment
6. dividend/distribution treatment
7. point-in-time availability rule
8. missing and duplicate checks
9. source-to-source anomaly comparison
10. immutable raw evidence plus deterministic transformation history

## Gate decision

Current state remains `M1-B = YELLOW / BLOCKING`.

The remediation is sufficient to establish the root cause of the two known findings, but it is **not yet sufficient to certify all five critical historical series**. Historical backtesting remains blocked.

## External evidence references

- Yahoo Finance SPY historical prices: February 2026 daily OHLC confirms neighboring values around the disputed observation.
- Financecharts SPY history: corroborates February 2026 daily OHLC.
- ChartExchange SPY history: exposes the `69.005` value on February 2, 2026, demonstrating feed-level disagreement that must be preserved as provenance evidence.
- SEC filing dated November 28, 2017: documents the scheduled BIL reverse split effective November 30, 2017.
- State Street announcement dated November 15, 2017: specifies BIL `1:2` reverse split and estimated post-split price.
