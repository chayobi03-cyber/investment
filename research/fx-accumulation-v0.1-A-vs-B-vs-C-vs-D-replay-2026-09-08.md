# FX Accumulation A/B/C/D Replay — v0.1

**Date:** 2026-09-08
**Status:** FIRST REPLAY RESULT — NOT PROMOTED TO A HARD RULE
**Origin:** P0 open-work item from `docs/governance/CLAUDE_HANDOVER_2026-09-08.md` and
`docs/governance/LESSONS_LEARNED_2026-09-07_FX_ACCUMULATION.md` section 8 ("Next Validation").
**Script:** `research/scripts/run_fx_accumulation_abcd.py`
**CI workflow:** `.github/workflows/fx-accumulation-abcd.yml`
**Successful run:** GitHub Actions run
[`34168543658`](https://github.com/chayobi03-cyber/investment/actions/runs/34168543658)
(commit `62c8f7c`), artifact `fx-accumulation-abcd-results`
(id `10034951933`, digest `sha256:fd3ed89ec5cf627d1feac8bdb56a7a08bf066290e13fcfe34b46b8d1561969f9`).

> This is a research replay, not a live trading signal. No number in this
> document should be used as a current market price, current FX rate, or
> current portfolio value.

---

## 1. Hypothesis

From the FX-ACCUMULATION RULE v0.2 lesson (2026-09-07):

> `Buy Intensity = Portfolio Gap × Asset Opportunity × Risk Gate × FX Benefit`

H2 (restated from the governance doc): a combined `FX × Asset Price` trigger
improves KRW-denominated acquisition efficiency for a foreign-equity position
versus FX-only or asset-price-only triggers, without a materially worse
outcome than plain periodic accumulation.

This replay tests four accumulation strategies for a hypothetical KRW-funded
S&P 500 position, holding the benchmark, decision frequency, and total cash
budget identical across all four:

- **A — Fixed periodic (plain DCA):** invest the same weekly amount always.
- **B — Asset-price trigger:** tilt weekly investment up as the S&P 500
  falls further below its trailing 52-week high.
- **C — FX trigger:** tilt weekly investment up as USD/KRW falls to a lower
  point in its trailing 3-year distribution (KRW strengthens).
- **D — Combined trigger:** multiply B's and C's tilts together, matching
  the `Asset Opportunity × FX Benefit` term of the governance formula
  (Portfolio Gap and Risk Gate are held constant/out of scope for this
  replay so only the FX/asset tilt is being isolated and tested).

## 2. Data

- **Source:** Yahoo Finance daily closes, fetched inside GitHub Actions CI
  (this interactive session's network policy blocks direct egress to
  `query1.finance.yahoo.com` and `fred.stlouisfed.org`, so — mirroring the
  existing `v0.2.3 daily panel backtest` pattern in this repository — the
  fetch runs in CI and results are recovered from the workflow run/artifact
  rather than fetched in-session).
- **Series:** `^GSPC` (S&P 500) and `KRW=X` (USD/KRW), daily, forward-filled,
  resampled to weekly (`W-FRI`) closes.
- **Window:** script start parameter `START = "2004-01-01"`, end = CI run
  timestamp (2026-09-07). After the 52-week signal warm-up required by the
  asset-drawdown and FX-percentile windows, the valid replay window is
  **1,134 weekly observations (~21.8 years)**, approximately late
  2004/early 2005 through 2026-09-04. The exact first/last valid week is
  recorded in `run_metrics.json` inside the CI artifact; this session could
  not independently re-verify that exact date because the artifact zip is
  hosted on `productionresultssa19.blob.core.windows.net`, which this
  session's egress policy also blocks. The metrics below are read from the
  job's stdout log, not from a locally re-opened CSV — see the **Provenance
  caveat** in section 6.
- **Common weekly budget:** KRW 1,000,000. Every strategy deploys the
  identical total budget (KRW 1,134,000,000 nominal, confirmed identical
  across A/B/C/D in the run output) over the identical 1,134 weeks — only
  the per-week weighting differs. This satisfies the handover's "same
  benchmark / same frequency / same cash budget" requirement.

## 3. Threshold definitions

**Strategy B (asset-price tilt)**, based on drawdown from the trailing
52-week S&P 500 high:

| Drawdown from 52-week high | Raw multiplier |
|---|---:|
| 0% to -5% | 1.0 |
| -5% to -10% | 1.5 |
| -10% to -20% | 2.0 |
| ≤ -20% | 3.0 |

**Strategy C (FX tilt)**, based on USD/KRW's percentile rank within its
trailing 3-year (156-week) window (lower percentile = weaker USD / stronger
KRW = more favorable):

| USD/KRW trailing-3y percentile | Raw multiplier |
|---|---:|
| < 20th | 2.0 |
| 20th–40th | 1.5 |
| 40th–70th | 1.0 |
| ≥ 70th | 0.7 |

**Strategy D:** `raw_D = raw_B × raw_C`.

All four strategies' raw multipliers are renormalized so their weekly sum
equals the same total budget as Strategy A (see script `normalize_and_invest`).
This is a **tilt of a fixed pool**, not a variable total spend — the same
invariant the handover asked for.

## 4. Backtest results

| Strategy | Total invested (KRW) | Final value (KRW) | Total return | Annualized IRR (money-weighted) | Avg. acquisition cost (KRW / index unit) | Max drawdown (value-per-invested-KRW basis) | Trigger frequency |
|---|---:|---:|---:|---:|---:|---:|---:|
| A — Fixed periodic | 1,134,000,000 | 5,499,308,000 | +384.9% | **12.76%** | 2,140,511 | -28.1% | 0% (no trigger concept) |
| B — Asset-price trigger | 1,134,000,000 | 5,791,347,000 | +410.7% | **12.87%** | 2,032,571 | -28.3% | 29.4% |
| C — FX trigger | 1,134,000,000 | 6,101,459,000 | +438.0% | **12.46%** | 1,929,264 | -28.0% | 35.4% |
| D — Combined FX × Asset | 1,134,000,000 | 6,253,106,000 | +451.4% | **12.59%** | 1,882,477 | -28.1% | 59.2% |

Detection-style metrics against a "good acquisition window" ground truth
(weeks where KRW cost per index unit, `SP500 × USDKRW`, is at or below its
trailing-3-year 20th percentile; 8 such window episodes exist in the full
sample):

| Strategy | True-positive weeks | False-positive weeks | FP rate of triggers | Missed good windows (FN) | Mean lead time when detected |
|---|---:|---:|---:|---:|---:|
| A | 0 | 0 | n/a (never triggers) | 8 / 8 (structural — see caveat) | n/a |
| B | 40 | 293 | 88.0% | 1 / 8 | 0.0 days |
| C | 9 | 392 | 97.8% | 6 / 8 | 0.0 days |
| D | 44 | 627 | 93.4% | 0 / 8 | 0.0 days |

### Reading the results

- **Total nominal return and average acquisition cost improve monotonically**
  from A → B → C → D. The combined trigger achieves the lowest average KRW
  cost per index unit and the highest total nominal return of the four.
- **Money-weighted annualized IRR does *not* improve monotonically.** B has
  the highest IRR (12.87%), then A (12.76%), then D (12.59%), then C
  (12.46%) — the ranking by IRR is **B > A > D > C**, not A < B < C < D as
  the total-return column alone would suggest. This matters: total return
  and average acquisition cost are aggregate, timing-insensitive numbers,
  while IRR accounts for *when* the KRW was actually spent. On this
  benchmark, tilting harder toward FX-only signals (C) did not turn into a
  better money-weighted outcome than doing nothing extra (A) or than the
  price-only tilt (B).
- **Coverage of the 8 "good" acquisition windows is uneven.** B (asset-price
  tilt) catches 7/8; D (combined) catches all 8; C (FX-only tilt) catches
  only 2/8 and misses 6/8. This is consistent with the governance intuition
  that "FX is not an independent buy signal" (`docs/governance/LESSONS_LEARNED_2026-09-07_FX_ACCUMULATION.md`
  section 2) — on this benchmark, the cheapest KRW-cost weeks for a foreign
  asset are driven more by the asset's own drawdowns than by USD/KRW alone.
- **None of the triggers show real lead time.** Mean lead time is 0.0 days
  for B, C, and D — when a trigger did coincide with a good window, it did
  so in the *same week* the window started, never earlier. None of these
  three trigger designs functions as an early-warning indicator; at best
  they are contemporaneous confirmations.

## 5. Falsification

### 5.1 H2 status: partially falsified, not confirmed

H2 claimed the combined FX × Asset trigger improves acquisition efficiency
"without a materially worse outcome" than the alternatives. On aggregate
acquisition-cost and total-return metrics, D wins outright. But on the
money-weighted IRR — arguably the more decision-relevant number, since it
reflects the actual timing of KRW outlays rather than an aggregate average —
D is **worse than the plain fixed-periodic baseline (A)** and worse than the
price-only trigger (B). H2 is not confirmed as stated; the corrected claim
this replay supports is narrower:

> On this single-benchmark, single-asset-pair replay, a price-based or
> combined FX×price tilt lowers average acquisition cost and raises total
> nominal return versus fixed periodic accumulation, but does not
> necessarily raise the money-weighted annualized return, and an FX-only
> tilt (C) underperforms the fixed baseline on annualized IRR while adding
> the most missed "good windows" among the three triggered strategies.

### 5.2 Methodological limitation — the FP/FN/lead-time ground truth is partly circular

**This is the most important caveat in this document.** The "good
acquisition window" ground truth used to compute true/false positives,
false negatives, and lead time is defined directly from `krw_cost = SP500 ×
USDKRW` — the exact same combined quantity that Strategy D's trigger
approximates (`raw_B` is a function of the SP500 leg, `raw_C` is a function
of the USDKRW leg, and D multiplies them). This is a materially weaker
separation than the Stress Convergence framework's Early Warning / Crisis
Confirmation split, which deliberately uses **independent indicator
families** (rates, credit, labor, energy, volatility) so that one family
can validate or falsify another.

Here, by contrast:

- Strategy D's high false-positive rate (93.4% of its triggered weeks are
  *not* inside a "good window") and its 0.0-day mean lead time are expected
  almost by construction, not purely evidence of a weak strategy: the
  ground truth and the trigger both derive from the same two input series.
- Strategy C's poor detection performance (FN = 6/8, FP rate 97.8%) is more
  informative precisely *because* USDKRW is only one of the two legs in the
  ground truth — it is the closest thing to an independent test in this
  replay, and it still underperforms.
- The high false-positive rates across B/C/D should not be read the same
  way as a stress-convergence false-positive rate (where the detector and
  the crisis definition are genuinely independent). They mean "the trigger
  fires in many weeks that are not in the cheapest 20th percentile," which
  is a much easier bar to fail than "the trigger wrongly signals an
  independently defined crisis."

**Recommended v2 follow-up:** redefine the ground truth using a forward-looking,
strategy-independent target — e.g., "this week's KRW cost basis turned out
to be cheaper than the KRW cost basis realized 26/52 weeks later" — so the
detection metrics test genuine forecasting value rather than partially
restating the trigger's own inputs. Do not treat the current FP/FN/lead-time
numbers as validating or invalidating the triggers on their own; treat the
IRR and acquisition-cost columns in section 4 as the more load-bearing
result of this replay.

### 5.3 Other caveats

- Single asset pair (USD/KRW, S&P 500 only). No robustness check yet across
  other foreign-asset buckets (US Dividend, Domestic ETF, Gold/JPY hedge)
  named in `docs/governance/PORTFOLIO_ALLOCATION_RULE_v0.1.md`.
- Weekly `W-FRI` resampling of daily closes; no transaction costs, no bid/ask
  or FX conversion spread, no tax treatment.
- Threshold tiers (5%/10%/20% drawdown bands; 20th/40th/70th FX percentile
  bands) were set from the governance document's existing staging language,
  not fit to this data — but they also have not yet been stress-tested
  against a second, independent historical window or asset pair. Per the
  Investment Research Loop's decision discipline, these thresholds must not
  be tuned post hoc to improve this specific result.
- IRR is a single money-weighted internal rate of return over the full
  ~21.8-year series; it is sensitive to the very large late-period cashflow
  denominator effect common to long DCA series and should be read as
  directional, not as a precise expected forward return.
- One historical realization only — 2004–2026 is a single, mostly-rising
  path for both the S&P 500 and, on net, USD/KRW's range. It is not a
  stress test across multiple regimes the way the Stress Convergence
  11-window benchmark is.

## 6. Provenance caveat

The exact numbers in sections 4–5 are transcribed from the successful CI
job's stdout log (`replay` job, run
[`34168543658`](https://github.com/chayobi03-cyber/investment/actions/runs/34168543658)),
not from a locally reopened `strategy_summary.csv`. The raw
`weekly_panel.csv`, `strategy_summary.csv`, and `run_metrics.json` are
preserved in the CI artifact `fx-accumulation-abcd-results` (retained until
2026-12-06), but this interactive session could not download that artifact:
GitHub Actions artifacts are served from
`productionresultssa19.blob.core.windows.net`, and this session's network
egress policy blocks that host (confirmed via both direct HTTPS and the
web-fetch tool; see `/root/.ccr/README.md`'s guidance to report, not route
around, an egress-blocked host). A future session with unrestricted egress,
or a human downloading the artifact directly from the GitHub Actions UI,
should re-open `weekly_panel.csv` and re-verify the exact valid-window start
date and the full precision of every metric before this replay is used to
justify any rule promotion.

## 7. Action

- **Do not promote any of A/B/C/D to a hard deployment rule.** This is a
  first replay on one asset pair, one historical path, and a ground truth
  with a documented circularity limitation (section 5.2).
- **Directionally**, this replay is consistent with — not contradictory to
  — the existing FX-ACCUMULATION RULE v0.2 principle that FX alone is a
  weaker signal than asset price, and weaker still than a combination: C
  (FX-only) has the worst window coverage and the worst IRR of the three
  triggered strategies.
- **Do not treat D's higher total return / lower average cost as proof of
  superiority** over B or A without also weighing D's lower IRR than both A
  and B. If a single ranking must be chosen, the money-weighted IRR ranking
  (B > A > D > C) is the more decision-relevant one for a project whose
  stated objective (`README.md`) is risk-adjusted compounding, not raw
  average cost basis.

## 8. Lesson Learned

Aggregate acquisition-cost and total-return metrics can rank strategies
differently than a money-weighted (timing-aware) return metric. A
combined-trigger strategy that looks best by average cost basis was not the
best by annualized IRR in this replay. Any future accumulation-strategy
comparison in this project should report both an aggregate metric (average
cost, total return) and a timing-aware metric (IRR or equivalent), because
they can disagree, and the disagreement itself is information.

Separately: a detection-style evaluation (FP/FN/lead time) is only as
informative as the independence of its ground truth from the strategy being
tested. Reusing this replay's FP/FN framework for other strategy
comparisons should first check whether the same circularity risk applies.

## 9. Rule Change

**YES, narrowly** — amend `docs/governance/LESSONS_LEARNED_2026-09-07_FX_ACCUMULATION.md`
section 8 ("Next Validation") to record that the A/B/C/D replay has been run
once (this document) with the above result and caveats, and that promotion
of any trigger design to an operating rule requires (a) a second, more
adversarial historical window or asset pair, and (b) a non-circular
detection ground truth per section 5.2, before the FX-ACCUMULATION RULE v0.2
working thresholds can be treated as validated rather than working
hypotheses.

No change to the Portfolio Allocation Rule v0.1 targets, the FX trigger
bands, or the Stress Convergence framework is justified by this replay
alone.

## 10. Git Commit

**YES** — this is a validated (CI-executed, reproducible) research replay
result with a documented methodology, result table, and falsification
section, per the Auto Commit Policy v0.1 ("validated research findings that
affect the decision framework"). Committed alongside the IRR bug fix in
`research/scripts/run_fx_accumulation_abcd.py`.
