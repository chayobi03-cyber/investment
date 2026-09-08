# Deployment Engine v0.1 — Dry Powder 28% Floor Backtest Result

**Date:** 2026-09-08
**Status:** REPLAY RESULT — FLOOR SHOWS A REAL BENEFIT, WORDING NEEDS CLARIFICATION
**Origin:** Tests the last remaining "Not backtested" row in
`docs/governance/PORTFOLIO_DEPLOYMENT_ENGINE_v0.1.md` sections 7 and 8:
the proposed Dry Powder 28% floor.
**Script:** `research/scripts/run_dry_powder_floor_backtest.py`
**CI workflow:** `.github/workflows/dry-powder-floor-backtest.yml`
**Run:** [`34185691923`](https://github.com/chayobi03-cyber/investment/actions/runs/34185691923)
(commit `3a7de42`)

> Research replay only, not a live trading signal.

## 1. Hypothesis

From `PORTFOLIO_DEPLOYMENT_ENGINE_v0.1.md` section 7: "do not let
active-sandbox Dry Powder fall below the Aggressive scenario's 28% floor
without an explicit, separately recorded risk-state decision." The
implicit hypothesis: refusing to deploy a tranche that would breach 28%
should reduce drawdown/exhaustion risk during repeated corrections, at
some cost to upside capture.

## 2. Data

Same S&P 500 (`^GSPC`) / USD-KRW (`KRW=X`) weekly series and window as
`research/fx-accumulation-v0.1-A-vs-B-vs-C-vs-D-replay-2026-09-08.md`
(**2004–2026, 1,134 valid weeks**). This is a **different window** than
the Risk Gate cap backtest (1993–2022-01-10, bounded by Stress Convergence
coverage) — the two results are not directly comparable in magnitude,
only each internally against its own baseline.

Of 1,134 weeks, 333 were drawdown weeks (asset-opportunity tier > 1.0).

## 3. Method

Unlike the FX-accumulation and Risk-Gate-cap replays — which model a
recurring weekly budget added over time — a Dry Powder floor is a **stock**
question: you hold a fixed pool of cash and risk assets and tactically move
money between them. This script simulates a **static-total** portfolio (no
new external contributions):

- Start: KRW 100,000,000 total, split 42% Dry Powder / 58% risk asset
  (the Balanced-scenario Dry Powder target from
  `PORTFOLIO_ALLOCATION_RULE_v0.1.md`).
- Dry Powder earns an assumed 3.5%/year cash yield (Dry Powder =
  CD-rate ETF + cash + SGOV) — **not independently verified against actual
  historical short-rate ETF returns**; a design assumption, not measured.
- Each drawdown week (asset-opportunity tier > 1.0), a tranche is drawn
  from Dry Powder: `2% of the *initial* Dry Powder balance × tier`
  (so 3.0%/4.0%/6.0% of initial Dry Powder at tiers 1.5/2.0/3.0). Using the
  *initial* balance (not the currently remaining one) as the base keeps
  tranche sizes stable and interpretable, and matters for whether the floor
  actually binds.
- **Annual rebalance back to 42/58, but only in a non-drawdown week
  (tier == 1.0).** This is deliberate: over 22 years equities compound
  faster than a 3.5% cash yield, so without periodic rebalancing the Dry
  Powder weight would passively erode from ordinary market appreciation —
  a completely different phenomenon from the crisis-driven depletion this
  backtest is actually meant to test. Never rebalancing mid-drawdown
  preserves the exact dynamic under test.
- **NOFLOOR:** deploy the full tranche, capped only by remaining Dry
  Powder (can reach 0%).
- **WITHFLOOR:** never deploy an amount that would push Dry Powder below
  28% of the current total (`deployed ≤ dry_powder − 0.28 × total`).

## 4. Threshold

28% floor, exactly as specified in section 7 of the governance document.

## 5. Results

| Path | Final total (KRW) | Total return | CAGR | Max drawdown | Min Dry Powder % | Weeks < 28% | Total deployed (KRW) | Total blocked (KRW) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| NOFLOOR | 513,909,200 | +413.8% | 7.79% | **−28.09%** | **0.00%** | 202 | 389,134,600 | 161,065,400 |
| WITHFLOOR | 516,268,300 | +416.1% | 7.82% | **−20.68%** | 24.67% | 173 | 260,283,400 | 289,916,600 |

## 6. Falsification

### 6.1 Did the floor prevent Dry Powder exhaustion?

**Yes, materially.** NOFLOOR's Dry Powder hits **exactly 0%** at some point
in this benchmark — full exhaustion. WITHFLOOR's minimum is 24.67%, well
above zero and only modestly below the nominal 28% target.

### 6.2 Did the floor cost return? No — and it reduced drawdown substantially.

CAGR is essentially identical (7.82% WITHFLOOR vs. 7.79% NOFLOOR — a
0.03 percentage-point difference, within noise, if anything marginally in
WITHFLOOR's favor). **Max drawdown improved from −28.09% to −20.68%, a
~7.4 percentage-point reduction.** This is a materially different outcome
than the Risk Gate cap backtest
(`research/deployment-engine-v0.1-risk-gate-cap-backtest-result-2026-09-08.md`),
where capping intensity cost IRR without any drawdown benefit. Here, the
mechanism is different: NOFLOOR's complete cash exhaustion at the worst
point in a drawdown leaves the portfolio maximally exposed exactly when it
is most vulnerable, amplifying the value-per-invested drawdown; WITHFLOOR's
preserved cash cushion dampens that same trough without giving up
compounding, because the deployment it *does* still make is enough to
capture most of the recovery upside.

### 6.3 The confirmed interpretation ambiguity

WITHFLOOR's minimum Dry Powder % (24.67%) is **below the nominal 28%
floor.** This is not a bug in the deployment-time check — the floor
inequality (`deployed ≤ dry_powder − 0.28 × total`) is algebraically
guaranteed to hold immediately after every deployment decision. Based on
local synthetic-data testing with the same code (where the same pattern
was directly traced week-by-week), this dip below 28% happens **after** a
crisis, during the recovery rally, **before** the next annual rebalance —
risk-asset value grows from price appreciation alone (no new deployment),
which mechanically raises the total and dilutes the Dry Powder percentage,
since Dry Powder itself only earns the flat cash yield. **This session did
not re-extract the real run's per-week CSV to directly confirm the exact
week of the minimum** (the GitHub Actions artifact is on
`productionresultssa19.blob.core.windows.net`, which this session's egress
policy blocks — the same limitation noted in the two prior replay
write-ups); the conclusion above is inferred with high confidence from (a)
the algorithm's provable deployment-time correctness and (b) the identical
qualitative pattern reproduced in local synthetic testing, not from
re-opening this exact run's raw output.

**This confirms a real ambiguity in how the governance document's floor is
worded.** "Do not let Dry Powder fall below 28%" could mean:

1. **Deployment-time constraint (what this backtest implements):** never
   *choose* to deploy an amount that would breach 28%. Compatible with the
   ratio later drifting below 28% from market appreciation alone.
2. **Permanent state constraint:** Dry Powder must never read below 28% at
   any time, which would require an additional **sell-side rule** — trim
   appreciated risk assets back to cash whenever the ratio drifts below the
   floor, not just when a new purchase is being considered. This governance
   framework does not currently define such a rule.

This backtest validates interpretation (1). Interpretation (2) has not been
specified or tested and would be a materially different (and more
complex, tax/cost-sensitive) rule.

### 6.4 Limitations

- Single benchmark (2004–2026 S&P 500 / USD-KRW), single asset pair.
- Tranche-size formula (2% of initial Dry Powder per tier-1.5 drawdown
  week) and the annual, non-drawdown-only rebalance cadence are design
  choices, not fit to data or independently validated against alternative
  cadences/sizes.
- The 3.5%/year cash-yield assumption for Dry Powder is illustrative, not
  measured against actual CD-rate ETF/SGOV historical returns.
- This tests one specific numeric floor (28%, from the Aggressive
  scenario). Sensitivity to the exact floor level (e.g., 20% vs. 35%) is
  untested.

## 7. Action

**Adopt the Dry Powder floor concept, but clarify the governance wording**
to state explicitly that it is a **deployment-time constraint** (this
backtest's interpretation), not a permanent state guarantee, unless and
until a separate sell-side rebalancing rule is proposed and independently
tested. Unlike the Risk Gate cap (rejected — pure cost, no benefit), this
floor showed a real, close-to-free drawdown reduction on this benchmark and
is a reasonable candidate for the working ruleset, with the wording fix
noted above and the standard caveat that one benchmark is not sufficient to
freeze it as a permanent hard rule.

## 8. Lesson Learned

Two guardrails proposed together in the same document (the Risk Gate cap
and the Dry Powder floor) can have opposite validation outcomes when
actually tested — one purely costly, the other close to free. Intuition
("limiting exposure during stress must be prudent") is not a substitute for
replay even when the two mechanisms sound similar; they act on different
parts of the portfolio (an intensity multiplier vs. a cash-balance
constraint) and their outcomes were not alike. Separately: a floor
described only as "do not let X fall below Y%" is ambiguous between a
constraint on new decisions and a constraint on the resulting state — this
should be made explicit in any future guardrail wording in this project.

## 9. Rule Change

**YES.** Update `docs/governance/PORTFOLIO_DEPLOYMENT_ENGINE_v0.1.md`:

- Section 7's Dry Powder floor proposal: add that the floor is a
  **deployment-time constraint** (does not, by itself, guarantee the ratio
  never drifts below 28% between rebalances) and cite this replay.
- Section 8's Dry Powder 28% floor row: mark **"REPLAYED 2026-09-08 —
  showed a real drawdown reduction (−28.1% → −20.7% MDD) at negligible CAGR
  cost on one 2004–2026 benchmark; interpretation clarified as a
  deployment-time constraint, not a permanent state guarantee. Reasonable
  candidate for adoption; not yet a frozen hard rule (single benchmark)."**

No change to the Stress Convergence gate, JPY overlay conclusion, FX
Benefit bounds, or the (separately rejected) Risk Gate cap conclusion.

## 10. Git Commit

**YES** — CI-executed, reproducible replay with documented methodology,
results, and falsification section, per the Auto Commit Policy v0.1.
