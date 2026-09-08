# Stock Data Source Registry — 2026-09-08

## Status legend

- A = primary/official source suitable for production if access terms and credentials are satisfied
- B = official/authoritative source but licensing, delay, or coverage constraints require review
- C = fallback/research source only

## 1. Korea

| Data | Preferred source | Grade | Connection / caveat |
|---|---|---|---|
| KRX stock OHLCV, volume | KRX Data Marketplace / KRX Open API | A/B | Official. Open API requires authentication key and service application/approval. EOD and real-time distribution have separate access/terms. |
| KRX market breadth | Derived from KRX listed-issue prices + market summary | A/B | Build advancing/declining, % above MA, new highs/lows from the issue-level dataset rather than using a third-party breadth series. Universe must be frozen. |
| Sector price / index | KRX indices + industry classification | A/B | Use KRX sector/index data and issue industry classification. Relative strength is computed internally. |
| Foreign / institutional flow | KRX trading by investor / individual issue | A/B | Official investor-type data. Store raw net flow and rolling persistence separately. |
| Foreign ownership | KRX foreign ownership by issue | A/B | Use as ownership state, never as a substitute for daily flow. |
| Corporate financials | OpenDART | A | Official FSS filing data and XBRL-based financial statements. API authentication key required. |
| Company events / filings | DART / OpenDART | A | Use point-in-time filing/reception timestamps. Event classification must be deterministic where possible. |
| Korean rates / macro | Bank of Korea ECOS / official BOK releases | A/B | Prefer official series and publication timestamps. API access and series mapping must be verified during implementation. |
| USD/KRW | BOK/official Korean FX source; fallback FRED H.10 DEXKOUS | A/B | FRED DEXKOUS is daily noon New York buying rate and is not identical to the Korean market close. Session alignment must be explicit. |

KRX explicitly lists stock price, trading by investor, foreign ownership, industry classification and related market data in its Data Marketplace. KRX also provides an Open API service, while some real-time/distribution data are subject to separate access arrangements.

## 2. United States / Global

| Data | Preferred source | Grade | Connection / caveat |
|---|---|---|---|
| S&P 500 | S&P Dow Jones Indices; FRED SP500 for research history | A/B | Official index publisher. FRED provides daily close history sourced from S&P Dow Jones Indices but carries S&P usage restrictions. |
| SOX | Nasdaq PHLX Semiconductor Sector Index | A/B | Official Nasdaq index methodology and index page. Programmatic historical use and redistribution terms must be checked. |
| VIX | Cboe; FRED VIXCLS for history | A/B | Cboe is primary. FRED VIXCLS is sourced from Cboe and is daily close. |
| VIX3M | Cboe volatility index family | A/B | Official Cboe source. Confirm accessible historical feed before production; do not substitute VIX silently. |
| HY OAS | ICE BofA via FRED BAMLH0A0HYM2 | B | Authoritative. FRED currently provides daily close series; ICE/FRED data-availability history and licensing need review for long backtests. |
| U.S. 2Y / 10Y | U.S. Treasury / Federal Reserve; FRED DGS2/DGS10 | A | Daily constant-maturity yields. Publication timing and market close conventions must be retained. |
| DXY / broad dollar | Federal Reserve H.10 / FRED DTWEXBGS | A/B | Broad trade-weighted dollar index is preferable for a broad macro factor; a commercial DXY feed can be added separately if required. |
| Gold | World Gold Council / LBMA-linked benchmark data | A/B | World Gold Council exposes gold-price datasets; historical LBMA access may have licensing limitations. |
| WTI | U.S. EIA; FRED DCOILWTICO | A/B | EIA is primary. FRED provides the EIA-derived daily WTI Cushing spot series. |
| BTC | Exchange/market-data provider with reproducible timestamped OHLCV; Binance/Coinbase as candidate feeds | B/C | Crypto trades 24/7, so a daily cutoff must be defined. Venue selection must be frozen before backtest. |

## 3. Why the source hierarchy matters

The production pipeline should distinguish:

`PRIMARY_OFFICIAL → AUTHORITATIVE_MIRROR → RESEARCH_FALLBACK`

A fallback source may be used to validate logic or fill a temporarily unavailable feed, but it must never silently overwrite the official source in the production dataset.

## 4. Point-in-time requirements

Every row must retain:

`source, series/ticker, observation_time, available_at, timezone, market_session, raw_value, revision_flag, source_version`

Financial statement facts additionally need:

`filing_date, report_period, fiscal_period, accession/reception number`

A quarterly result belongs in the investment engine only after its filing/publication timestamp. Backtests must not use the later revised dataset snapshot when that revision was not available at the decision time.

## 5. Initial implementation priority

1. KRX EOD issue price + volume
2. KRX investor flow by issue
3. KRX industry/sector classification + sector indices
4. OpenDART financial statements and filings
5. FRED/Cboe/S&P/Nasdaq macro-market layer
6. BOK/FX layer
7. gold/WTI/BTC overlay
8. Catalyst parser / event state

The initial ranking universe should remain the ten specified large-cap names until this pipeline is reproducible.
