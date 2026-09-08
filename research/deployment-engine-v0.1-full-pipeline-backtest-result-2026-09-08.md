# Deployment Engine v0.1 — Full Pipeline End-to-End Backtest Result

**Date:** 2026-09-08
**Status:** CAPSTONE REPLAY — DIRECTIONAL SUPPORT ONLY, NOT A LIVE-READY SYSTEM
**Origin:** The last unchecked row in
`docs/governance/PORTFOLIO_DEPLOYMENT_ENGINE_v0.1.md` section 8: "The full
five-stage pipeline end-to-end."
**Script:** `research/scripts/run_deployment_engine_v0.1_full_pipeline_backtest.py`
**CI workflow:** `.github/workflows/deployment-engine-full-pipeline-backtest.yml`
**Run:** [`34188894534`](https://github.com/chayobi03-cyber/investment/actions/runs/34188894534)
(commit `647a5f8`)

> Research replay only, not a live trading signal.

## 1. Hypothesis

Does combining every piece this session separately validated (Asset
Opportunity price-drawdown tiers, the bounded FX Benefit modifier, the JPY
caution modifier, and the Dry Powder 28% floor) into one coherent pipeline
actually beat doing nothing extra — and does the combination add anything
beyond what the Dry Powder floor alone already showed?

## 2. Data

Same 2004–2026 weekly window as
`research/fx-accumulation-v0.1-A-vs-B-vs-C-vs-D-replay-2026-09-08.md` and
`research/deployment-engine-v0.1-dry-powder-floor-backtest-result-2026-09-08.md`
(1,134 valid weeks) — **not** the 1993–2022-01-10 window used by the
(rejected) Risk Gate cap replay. Adds `JPYKRW=X` and `JPY=X` (USD/JPY) from
Yahoo Finance to the S&P 500/USD-KRW pair.

## 3. Method

Reuses the static-total stock simulation from the Dry Powder floor
backtest (42/58 initial split, annual non-drawdown-week rebalance, 3.5%
cash yield). Combined tranche formula for a drawdown week:

```text
intended_tranche = base_tranche × asset_opportunity_tier × fx_benefit × jpy_multiplier
```

- `asset_opportunity_tier`: 1.5/2.0/3.0 (drawdown from 52-week high), as in
  every prior replay this session.
- `fx_benefit`: bounded ×0.3–×1.2, per
  `PORTFOLIO_DEPLOYMENT_ENGINE_v0.1.md` section 6.
- `jpy_multiplier`: ×0.9 caution flag when JPY/KRW rises while USD/JPY
  falls over a trailing **5-week** window. **This is a cadence adaptation,
  not the same definition as the original JPY overlay replay**, which used
  a 5-*day* momentum window on a daily panel
  (`research/jpy-overlay-v0.1-seven-window-replay-result-2026-09-08.md`).
  The two are not directly comparable.

**Why the Stress Convergence Risk Gate cap is deliberately excluded:** it
was independently replayed and rejected
(`research/deployment-engine-v0.1-risk-gate-cap-backtest-result-2026-09-08.md`
— cost IRR with no measured drawdown benefit). A "full pipeline of
validated pieces" should not include a piece that failed its own
validation, so this capstone test combines stages 3, 4, part of 2 (JPY
only), and 5 (Dry Powder floor), and reports the omission explicitly rather
than silently.

Three paths: **BASELINE** (no tilt, rebalance only), **FULL_NOFLOOR**
(combined tilt, no floor), **FULL_WITHFLOOR** (combined tilt, 28% floor).

## 4. Results

| Path | Final total (KRW) | Total return | CAGR | Max drawdown | Min Dry Powder % | Total deployed (KRW) | Total blocked (KRW) |
|---|---:|---:|---:|---:|---:|---:|---:|
| BASELINE | 482,796,300 | +382.7% | **7.49%** | **−16.55%** | 34.50% | 0 | 0 |
| FULL_NOFLOOR | 507,983,000 | +407.8% | **7.74%** | **−28.04%** | 0.00% | 353,934,400 | 128,635,100 |
| FULL_WITHFLOOR | 513,658,600 | +413.5% | **7.79%** | **−20.68%** | 24.67% | 245,663,000 | 236,906,500 |

## 5. Falsification

### 5.1 Does the combination beat BASELINE? Yes, on CAGR — at a drawdown cost.

Both tilted variants beat BASELINE's 7.49% CAGR (NOFLOOR 7.74%, WITHFLOOR
7.79%). But BASELINE has by far the **best** max drawdown of the three
(−16.55%), while FULL_NOFLOOR has the **worst** (−28.04%).

### 5.2 The "buying into the decline" mechanical pattern is confirmed in real data

The synthetic sanity check's prediction holds: **tactically adding
exposure during a decline mechanically worsens max drawdown**, because the
newly-deployed capital is itself exposed to further decline before any
recovery arrives, even though the S&P 500 fully recovered from every major
drawdown (2008, 2020, 2022) well within this 2004–2026 window. Buying more
into a fall shows up as a *deeper* trough relative to the pre-fall peak by
construction — it is not evidence of a flawed strategy, but it is a real
and unavoidable trade-off, not a free lunch.

### 5.3 Does the Dry Powder floor claw back the MDD cost? Yes, substantially.

FULL_WITHFLOOR's max drawdown (−20.68%) recovers most of the gap between
BASELINE (−16.55%) and FULL_NOFLOOR (−28.04%) — roughly 60% of the
drawdown damage tactical tilting caused is undone by the floor, at
essentially no CAGR cost (7.79% vs. 7.74%, WITHFLOOR is *marginally
better*). This matches the standalone Dry Powder floor backtest's finding
exactly in direction.

### 5.4 Do FX Benefit and JPY caution add anything on top of the floor? No — if anything, marginally negative.

This is the most important finding for judging the engine's current
maturity. Compare this run's numbers to the **Dry-Powder-floor-only**
backtest (`research/deployment-engine-v0.1-dry-powder-floor-backtest-result-2026-09-08.md`),
which used the *same* Asset Opportunity tiers and Dry Powder floor but
*no* FX Benefit or JPY modifiers:

| | Dry-Powder-floor-only NOFLOOR | Full-pipeline FULL_NOFLOOR | Dry-Powder-floor-only WITHFLOOR | Full-pipeline FULL_WITHFLOOR |
|---|---:|---:|---:|---:|
| Final total (KRW) | 513,909,200 | 507,983,000 | 516,268,300 | 513,658,600 |
| CAGR | 7.79% | 7.74% | 7.82% | 7.79% |
| Max drawdown | −28.09% | −28.04% | −20.68% | −20.68% (identical) |

Adding the FX Benefit and JPY caution modifiers on top of the
already-validated Asset-Opportunity + Dry-Powder-floor combination made
**final value and CAGR very slightly worse**, not better, in both the
floor and no-floor cases (roughly 0.05pp of CAGR, under 1.2% of final
value — small, but consistently in the wrong direction, not noise that
happens to average out to zero). Max drawdown was essentially unchanged.
**This run cannot isolate which of FX Benefit or JPY caution individually
caused this** — only that the combination of the two, as specified, did
not improve on Asset Opportunity + Dry Powder floor alone on this
benchmark.

### 5.5 Limitations

- Single benchmark, single asset pair — same caveat as every prior replay
  this session.
- The JPY momentum window (5 weeks here vs. 5 days in the original JPY
  overlay replay) is a cadence adaptation for this weekly-step simulation,
  not a re-validation of the original JPY overlay finding at this cadence.
- All tranche-size, rebalance-cadence, and modifier-bound parameters are
  design choices carried over from earlier replays, not jointly re-fit or
  re-validated as a system.
- FX Benefit and JPY caution are tested here **only as a bundle** — no
  standalone attribution of either piece's individual marginal contribution
  was performed in this run.
- The "buying into the decline" MDD cost is specific to how this
  simulation measures drawdown (mark-to-market of a growing risk-asset
  position); it does not mean the tilted strategies are unsound, only that
  MDD alone is an incomplete lens for comparing a static allocation against
  a tactically-tilted one.

## 6. Action

**This capstone result gives directional support for the engine's core
shape (Asset Opportunity + Dry Powder floor), not blanket validation of
the full five-stage design as specified.** Precisely:

- **Adopt as directionally reasonable:** Asset Opportunity tiers combined
  with the Dry Powder floor — this combination beat BASELINE on CAGR and
  recovered most of the tactical-tilting MDD cost, consistent with the
  standalone Dry Powder floor result.
- **Do not add the FX Benefit and JPY caution modifiers on top, as
  currently specified** — this run shows no benefit and a small
  consistent cost. This does not re-open the earlier FX-accumulation or
  JPY-overlay conclusions (those were tested as standalone triggers on
  their own benchmarks and remain valid there); it specifically means
  layering them as *additional* modifiers on an already-tilted
  Asset-Opportunity + floor strategy did not help *here*.
- **This is not sufficient evidence to treat the Deployment Engine as a
  live-ready system.** One benchmark, one asset pair, un-isolated modifier
  attribution, and several un-refit design parameters mean this remains
  research support for the engine's general shape, not a frozen production
  rule. Per the Investment Research Loop's decision discipline, a second,
  more adversarial benchmark and standalone FX/JPY attribution runs should
  precede any live-capital reliance on this specific configuration.

## 7. Lesson Learned

A capstone "does the whole system work" test surfaced something the
individual-piece replays could not: two pieces (FX Benefit, JPY caution)
that were each independently reasonable in their own narrow replay did not
add value when stacked on top of a different, already-effective
combination (Asset Opportunity + Dry Powder floor). Validating pieces in
isolation does not guarantee they compose well — composition itself needs
to be tested, which is exactly what this end-to-end run did, and it found
a real (if modest) negative interaction. Separately: tactical drawdown
buying trades a worse near-term max-drawdown number for better long-run
CAGR — this is a real trade-off to be explicit about with a capital
allocator, not something a "smarter" modifier combination can eliminate;
only the Dry Powder floor materially softened it in this replay.

## 8. Rule Change

**YES.** Update `docs/governance/PORTFOLIO_DEPLOYMENT_ENGINE_v0.1.md`:

- Section 8's "full five-stage pipeline end-to-end" row: mark **"REPLAYED
  2026-09-08 — Asset Opportunity + Dry Powder floor combination beats
  BASELINE on CAGR (7.79% vs 7.49%) and recovers most of tactical-tilting's
  MDD cost; layering the FX Benefit and JPY caution modifiers on top added
  no benefit and a small consistent cost in this run. Directional support
  only — not sufficient to treat as a live-ready system (single benchmark,
  un-isolated modifier attribution)."** See
  `research/deployment-engine-v0.1-full-pipeline-backtest-result-2026-09-08.md`.
- Add a summary line below section 8's table: all five rows have now been
  replayed at least once as of 2026-09-08. Two guardrails were rejected
  outright (Risk Gate cap), one showed a real benefit (Dry Powder floor),
  and the full combination shows the floor's benefit does not straightforwardly
  extend when more modifiers are stacked on top — the engine's current
  best-supported configuration is **Asset Opportunity tiers + Dry Powder
  floor**, without the Risk Gate cap, and without stacking FX Benefit/JPY
  caution on top, pending further isolated attribution testing.

## 9. Git Commit

**YES** — CI-executed, reproducible capstone replay tying together every
piece validated this session, with documented methodology, results, and
falsification section, per the Auto Commit Policy v0.1.
