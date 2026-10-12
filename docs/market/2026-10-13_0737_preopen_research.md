# 2026-10-13 07:37 KST Pre-open Market Review

## Record status

- **Record type:** PREOPEN_RESEARCH_ONLY
- **As-of:** 2026-10-13 07:37 KST
- **Model label:** market-review-v1.1-research-only
- **Data label:** web-curated-2026-10-13-0737
- **Important:** This is an early pre-open research note, not the specified 08:00/08:30/08:50 snapshot. KOSPI 200 futures, full KRX breadth, and several required overseas futures were not verified in this run.
- **Historical DB:** Not ingested through `record_live_market_review.py`; do not treat this Markdown note as a completed Historical DB transaction.
- **Monitor integrity:** The current monitor snapshot contains a confirmed return-horizon/freshness defect. See [Issue #27](https://github.com/chayobi03-cyber/investment/issues/27).

## 1. Decision summary

**Qualitative regime: RISK-OFF / capital-preservation mode.** The signal is driven by the domestic selloff, foreign and institutional net selling, semiconductor weakness, and the oil/inflation/rates channel. This is a research judgement, not a calibrated R1–R6 engine output: the current monitor's change percentages are not valid daily returns, so its `RISK=GREEN` and `REGIME=UNCONFIRMED` must not be used as authoritative.

- **New entries:** WAIT / no buy permission.
- **BUY_ALLOWED:** false.
- **EXECUTION_ALLOWED:** false.
- **D/W/M rule:** No stock-level entry signal until each candidate passes daily/weekly/monthly trend, support/resistance, distance-from-high, momentum, and relative-strength validation.
- **Today's validation window:** Compare the pre-open hypothesis with the Korean open and 09:30/10:00 KST outcomes. These outcomes are not known at this record's timestamp.

## 2. Korea: last regular-session close (2026-10-12)

| Observation | Value | Evidence/status |
|---|---:|---|
| KOSPI close | 6,384.24 (-3.65%) | Published close; [NewsPim](https://www.newspim.com/news/view/20261012001236) |
| KOSPI open / high / low | 6,578.17 / 6,589.69 / 6,368.49 | Daily OHLC; [Investing.com history](https://www.investing.com/indices/kospi-historical-data) |
| KOSDAQ close | 849.19 (-4.83%) | Published close; [NewsPim](https://www.newspim.com/news/view/20261012001236) |
| KOSPI foreign flow | -₩2.0186T | Published close; [NewsPim](https://www.newspim.com/news/view/20261012001236) |
| KOSPI institution flow | -₩110.7B | Published close; [NewsPim](https://www.newspim.com/news/view/20261012001236) |
| KOSPI individual flow | +₩1.4674T | Published close; [NewsPim](https://www.newspim.com/news/view/20261012001236) |
| USD/KRW | 1,335.0 | 2026-10-12 local-market close; [NewsPim](https://www.newspim.com/news/view/20261012001236) |

The KOSPI closed only 15.75 points above its intraday low and fell about 2.95% from its opening level to the close. The session marked a fourth consecutive trading-session decline. From the 2026-10-02 close of 7,003.74 to 6,384.24 on 2026-10-12, KOSPI declined about **8.85%**. From the 2026-10-01 close of 6,971.35, month-to-date decline was about **8.42%**. The current close is about **29.96% below** the 2026-06-22 record close of 9,114.55. The record-high reference and foreign-flow backdrop are reported by [Yonhap](https://www.yna.co.kr/amp/view/AKR20261012086951008).

### D/W/M market structure

- **Daily (D): RED.** Large down session, close near low, and four-session decline. The 6,368.49 low is the first immediate reference level, not a proven durable support.
- **Weekly (W): RED.** The 2026-10-08 close of 6,625.93 was about 4.95% below the 2026-10-01 close of 6,971.35; 2026-10-12 then extended the decline.
- **Monthly (M): RED / MTD deterioration.** Month-to-date KOSPI is down about 8.42% from the 2026-10-01 close. A full moving-average/oscillator calculation was not run here; this is a close-to-close structure assessment, not a complete technical-indicator scan.

## 3. Global cross-asset context (latest 2026-10-12 US session)

| Observation | Last reported move/level | Interpretation |
|---|---:|---|
| Dow Jones | +0.38% | Mixed, not broad-based US panic |
| S&P 500 | -0.06% | Near flat |
| Nasdaq Composite | -0.44% | Growth/technology pressure |
| Philadelphia Semiconductor Index (SOX) | -2.7%, at a three-week low | Semiconductor-specific stress |
| Brent crude | about $106.65/bbl, +1.8% | Elevated inflation/supply-risk input |
| WTI crude | about $93.55/bbl, +1.9% | Elevated energy cost input |
| US 10Y Treasury yield | about 5.24% at the last available prior session | Treasury cash market was closed on 2026-10-12; this is not a live 2026-10-13 yield |

Evidence: [Reuters US close](https://www.reuters.com/business/us-stock-futures-muted-oil-stays-above-100-ahead-earnings-2026-10-12/), [AP market recap](https://apnews.com/article/f07713e8b2e438ac5903b50f5ce97235).

### Causal chain to monitor

Geopolitical attacks affecting Saudi Arabia -> higher oil risk premium -> inflation expectations -> more restrictive Fed pricing / higher discount rates -> pressure on long-duration growth equities and semiconductors.

The oil/technology conjunction is observed; it does not prove that geopolitics alone caused every stock move. The US session was mixed by index, but the semiconductor decline and negative Nasdaq breadth reinforce risk reduction rather than an immediate dip-buy thesis. US CPI/PPI, retail sales, and major bank earnings were upcoming catalysts in Reuters' 2026-10-12 report.

## 4. Domestic leadership / watchlist

| Instrument | 2026-10-12 close or move | Interpretation |
|---|---:|---|
| Samsung Electronics | ₩250,500; -4.39% | Weak semiconductor leadership; no averaging-up based on reported earnings alone |
| SK hynix | ₩1,605,000; -4.52% | Weak semiconductor leadership; do not treat one down day as a buy trigger |
| SK Square | -6.29% | High-beta underperformance; keep on watch, not an automatic dip-buy |
| Samsung SDI | ₩561,000; -1.41% | One-day relative outperformance versus KOSPI; insufficient for entry without D/W/M and sector checks |
| KB Financial | Flat | One-day relative resilience, not a trend signal |
| Hyundai Motor | -1.39% | Outperformed KOSPI on the day; entry status still unconfirmed |
| Samsung Biologics | -1.48% | Outperformed KOSPI on the day; entry status still unconfirmed |

Stock close/move sources: [NewsPim](https://www.newspim.com/news/view/20261012001236) and [Samsung SDI daily history](https://kr.investing.com/equities/samsung-sdi-historical-data).

For Samsung Fire, SK Innovation, Doosan Enerbility, and NAVER, this note does not assign a daily close-to-close move: the monitor's stored `change_pct` is based on adjacent 5-minute bars and is invalid for that purpose. No daily/weekly/monthly entry signal is assigned to any individual security in this research note.

## 5. Price references and scenario gates

These are provisional reference levels derived from recent daily OHLC/close data, not a validated support/resistance model.

- **Immediate downside reference:** 6,368.49, the 2026-10-12 intraday low. A decisive break with no prompt reclaim increases continuation risk.
- **Psychological level below:** 6,300; round-number reference only, not a verified historical support zone.
- **First overhead supply zone:** 6,578–6,590, the 2026-10-12 open/high area.
- **Next overhead reference:** 6,625.93, the 2026-10-08 close.
- **Higher resistance area:** 6,804–6,941, the 2026-10-07 and 2026-10-06 closes.

### Intraday decision gates

1. **Breakdown case:** KOSPI loses 6,368.49 and cannot reclaim it; foreign selling stays heavy and semiconductor leaders underperform. Action: remain defensive; no new entry.
2. **Stabilization attempt:** KOSPI holds above the prior low, reclaims 6,500–6,590, market breadth improves, and foreign net selling clearly narrows. Action: watch-only; wait for the close and stock-level D/W/M evidence.
3. **Credible recovery:** KOSPI sustains above the 6,578–6,590 zone and semiconductor leaders improve relative to the index, without a renewed oil/rates shock. Action: re-evaluate candidates, not automatic BUY.

## 6. Monitor data-quality incident and corrective action

The monitor's latest stored state at 2026-10-13 07:28:33 KST reported KOSPI -0.377%, KOSDAQ -0.435%, Samsung Electronics -0.299%, SK hynix -0.496%, `DATA_QUALITY=GREEN`, and `RISK=GREEN`. These are not prior-session close-to-close returns: the implementation takes the last 5-minute bar divided by the immediately preceding 5-minute bar while the thresholds are labelled `material_abs_pct_15m`. Freshness also uses the newest timestamp across all symbols, so a fresh USD/JPY quote can mask older Korean index observations.

- **Root-cause ticket:** [investment #27](https://github.com/chayobi03-cyber/investment/issues/27)
- **Operational instruction:** Do not use the current monitor's compact `RISK`, `TREND`, or `DATA_QUALITY` output as authoritative buy timing until return horizons and per-instrument/session-aware freshness are fixed and regression-tested.
- **HOTL evidence to append after the session:** opening return, 09:30 and 10:00 returns, intraday high/low excursion, actual KOSPI/KOSDAQ breadth, foreign/institution flow, and semiconductor relative strength. Keep the pre-open hypothesis immutable; record hit/miss and reasons separately.

## Sources

1. [NewsPim — 2026-10-12 KOSPI/KOSDAQ close and investor flow](https://www.newspim.com/news/view/20261012001236)
2. [Yonhap — October foreign flow and KOSPI drawdown](https://www.yna.co.kr/amp/view/AKR20261012086951008)
3. [Reuters — US close, oil, semiconductors and upcoming catalysts](https://www.reuters.com/business/us-stock-futures-muted-oil-stays-above-100-ahead-earnings-2026-10-12/)
4. [AP — US indices, Brent and latest available 10Y yield](https://apnews.com/article/f07713e8b2e438ac5903b50f5ce97235)
5. [KOSPI daily history](https://www.investing.com/indices/kospi-historical-data)
