# Deployment Engine v0.1 — Risk Gate Cap Backtest Result

**Date:** 2026-09-08
**Status:** REPLAY RESULT — RISK GATE CAP NOT ADOPTED AS SPECIFIED
**Origin:** Tests the two "Not backtested" rows in
`docs/governance/PORTFOLIO_DEPLOYMENT_ENGINE_v0.1.md` section 8:
the EARLY_WARNING/TIGHTENING_STATE intensity cap and the
CRISIS_CONFIRMATION pause posture.
**Script:** `research/scripts/run_deployment_engine_v0.1_backtest.py`
**CI workflow:** `.github/workflows/deployment-engine-backtest.yml`
**Run:** [`34184771233`](https://github.com/chayobi03-cyber/investment/actions/runs/34184771233)
(commit `c552c47`)

> Research replay only, not a live trading signal.

## 1. Hypothesis

From `PORTFOLIO_DEPLOYMENT_ENGINE_v0.1.md` section 4.1: capping combined
deployment intensity during Stress Convergence `EARLY_WARNING`/
`TIGHTENING_STATE` (at ×1.5) and forcing it down during
`CRISIS_CONFIRMATION` (to ×0.3) should reduce drawdown risk relative to
deploying the same Asset-Opportunity × FX-Benefit tilt with no cap at all,
ideally without giving up too much return.

Three variants, identical weekly benchmark and identical total KRW budget:

- **BASE** — plain fixed periodic accumulation (no tilt).
- **NOCAP** — Asset Opportunity (price-drawdown tiers) × FX Benefit
  (bounded ×0.3–×1.2), no Risk Gate cap.
- **WITHCAP** — same tilt as NOCAP, but capped at ×1.5 combined intensity
  during `EARLY_WARNING`/`TIGHTENING_STATE`, and forced to ×0.3 during
  `CRISIS_CONFIRMATION`.

## 2. Data

- Same Stress Convergence state definitions as
  `research/scripts/run_v0.2.3_daily_panel.py` (`EARLY_WARNING`,
  `TIGHTENING_STATE`, `CRISIS_CONFIRMATION`), reused verbatim.
- S&P 500 (`^GSPC`) and USD/KRW (`KRW=X`) from Yahoo Finance, joined to the
  same daily panel, resampled to weekly (`W-FRI`).
- **Window: 1993-01-01 to 2022-01-10 — 1,052 valid weekly observations.**
  This is bounded by the v0.2.3 Stress Convergence definitions' coverage
  and is **not the same window** as
  `research/fx-accumulation-v0.1-A-vs-B-vs-C-vs-D-replay-2026-09-08.md`
  (which used 2004–2026). **Results here are not directly comparable in
  magnitude to that replay — only the relative ranking of BASE/NOCAP/WITHCAP
  within this run is meaningful.**
- Of 1,052 weeks: 176 were `EARLY_WARNING`/`TIGHTENING_STATE`, 40 were
  `CRISIS_CONFIRMATION`.

## 3. Thresholds

- Asset Opportunity tiers: identical to the FX-accumulation replay's
  Strategy B (drawdown from trailing 52-week high: 1.0/1.5/2.0/3.0×).
- FX Benefit: bounded ×0.3–×1.2 per `PORTFOLIO_DEPLOYMENT_ENGINE_v0.1.md`
  section 6 (narrower than the FX-accumulation replay's ×0.7–×2.0 — this
  engine deliberately treats FX as a smaller modifier).
- Risk Gate cap: `min(combined, 1.5)` during EW/Tightening;
  `combined = 0.3` (forced, not capped) during Crisis Confirmation.

## 4. Results

| Strategy | Total invested (KRW) | Final value (KRW) | Total return | Annualized IRR | Avg. acquisition cost | Max drawdown | Invested during Crisis Confirmation (KRW) |
|---|---:|---:|---:|---:|---:|---:|---:|
| BASE | 1,052,000,000 | 2,946,443,000 | +180.1% | **9.30%** | 2,001,523 | −28.11% | 40,000,000 |
| NOCAP | 1,052,000,000 | 3,223,384,000 | +206.4% | **9.44%** | 1,829,559 | −28.21% | 78,938,010 |
| WITHCAP | 1,052,000,000 | 3,093,978,000 | +194.1% | **9.34%** | 1,906,081 | −28.22% | 10,598,380 |

## 5. Falsification

### 5.1 Did the cap mechanically work?

**Yes.** `invested_during_crisis_confirmation_krw` drops from
78.9M (NOCAP) to 10.6M (WITHCAP) — the ×0.3 force during
`CRISIS_CONFIRMATION` clearly suppressed buying in those weeks as designed.
This confirms the implementation is not buggy; the cap does what it says.

### 5.2 Did the cap reduce drawdown? No.

Max drawdown is **statistically indistinguishable across all three
strategies**: −28.11% (BASE), −28.21% (NOCAP), −28.22% (WITHCAP). WITHCAP's
drawdown is not better than NOCAP's — if anything it is marginally worse
(by 0.01 percentage points, well within noise). **The cap did not deliver
its stated purpose** (reduce drawdown risk during stress states).

### 5.3 Did the cap cost return? Yes.

IRR ranks **NOCAP (9.44%) > WITHCAP (9.34%) > BASE (9.30%)**. WITHCAP sits
between the uncapped tilt and doing nothing extra — it captured only part
of NOCAP's improvement over BASE. The reason is visible directly in section
5.1: NOCAP invested nearly 2× the proportional base amount during Crisis
Confirmation weeks (78.9M vs. an equal-weighted ~38M share of the budget),
and this benchmark's Crisis Confirmation weeks evidently coincided with
favorable (cheap) KRW-cost acquisition points often enough that suppressing
that buying reduced compounding, without buying any drawdown protection in
return.

### 5.4 Interpretation

On this specific 1993–2022 benchmark, **the Risk Gate cap as specified is a
pure cost with no measured benefit**: it gives up ~0.1 percentage points of
annualized IRR and ~35–40% of NOCAP's total-return improvement over BASE,
while leaving max drawdown unchanged. This does not mean "never limit
buying during Crisis Confirmation" — it means *this specific* all-weeks,
mechanically-forced ×0.3 design, tested once, does not show the protective
benefit it was designed for.

### 5.5 Limitations

- **Single window, single asset pair.** Per the Investment Research Loop's
  decision discipline, one backtest does not confirm or permanently reject
  a design — it is evidence, not proof.
- **Max drawdown here is measured on a "value per KRW invested" curve**
  (same method as the FX-accumulation replay), which is influenced by the
  accumulation path, not a pure mark-to-market drawdown of a fixed position.
  Because all three curves show nearly identical MDD, this caveat doesn't
  change the conclusion here, but it means "unchanged drawdown" should not
  be read as "unchanged risk" in every possible sense (e.g., this doesn't
  measure cash-flow-timing risk or realized volatility of returns).
- **The specific numeric choices (×1.5 cap, ×0.3 force)** were design
  choices in the original governance document, not derived from any prior
  measurement — this replay tests those exact numbers, not the general
  concept of "some cap." A differently-tuned cap might behave differently;
  this result should not be read as closing the door on all possible
  Risk-Gate-cap designs.
- **Crisis Confirmation weeks being "good buying weeks" in this sample is
  itself a single-benchmark observation**, consistent with the project's
  broader FX-accumulation lesson that suppressing purchases during
  drawdowns/stress can hurt long-run compounding — but this should be
  weighed against the capital-preservation-first objective in `README.md`,
  which explicitly does not optimize for raw CAGR alone. A cap could still
  be worth its cost if the project's risk tolerance values the (untested-here)
  psychological/liquidity benefits of not deploying capital during confirmed
  stress, even without a measured drawdown benefit — that is a values
  question this replay cannot answer by itself.

## 6. Action

- **Do not adopt the ×1.5/×0.3 Risk Gate cap as a hard rule.** On this
  benchmark it cost return without measurably reducing drawdown.
- Do not conclude the opposite either (i.e., "never cap deployment during
  stress") — this is one benchmark, one asset pair, and one specific
  numeric design.
- If the Risk Gate concept is worth keeping, the next iteration should test
  alternative designs — e.g., a cap that only reduces the *upper* extreme of
  the tilt (leaving baseline accumulation intact) rather than forcing the
  whole multiplier down, or a cap calibrated from this benchmark's own
  distribution rather than picked a priori — before being retested.

## 7. Lesson Learned

A risk-reduction mechanism should be judged by whether it actually reduces
the risk metric it targets, not by whether it "sounds prudent." Here, a cap
explicitly designed to reduce drawdown during confirmed stress states left
drawdown unchanged while reducing returns — the intuition that "buy less
during confirmed crises must be safer" did not hold on this benchmark,
because those weeks were disproportionately good KRW-cost acquisition
points. This is consistent with, and reinforces, the FX-accumulation
replay's finding that timing-sensitive (IRR) and cost-based metrics can
diverge from intuition, and that this project's guardrails need to be
replayed, not merely reasoned about.

## 8. Rule Change

**YES, narrow.** Update
`docs/governance/PORTFOLIO_DEPLOYMENT_ENGINE_v0.1.md` section 8:

- `EARLY_WARNING`/`TIGHTENING` Stage-≤2 cap → mark **"REPLAYED 2026-09-08 —
  result argues against adopting this specific cap design (see
  `research/deployment-engine-v0.1-risk-gate-cap-backtest-result-2026-09-08.md`);
  not promoted, not permanently rejected."**
- `CRISIS_CONFIRMATION` pause-and-require-reset → same status/citation.

No change to the frozen Stress Convergence v0.2.4 gate, the FX-accumulation
bands, or the JPY overlay conclusion.

## 9. Git Commit

**YES** — CI-executed, reproducible replay with a documented methodology,
result table, and falsification section, per the Auto Commit Policy v0.1.
