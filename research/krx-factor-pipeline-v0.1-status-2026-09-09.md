# KRX Factor Pipeline v0.1 — Status (2026-09-09)

## What this is

A 3-stage pipeline (`research/scripts/run_krx_factor_pipeline.py`) covering the
agreed 10-ticker universe (8 semiconductor-related names + KODEX 200 + KODEX
반도체 as market/sector references):

1. **Data completeness** — per ticker/field, expected vs. actual trading days,
   completeness %, null counts. Gaps are reported, never silently imputed.
2. **Raw factors** — momentum (20/60/120d), 60d realized vol, drawdown from
   52w high, sector-relative momentum, investor-flow sums, and valuation
   ratios (PER/PBR/EPS/BPS/DIV).
3. **Normalized factors** — each raw factor converted to a cross-sectional
   percentile rank (0-100) within the 10-ticker universe.

**This pipeline does NOT compute Buy Intensity or Risk Score itself.** The
normalized percentile columns are intended future inputs to
`docs/governance/PER_ASSET_BUY_INTENSITY_RISK_SCORE_FRAMEWORK_v0.1.md`'s
actual scoring — which factor feeds which score, with what sign and weight,
is a deliberately separate, explicit decision not implied by running this
pipeline. Research pipeline only, not a live trading signal.

## Data sources

| Data | Source | Notes |
|---|---|---|
| EOD OHLCV | KRX via `pykrx` (`stock.get_market_ohlcv`) | Works anonymously, no login needed |
| Investor-type net-buy flow (기관/외국인) | Naver Finance (`finance.naver.com/item/frgn.naver`), scraped | Share-count based; KRW estimated as shares × close |
| 개인(individual) flow | Not published by Naver — computed as residual `-(기관+외국인)` | Explicit estimate, not a measured figure |
| PER/PBR/EPS | Naver Finance (`finance.naver.com/item/main.naver`), scraped | Point-in-time snapshot, not a history |
| BPS/배당수익률(div) | Same page | Currently unreliable — see Known Gaps |
| Market-day calendar | KODEX 200 (069500) OHLCV | Stands in for a KOSPI trading-day calendar |
| Sector benchmark | KODEX 반도체 (091160) OHLCV | Stands in for a semiconductor sector index |
| Financial-statement fundamentals (revenue, margins, etc.) | OpenDART | **Not yet wired up** — see Next Steps |

## Why Naver Finance instead of KRX directly

`pykrx` 1.2.8's investor-flow, fundamental, and index/sector endpoints all
require a logged-in KRX session (`KRX_ID`/`KRX_PW` env vars — confirmed by
reading `pykrx/website/comm/auth.py`'s `build_krx_session()`). Separately, KRX
itself migrated to a member-only "Data Marketplace" on 2025-12-27 with
Naver/Kakao social login as the promoted signup path, a change `pykrx` has an
open, unresolved compatibility issue for
([sharebook-kr/pykrx#244](https://github.com/sharebook-kr/pykrx/issues/244)).
Rather than block on that, investor-flow and valuation are sourced directly
from Naver Finance instead — an unrelated site with no such login gate. OHLCV
continues via `pykrx` since that endpoint works anonymously.

## Bugs found and fixed this session

1. **Missing `lxml` dependency** — `pandas.read_html()` needs an HTML parser
   backend; the workflow's pip install only listed `pandas numpy pykrx`,
   causing 100% of investor-flow parsing to fail with
   `ImportError: Missing optional dependency 'lxml'`. Fixed by adding
   `lxml requests` to the install step.
2. **Wrong valuation regex** — the original label-proximity regex matched
   unrelated numbers elsewhere on the page (e.g. legend text), producing
   identical bogus values across every ticker (PBR=4.0 for all 8 companies;
   EPS/BPS=2026.06, a date rather than a value). Replaced with regex anchored
   on Naver's documented, specific DOM element ids (`id="_per"`, `id="_eps"`,
   `id="_pbr"`, `id="_bps"`) — precise rather than proximity-based.
3. **외국인(foreign) flow column always NaN** — `inst_col` (기관) matched via
   substring (`"기관" in c`), but `frgn_col` used `c.startswith("외국인")`.
   Naver's flow table has a two-row header that pandas can flatten into a
   tuple-stringified column name (e.g. `"('외국인', '순매매량')"`), which
   *contains* "외국인" without *starting with* it — `startswith` silently
   matched nothing, leaving `flow_외국인_20d_est_krw` (and the derived
   `flow_개인` residual) 100% NaN for every ticker, even though `flow_기관`
   worked. Fixed by switching to substring matching, consistent with
   `inst_col`, still excluding holdings-count/ratio columns (보유/지분).

## Current working state (as of the 2026-09-09 CI run, window 2025-08-05 to 2026-09-09)

Investor-flow completeness is 268/268 trading days with **0 null cells**
(previously 140/268 with 140 nulls before the lxml fix). Raw factors, final
confirmed values:

| ticker | name | mom_20 | mom_60 | vol_60 | drawdown_52w | flow_기관_20d (KRW) | flow_외국인_20d (KRW) | PER | PBR | EPS |
|---|---|---|---|---|---|---|---|---|---|---|
| 005930 | 삼성전자 | +12.5% | -20.0% | 1.03 | -25.7% | +1.90e11 | +1.38e12 | 12.09 | 3.13 | 22,292 |
| 000660 | SK하이닉스 | +30.2% | -18.9% | 1.23 | -36.4% | -2.64e12 | -1.48e12 | 8.27 | 5.01 | 224,313 |
| 042700 | 한미반도체 | +17.6% | -27.8% | 1.17 | -38.8% | +8.40e10 | +2.38e11 | 107.51 | 31.81 | 2,330 |
| 039030 | 이오테크닉스 | +27.5% | -11.5% | 0.99 | -23.2% | +1.17e11 | -9.68e10 | 53.36 | 7.74 | 8,808 |
| 357780 | 솔브레인 | +7.6% | -20.8% | 0.82 | -32.5% | -1.01e10 | +3.23e10 | 20.60 | 2.25 | 16,410 |
| 064760 | 티씨케이 | +28.4% | -11.4% | 1.01 | -26.1% | +5.17e10 | -4.72e10 | 35.34 | 5.22 | 7,287 |
| 014680 | 한솔케미칼 | -13.1% | -33.1% | 0.67 | -39.9% | -4.38e10 | +2.99e10 | 14.86 | 1.99 | 13,662 |
| 240810 | 원익IPS | +14.7% | -31.2% | 1.29 | -34.5% | -1.06e11 | +1.71e11 | 34.06 | 5.44 | 3,526 |

PER/PBR/EPS values are plausibly differentiated across tickers (e.g. 한미반도체's
PER 107.51 vs. SK하이닉스's 8.27, consistent with their very different growth/
valuation profiles), and flow values are non-identical and directionally
sensible. Percentile normalization (Stage 3) runs cleanly against these.

## Known gaps

- **BPS and 배당수익률(dividend yield) are still NaN for every ticker.** The
  DOM-id anchor approach that fixed PER/PBR/EPS did not resolve these two —
  either the `id="_bps"` element doesn't exist in the current page structure,
  or dividend yield's label-proximity match still isn't matching. Not
  diagnosable further from this session without live access to
  `finance.naver.com` (network-blocked here). Left as a documented limitation
  rather than guessed at blindly.
- **개인(individual) flow is a residual estimate**, not a directly measured
  figure — Naver's `frgn.naver` page does not publish it.
- **KRW flow values are estimated as shares × close**, not the actual
  transacted value (which can differ intraday).
- **Investor-flow history is capped at ~140 trading days** (7 pages ×
  ~20 rows/page from Naver), well short of the full 268-day OHLCV window —
  sufficient for the 20-day flow sums this pipeline currently computes, but a
  constraint if longer flow lookback windows are needed later.
- **`DART_API_KEY` is now registered** (confirmed `True` in this run's
  presence-only diagnostic), but the OpenDART fundamentals stage itself is
  not yet built — see Next Steps.

## Next steps

1. Build the OpenDART stage: fetch each ticker's `corp_code` once via
   OpenDART's `corpCode.xml`, then pull financial-statement fundamentals
   (revenue, gross margin, operating income, etc.) via `fnlttSinglAcntAll.json`,
   append as additional raw factors, and extend Stage 3's percentile
   normalization to cover them.
2. Once fundamentals are in, feed the full set of normalized percentile
   columns into `docs/governance/PER_ASSET_BUY_INTENSITY_RISK_SCORE_FRAMEWORK_v0.1.md`
   as the actual per-asset Buy Intensity / Risk Score inputs — a separate,
   explicit weighting/sign decision, not automated by this pipeline.
3. Optionally revisit BPS/배당수익률 extraction if those fields become
   needed for scoring.
