# 08:00 Market Snapshot Specification v1

## Purpose

Capture the information available around 08:00 KST before the Korean cash market opens, then link it to the 09:00 open and subsequent market outcome.

This is an observation/decision-support layer, not an automatic trading system.

## Fixed observation windows

- 08:00 KST: primary pre-open snapshot
- 08:30 KST: refresh
- 08:50 KST: final pre-open refresh
- 09:00 KST: Korean cash-market open observation
- 09:00-10:00 KST: outcome window for initial validation

## Required fields

### Korea
- KOSPI 200 futures
- USD/KRW
- KOSPI/KOSPI200 pre-open indication when available

### Global risk
- S&P 500 futures
- Nasdaq 100 futures
- Nikkei 225 futures / current Nikkei reference
- Hang Seng / China reference

### Rates / commodities / risk assets
- US 10Y Treasury yield
- WTI crude oil
- Gold
- BTC/USD

### Semiconductor watchlist
- NVDA
- AVGO
- TSM
- AMD
- MU
- SMCI

## Data-quality contract

Every observation must carry:

- `observed_at_utc`
- `observed_at_kst`
- `source`
- `instrument`
- `value`
- `unit`
- `data_status`: `REALTIME`, `DELAYED`, `SNAPSHOT`, `STALE`, or `MISSING`
- `delay_note`

No missing or stale field may be silently treated as real-time.

## Derived signals

At 08:00 calculate:

1. Global risk direction
2. Korea opening-pressure direction
3. Rate-pressure direction
4. Oil inflation shock level
5. Safe-haven confirmation
6. Semiconductor relative-strength pressure

The derived signal is advisory and must not override the raw observation.

## Stress Convergence linkage

The snapshot should feed the existing chain:

Geopolitics -> Energy -> Inflation -> Fed -> Rates -> Credit

and record the following decision fields:

- Threshold
- Trigger
- Falsifier
- Action Level
- Evidence status

## Outcome fields at 09:00+

Store:

- opening price / opening return
- 09:30 return
- 10:00 return
- high/low excursion during 09:00-10:00
- direction match versus 08:00 signal
- false positive / false negative label when benchmark criteria are defined

## Fail-closed rule

If core pre-open inputs are missing, stale, or provenance-ambiguous, the system must lower confidence and must not represent the snapshot as a complete real-time market state.

## Implementation priority

1. Snapshot schema
2. Source adapter
3. Persistent storage
4. Validation tests
5. 08:00/08:30/08:50 scheduler
6. 09:00 outcome capture
7. Backtest of signal usefulness
