# 2026-10-15 11:42 KST Intraday Market Review

## 1. Run status

- **Workflow:** [Market Check Workflow V1](MARKET_CHECK_WORKFLOW_V1.md) (`market-check-workflow-v1.0`)
- **run_asof_kst:** 2026-10-15T11:42:44+09:00
- **session_phase:** INTRADAY
- **market_date:** 2026-10-15
- **Run ID:** `mc-20261015-1142-intraday-web`
- **DATA_QUALITY:** AMBER overall; breadth and live-quote groups `DATA_NOT_READY`
- **Decision controls:** `BUY_ALLOWED=false`, `EXECUTION_ALLOWED=false`, `PROMOTION=DISABLED`, `DECISION_MODE=RESEARCH_ONLY`, `REGIME_ENGINE=UNCONFIRMED`
- **Persistence:** `PERSISTENCE=NOT_RUN`. This Markdown note is not a Historical DB transaction; `record_live_market_review.py` was not run.
- **Retrieval limits:** Market-data endpoints (Naver, Yahoo) were refused by the proxy (403) and article pages failed DNS resolution. All values below are press-reported figures surfaced through web search results; no timestamped live quote was verified directly.

## 2. One-line conclusion

**Extreme risk-off (qualitative; calibrated regime engine not run).** KOSPI is down about 7.5–7.9% intraday with a sell-side sidecar triggered and the session low within about 6 points of the 8% circuit-breaker threshold (~5,528). The decline is led by semiconductor mega-caps and foreign net selling. No new entry; watch only.

## 3. Market-state vector

| # | Dimension | Observation (time) | State | Quality |
|---|---|---|---|---|
| 1 | Korean index structure | KOSPI 5,558.75 (-450.06, -7.49%) at 11:10 KST; intraday low 5,534.24 (-7.90%); open 5,673.01 (-5.59%); KOSDAQ 765.22 (-7.12%) at 11:10 — [NewsPim](https://www.newspim.com/news/view/20261015000463), [LCNews](https://www.lcnews.co.kr/news/articleView.html?idxno=209652) | NEGATIVE | AMBER — press-quoted, single source per value |
| 2 | Breadth | Exchange-wide advance/decline not retrieved | UNCONFIRMED | DATA_NOT_READY |
| 3 | Foreign/institutional flows | Provisional: foreign -₩285.6B at 09:02, below -₩920B around 09:30; institution about +₩810B. Finalized 2026-10-14: foreign -₩1.1755T, institution +₩802.1B, individual -₩314.9B — [Pinpoint News](https://www.pinpointnews.co.kr/news/articleView.html?idxno=495368), [FN Today](https://www.fntoday.co.kr/news/articleView.html?idxno=395343) | NEGATIVE | AMBER — intraday provisional, timestamps differ |
| 4 | Domestic leaders / RS | Samsung Electronics ₩210,000 (-9.48%), RS vs KOSPI -1.99pp; SK hynix ₩1,258,000 (-11.35%), RS -3.86pp (same 11:10 session-to-date horizon). The two names account for ~64% of KOSPI market-cap loss — [NewsPim](https://www.newspim.com/news/view/20261015000463) | NEGATIVE | AMBER |
| 5 | Rates/liquidity | US 10Y ~5.278% (+6bp) on 2026-10-14 after CPI; renewed Fed hike pricing for October — [TheStreet](https://www.thestreet.com/stock-market-today/stock-market-today-dow-jones-sp-500-nasdaq-updates-oct-14-2026). US 2Y not retrieved | NEGATIVE | AMBER |
| 6 | FX | USD/KRW 1,341.1–1,346.5 around 09:00–09:10 KST (sources conflict) — [Dailian](https://www.dailian.co.kr/news/view/1701711/%EC%9B%90%EB%8B%AC%EB%9F%AC-%ED%99%98%EC%9C%A8-%EC%98%A4%EC%A0%84-9%EC%8B%9C%EA%B2%BD-13421%EC%9B%90-2026), [NewsPim FX preview](https://www.newspim.com/news/view/20261015000089). No 11:00+ quote | MIXED — limited FX reaction relative to equity drop | AMBER — stale for run time |
| 7 | Energy/commodities | Brent ~$104–108, WTI ~$94–95, gold ~$4,160/oz — [Business Standard](https://www.business-standard.com/markets/news/stock-market-live-october-15-bse-sensex-today-nifty50-gift-nifty-crude-oil-prices-q2-results-ipo-today-126101500089_1.html), [TheStreet](https://www.thestreet.com/stock-market-today/stock-market-today-dow-jones-sp-500-nasdaq-updates-oct-14-2026) | NEGATIVE — elevated oil keeps inflation channel open | AMBER — conflicting sources/timestamps |
| 8 | Overseas equity/semis | 2026-10-14: S&P 500 ~-1.1%, Nasdaq ~-1.9%, Dow ~-0.09%, Russell 2000 ~-1.9%, SOX -4.3% (sixth straight decline), NVDA ~-3.2%. 2026-10-15: Nikkei ~-4.6% to -5% — [TheStreet](https://www.thestreet.com/stock-market-today/stock-market-today-dow-jones-sp-500-nasdaq-updates-oct-14-2026), [Kaohoon](https://www.kaohooninternational.com/markets/592711). US futures reported slightly higher, timestamp unverified | NEGATIVE | AMBER |
| 9 | Confirmed catalysts | US September CPI above expectations (2026-10-14), raising Fed hike odds. "AI investment profitability" and "Chinese memory catch-up" are press interpretations, not confirmed events | NEGATIVE | AMBER — CPI detail values conflict across sources |
| 10 | D/W/M structure | See section 5 | NEGATIVE | AMBER |

## 4. What is driving the move

- **Observed:** hotter-than-expected US CPI → higher US yields and a 4.3% SOX decline → Korean semiconductor mega-caps sharply underperforming → heavy foreign net selling (seventh consecutive selling session reported).
- **Plausible mechanism:** oil-driven inflation → Fed hike risk → higher discount rates → pressure on long-duration semiconductor valuations. This continues the causal chain recorded in the [2026-10-13 pre-open note](2026-10-13_0737_preopen_research.md).
- **Alternative explanation:** KOSPI's decline (-7.5%) exceeds SOX (-4.3%) and the Nikkei (~-4.6%), consistent with index concentration in semiconductors and possible forced deleveraging (margin/credit liquidation). Unverified: credit-balance and forced-sale data were not retrieved.

## 5. Key levels and D/W/M context (provisional references)

- **Circuit-breaker threshold:** ~5,528.1 (2026-10-14 close 6,008.81 × 0.92). The 5,534.24 low is about 6 points above it.
- **Downside references:** 5,534.24 intraday low; 5,500 round number (not a verified support zone).
- **Overhead references:** ~5,673 (today's open); 6,000–6,009 (prior close).
- **Drawdown:** about -12.9% from the 2026-10-12 close of 6,384.24; about -39% from the 9,114.55 record close; October decline reported near 18–20%. The 2026-10-02 close is reported as both 6,941.39 and 7,003.74 — conflict unresolved.
- **D/W/M:** Daily RED (gap-down extension of a multi-session decline); Weekly RED; Monthly RED. Close-to-close structure assessment only; no moving-average/oscillator scan was run.

## 6. Scenario gates

1. **Continuation/downside:** break of ~5,528 (circuit breaker) or a close at a new low, with foreign selling widening and semiconductor RS still negative. Invalidated by a close above the low with narrowing foreign selling.
2. **Stabilization attempt:** 5,534 holds and the close reclaims the ~5,673 open while foreign net selling stops growing. Watch-only; not a buy signal.
3. **Recovery confirmation:** 6,000 reclaimed and held across multiple sessions with improving breadth, foreign flows and semiconductor RS, and no renewed US rates/oil shock. Re-evaluate candidates only; no automatic BUY.

Missing for all scenarios: exchange-wide breadth, live 5m/15m returns, KOSPI 200 futures flows.

## 7. Action / permissions

**WAIT.** A sharp decline is not entry evidence. No averaging down or sell inference is drawn from this review. Stock-level consideration requires the separate D/W/M checklist. `BUY_ALLOWED=false`, `EXECUTION_ALLOWED=false`.

## 8. Missing data and caveats

- No direct live quote: market-data endpoints returned proxy 403 and article fetches failed DNS. All numbers are press-quoted via search results.
- Not retrieved: live quote at run time, 5m/15m returns, exchange-wide breadth, KOSPI 200, futures flows, USD/KRW after 09:10, US 2Y.
- Conflicts retained: foreign flow figures at different times; USD/KRW at 09:00; CPI headline/core values; oil levels; 2026-10-02 KOSPI close.
- `scripts/market_monitor/poll.py` output was not used ([Issue #27](https://github.com/chayobi03-cyber/investment/issues/27) still open).

## 9. HOTL checkpoint

- **Prior hypothesis scored:** the 2026-10-13 pre-open note (risk-off; continuation if 6,368.49 breaks). Subsequent evidence — 6,008.81 close on 2026-10-14 and today's 5,5xx trade — is consistent. **Provisional `HIT`**; the 2026-10-13 close and its 09:30/10:00 checkpoints were not retrieved, so the record is not fully evaluable.
- **Hypothesis at this timestamp:** risk-off persists into the close; a stabilization attempt requires holding 5,534 and reclaiming ~5,673.
- **Next run compares:** circuit-breaker trigger (yes/no), close and high/low range, finalized foreign/institution flows, exchange-wide breadth, Samsung Electronics/SK hynix RS vs KOSPI at the close, USD/KRW close.

## 10. Record receipt

Not persisted to Historical DB. No receipt or manifest exists for run `mc-20261015-1142-intraday-web`.

## Sources

1. [NewsPim — KOSPI 11:10 level, leaders, KOSDAQ](https://www.newspim.com/news/view/20261015000463)
2. [LCNews — KOSPI open 5,673.01](https://www.lcnews.co.kr/news/articleView.html?idxno=209652)
3. [Aju News — sidecar triggered](https://www.ajunews.com/view/20261015094214465)
4. [News1 — early-session KOSPI](https://www.news1.kr/finance/market-exr/6320675)
5. [FN Today — intraday foreign/institution flow](https://www.fntoday.co.kr/news/articleView.html?idxno=395343)
6. [Pinpoint News — 2026-10-14 flows](https://www.pinpointnews.co.kr/news/articleView.html?idxno=495368)
7. [Korea Report — 2026-10-14 close](https://www.koreareport.co.kr/news/articleView.html?idxno=53646)
8. [Junggi Economy — 2026-10-14 close](https://www.junggi.co.kr/news/articleView.html?idxno=38086)
9. [Dailian — USD/KRW ~09:00](https://www.dailian.co.kr/news/view/1701711/%EC%9B%90%EB%8B%AC%EB%9F%AC-%ED%99%98%EC%9C%A8-%EC%98%A4%EC%A0%84-9%EC%8B%9C%EA%B2%BD-13421%EC%9B%90-2026)
10. [NewsPim — USD/KRW morning preview](https://www.newspim.com/news/view/20261015000089)
11. [TheStreet — US close 2026-10-14, yields, oil](https://www.thestreet.com/stock-market-today/stock-market-today-dow-jones-sp-500-nasdaq-updates-oct-14-2026)
12. [Yahoo Finance — US intraday 2026-10-14](https://finance.yahoo.com/markets/stocks/articles/stock-market-today-oct-14-135249729.html)
13. [Tickeron — NVDA move](https://tickeron.com/blogs/why-is-nvidia-nvda-stock-down-3-56-today-19288)
14. [Kaohoon — Asia-Pacific selloff](https://www.kaohooninternational.com/markets/592711)
15. [Business Standard — Asia live, oil, gold](https://www.business-standard.com/markets/news/stock-market-live-october-15-bse-sensex-today-nifty50-gift-nifty-crude-oil-prices-q2-results-ipo-today-126101500089_1.html)
