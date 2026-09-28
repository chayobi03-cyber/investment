# Scout Strategy — Historical Analog Validation 2026-09-28

Date: 2026-09-28
Status: PRELIMINARY HISTORICAL ANALOG TEST — NOT VALIDATED / NOT LIVE

## 1. Objective

Test the same Scout logic used for the 2026-09-28 Korea market review:

1. Do not enter on price weakness alone.
2. Wait for intraday stabilization:
   - no new low after the initial dislocation;
   - low-hold / stabilization;
   - recovery toward VWAP or short-term mean;
   - foreign/institutional selling pressure easing;
   - broad market not continuing to deteriorate.
3. Start with a small scout allocation.
4. Scale only after persistence and cross-axis confirmation.
5. A one-day rebound is not sufficient for scale-up.
6. If the market/asset continues to deteriorate, keep the scout small or terminate it.
7. Scout is an observation/research state and must not bypass BUY_ALLOWED / EXECUTION_ALLOWED gates.

## 2. Important data limitation

The current repository contains the contract and daily historical framework, but the available historical dataset in this execution environment does not contain a verified, PIT, Korea-wide intraday dataset with minute VWAP plus investor-flow timestamps for all historical episodes.

Therefore this run is a historical analogue test using verified daily prices and contemporaneous public reporting. It can validate the direction of the logic and identify false-start patterns, but it is NOT the final statistical intraday backtest.

Final validation requires:
- KRX intraday OHLCV/VWAP;
- PIT foreign/institution flow by timestamp;
- market breadth at the decision timestamp;
- frozen source/version metadata;
- exact entry convention and cooldown/re-arm rules.

## 3. Historical analogue results

| Episode | Initial condition | What happened after the rebound | Scout interpretation |
|---|---|---|---|
| 2022-10-04 | KOSPI rebounded from >2-year low; U.S. Treasury yields had retreated; foreign investors net bought; breadth 815 advancers vs 90 decliners; Samsung Electronics +4.14%, SK hynix +4.33% | KOSPI 2,209.38 on 10/4; 2,192.07 five sessions later (-0.78%); 2,293.61 by 10/31 (+3.81%) | Initial scout could be allowed, but scale-up should still require persistence. This episode supports cross-axis confirmation rather than price-only entry. |
| 2020-03-20 | KOSPI rebounded 7.44% after a seven-session fall on the U.S.-Korea currency-swap news | KOSPI 1,566.15 on 3/20; fell 5.34% on 3/23; then +8.85% by 3/25 and +22.24% by 4/17 | One-day rebound was a false start. Persistence rule correctly blocks immediate scale-up. |
| 2020-03-24 | KOSPI rebounded 8.60% after the 3/23 plunge; however foreigners remained net sellers for the 14th consecutive session | Strong rebound continued on 3/25, but foreign selling did not confirm the move | Price rebound alone is insufficient. Scout can remain small while flow confirmation is absent. |
| 2016-01-13 | KOSPI rebounded 1.34% as China/FX stress eased somewhat | KOSPI 1,916.28 on 1/13; 1,845.45 by 1/20 (-3.70%); 1,912.06 by 1/29 (-0.22%); 1,835.28 by 2/12 (-4.23%) | False-start pattern. Continued foreign selling / unresolved macro stress should block scale-up. |
| 2008-10-30 | KOSPI surged 11.95% after the Korea-U.S. currency-swap agreement; foreign + institutional buying supported the rebound, but intraday volatility remained extreme | 1,084.72 on 10/30; 1,181.50 by 11/5 (+8.92%); 1,092.22 by 11/6 (+0.69%); 948.69 by 11/20 (-12.54%) | Strong initial scout result but poor persistence. Demonstrates why emergency rebound days must not be promoted directly to larger size. |
| 2018-12-27 | KOSPI stabilized on Wall Street gains; individuals and foreigners net bought while institutions sold | 2,028.44 on 12/27; 1,993.70 by 1/3/2019 (-1.71%); 2,097.18 by 1/15 (+3.39%) | Another whipsaw case. Stabilization without persistent follow-through should remain Scout/Watch rather than scale immediately. |

## 4. What the analogues support

The historical cases support the following research rules:

### R1 — No scale-up on one-day reversal

A large rebound can be followed immediately by another large decline:
- 2020-03-20 -> 2020-03-23;
- 2008-10-30 -> subsequent November volatility.

Therefore:

`Rebound(1D) != Confirmation`

### R2 — Cross-axis confirmation is more informative than price alone

The cleanest analogue is 2022-10-04: yields eased, foreign buying returned, breadth broadened materially, and semiconductor leaders participated together.

### R3 — Continuing foreign selling is a veto against scale-up

The 2020-03-24 rebound occurred while foreigners remained net sellers for the 14th straight session. A strong price reaction therefore did not equal a validated permission state.

### R4 — Emergency interventions create high-volatility false confirmations

The 2008 and 2020 examples show that policy/currency/liquidity interventions can generate very large one-day reversals while the broader market remains unstable.

## 5. Application to 2026-09-28

Pre-holiday KOSPI closed at 7,080.92 after four consecutive up sessions, while foreigners were net sellers over the week and institutions were net buyers. Market volatility had eased, but the post-holiday intraday flow confirmation was not yet established at the time of the morning review.

Therefore the 2026-09-28 state remains:

`SCOUT_WAIT -> require intraday confirmation -> possible small scout -> persistence check -> scale only after confirmation`

For a candidate such as Doosan Enerbility, the historical logic does NOT permit:
- buying solely because price is lower;
- scaling after a single rebound candle;
- overriding a market-level risk block.

## 6. Final validation gate

This document does not promote the Scout layer to live operation.

Required next test:

`PIT KRX minute data
-> intraday Scout trigger reconstruction
-> 1D / 5D / 20D outcomes
-> MAE / MFE
-> false starts / misses
-> episode clustering
-> OOS
-> walk-forward
-> sensitivity
-> promotion decision
`

Minimum report:
- trigger count;
- hit rate;
- median forward return;
- worst forward return;
- MAE;
- MFE;
- 1D / 5D / 20D / 60D outcomes;
- false-positive rate;
- average lead time;
- results by regime;
- results by shock type.

## 7. Sources

- Yonhap, 2022-10-04, Seoul shares rebound from a two-year low and foreign buying returns:
  https://en.yna.co.kr/view/AEN20221004008951320
- Yonhap, 2022-10-04, opening conditions and semiconductor rebound:
  https://en.yna.co.kr/view/AEN20221004002800320
- Yonhap, 2020-03-20, KOSPI rebound after Korea-U.S. currency swap:
  https://en.yna.co.kr/view/AEN20200320008500320
- Yonhap, 2020-03-23, KOSPI falls 5.34% after the prior rebound:
  https://en.yna.co.kr/view/AEN20200323009300320
- Yonhap, 2020-03-24, KOSPI rebound while foreign selling continued:
  https://en.yna.co.kr/view/AEN20200324008251320
- Yonhap, 2016-01-13 / 2016-01-20, rebound then continued weakness:
  https://en.yna.co.kr/view/AEN20160113009200320
  https://en.yna.co.kr/view/AEN20160120006851320
- Yonhap, 2008-10-30, currency-swap rebound and extreme intraday volatility:
  https://www.yna.co.kr/view/AKR20081030161400008
- Yonhap, 2018-12-27 / 2019-01-03, post-holiday stabilization followed by renewed weakness:
  https://newspim.com/news/view/20181227000593
  https://www.yna.co.kr/view/AKR20190103123600008

## 8. Lesson learned

The Scout layer should be treated as an experimental permission state, not a reduced-size buy signal.

The strongest reusable rule from this test is:

`price stabilization -> flow confirmation -> market confirmation -> persistence -> scale`

not

`price rebound -> buy`.

