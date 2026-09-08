# Portfolio Deployment Engine v0.1

- Date: 2026-09-08
- Status: WORKING BASELINE — NOT A FROZEN HARD RULE
- Scope: makes the decision hierarchy in `docs/governance/PORTFOLIO_ALLOCATION_RULE_v0.1.md`
  section 8 (`Market state → risk/early-warning signals → deployable percentage
  → target bucket → residual Dry Powder`) into an explicit, auditable function,
  per the P2 "Portfolio deployment engine" item in
  `docs/governance/CLAUDE_HANDOVER_2026-09-08.md` section 13.
- Origin: assembled from already-validated/replayed pieces (Stress Convergence
  v0.2.4 TTC gate, the 2026-09-08 JPY overlay AND-gate rejection, and the
  2026-09-08 FX accumulation A/B/C/D replay). **The full cascade below has not
  itself been backtested end-to-end** — see section 8.

> This document defines a decision procedure, not a live trading signal.
> Every input it references (market state, FX levels, portfolio weights)
> must be refreshed from current data before use, never taken from an
> example in this document.

---

## 1. Why this document exists

Prior governance (Portfolio Allocation Rule v0.1, FX-ACCUMULATION RULE v0.2,
the JPY stress-confirmation framework) each define one piece of the decision
chain, but no single document says how they compose into one number: *how
much to deploy, into which bucket, right now.* Without that composition,
the same signals can be read inconsistently across sessions. This document
is that composition layer.

It changes no existing frozen threshold. It only sequences already-defined
rules and makes explicit what was previously implicit or session-dependent.

## 2. The five-stage pipeline

```text
① Market State        → current facts, refreshed every session
② Risk Gate            → Stress Convergence state + JPY confirmation (confidence modifier only)
③ Asset Opportunity     → staging tier from drawdown/valuation depth
④ FX Benefit            → USD/KRW band modifier (bounded, non-gating)
⑤ Portfolio Gap × Concentration Guard → target bucket selection
                        → Deployable % of the planned tranche
                        → Target Bucket
                        → Residual Dry Powder (recomputed, feeds next cycle)
```

Each stage is described below with its current source rule, its current
status (FROZEN / WORKING / PROPOSED-UNVALIDATED), and how it plugs into the
next stage.

---

## 3. Stage ① — Market State

Refresh, every session, per handover section 15's standard check order:
US trading-day/holiday status, last regular session, US futures, UST yields,
oil, USD/KRW + USD/JPY, global equity/semiconductor relative strength.

**Status: WORKING.** No new rule introduced here; this stage is a data
refresh, not a decision.

## 4. Stage ② — Risk Gate

### 4.1 Base signal: Stress Convergence state

Use the frozen v0.2.4 TTC classification
(`research/stress-convergence/README.md`, `R-SC-TTC-001`/`R-SC-TTC-002`):
a state is one of `NORMAL`, `EARLY_WARNING`, `TIGHTENING_STATE`,
`CRISIS_CONFIRMATION`, using the 90-day primary confirmation window.

| Risk Gate state | Deployment posture |
|---|---|
| NORMAL | Full computed intensity from stages ③–⑤ (no cap). |
| EARLY_WARNING | **Cap the Asset Opportunity tier at Stage ≤ 2** (see section 5). Rationale: SC-RUN-0007 / the v0.2.3 daily panel found Early Warning has a high false-alarm rate (6/7 non-crisis false alarms in the 11-window benchmark) — useful for heightened attention, not sufficient alone to justify the largest tranches. |
| TIGHTENING_STATE | Same cap as EARLY_WARNING. Tightening explains rate-driven pressure but the handover explicitly notes it is "금리압력 설명에는 유용, 보편적 위기탐지에는 부족" — not a universal crisis detector, so it does not by itself license larger deployment either. |
| CRISIS_CONFIRMATION | **Pause new discretionary escalation** into Satellite/High-risk and Domestic Equity buckets. Continue only pre-committed Dry-Powder-funded tranches into Fixed Core-adjacent/Hedge buckets at Stage 0 only. Resuming normal staging requires an explicit new session decision, not an automatic reset. |

**Status: WORKING**, built directly from an already-frozen upstream rule
(v0.2.4). The specific caps (Stage ≤ 2 under EW/Tightening; Stage 0-only
under Crisis Confirmation) are new and **PROPOSED-UNVALIDATED** — no replay
has yet tested whether these particular caps improve outcomes versus no cap
or a different cap. Falsify before treating as hard.

### 4.2 JPY overlay: confidence modifier only, never a gate

Per `research/jpy-overlay-v0.1-seven-window-replay-result-2026-09-08.md`,
an AND-gated JPY overlay was replayed and rejected (it collapsed true
positives and lead time). Accordingly:

> JPY/KRW + USD/JPY joint behavior may **adjust confidence** within the
> Risk Gate state already determined by Stress Convergence, but **must
> never**, by itself, upgrade/downgrade the Risk Gate state, and must never
> multiply the Deployable % by more than ±10%.

Concretely: if Stress Convergence says `NORMAL` but JPY/KRW and USD/JPY both
show fresh joint strengthening (the framework's "Level 2 — FX confirmation"),
apply at most a −10% intensity adjustment to stage ③'s output as a caution
flag — never a hard stop, never an escalation to a higher risk posture on
its own.

**Status: WORKING**, directly reflecting the 2026-09-08 replay finding.

## 5. Stage ③ — Asset Opportunity (staging tier)

Reuses the existing staging ladder from Portfolio Allocation Rule v0.1
section 7, applied to the *depth of the relevant bucket's price
opportunity* (e.g., how far the target index/asset is below its recent
high), not to a fixed calendar schedule:

| Stage | Share of the planned tranche |
|---|---:|
| Stage 0 | 0–20% |
| Stage 1 correction | +20% |
| Stage 2 correction | +25% |
| Stage 3 correction | +25% |
| Stress/Panic | final +30% |

The Risk Gate cap from section 4.1 applies here (e.g., under EARLY_WARNING,
Stage 3/Panic tranches are not available even if the price drawdown alone
would justify them).

**On which trigger determines the stage:** the 2026-09-08 FX-accumulation
replay found the asset-price trigger (Strategy B) had better money-weighted
IRR and far better "good window" coverage (miss rate 1/8) than the FX-only
trigger (Strategy C, miss rate 6/8). Accordingly:

> The staging tier is driven primarily by **asset-price drawdown/valuation
> depth**, not by FX level. FX enters only at stage ④, as a bounded modifier.

**Status: WORKING**, informed by an actual replay (not by intuition alone),
but the replay covered exactly one asset pair (S&P 500 / USD-KRW) over one
historical path — extending this conclusion to other buckets (Gold, US
Dividend, Domestic ETF, satellites) is **PROPOSED-UNVALIDATED**.

## 6. Stage ④ — FX Benefit (bounded modifier)

Reuses the FX-ACCUMULATION RULE v0.2 working bands
(`docs/governance/LESSONS_LEARNED_2026-09-07_FX_ACCUMULATION.md` section 4),
converted into an explicit, bounded multiplier on the stage ③ output:

| USD/KRW | Multiplier |
|---:|---:|
| ≥ 1,450 | ×0.3 |
| 1,380–1,420 | ×0.7 |
| 1,340–1,350 | ×1.0 (neutral baseline) |
| 1,320–1,330 | ×1.1 |
| 1,300–1,320 | ×1.2 |
| 1,280–1,300 | ×1.0 (hold at neutral — re-verify market risk before going higher; per governance, extreme KRW strength alone does not justify a larger multiplier) |

Hard bound: this multiplier **may never exceed ×1.2 or go below ×0.3**, and
it applies only to the *timing/intensity* of an already-justified purchase —
it can never, by itself, create Portfolio Gap or override the Risk Gate.

**Status: WORKING**, a direct, bounded translation of the existing v0.2
bands. The bound values (×0.3/×1.2) are **PROPOSED-UNVALIDATED** — chosen to
keep FX a modifier rather than a driver, consistent with the FX
A/B/C/D replay's finding that the FX-only strategy (C) had the worst
money-weighted IRR of the three triggered strategies, but not itself
backtested at these exact multiplier values.

## 7. Stage ⑤ — Portfolio Gap, Concentration Guard, and output

1. **Compute Portfolio Gap** for every functional bucket: `target weight
   (Balanced scenario, Portfolio Allocation Rule v0.1 section 5) − current
   weight`, using the *active-sandbox* denominator only (fixed Samsung core
   excluded — see section 9; the account-reconciliation question that once
   affected this denominator was resolved 2026-09-08).
2. **Rank buckets** by Portfolio Gap, largest underweight first.
3. **Apply the Concentration Guard** (Portfolio Allocation Rule v0.1 section 6)
   before finalizing a target bucket:
   - Skip/reduce Domestic Equity (KODEX 200 / KODEX semiconductor) increases
     while the fixed Samsung core remains ~14–15% of the whole portfolio,
     unless a separate thesis and risk budget are recorded.
   - Treat direct NVIDIA additions as Satellite, not Core, regardless of
     computed gap.
4. **Deployable % for this cycle** = `Stage ③ tranche share × Stage ④ FX
   multiplier × Stage ② Risk Gate cap/pause`, applied to the *planned
   tranche* for the top-ranked eligible bucket (not to the whole Dry Powder
   balance at once).
5. **Target Bucket** = the top-ranked bucket surviving the Concentration
   Guard.
6. **Residual Dry Powder** = Dry Powder balance − amount deployed this
   cycle. Recompute Portfolio Gap from this residual before the next cycle.

### Dry Powder floor (new, unvalidated)

> Proposed floor: do not let active-sandbox Dry Powder fall below the
> **Aggressive scenario's 28% floor** (Portfolio Allocation Rule v0.1
> section 5) without an explicit, separately recorded risk-state decision.

This is a **PROPOSED-UNVALIDATED** guardrail, not yet backtested. Its
purpose is to prevent the staging ladder from mechanically draining Dry
Powder to zero across repeated corrections. It should be replayed (does a
hard floor materially change outcomes on the existing benchmarks?) before
being promoted.

**Status: WORKING** for the ranking/guard/bookkeeping mechanics (these are
direct applications of already-frozen rules); **PROPOSED-UNVALIDATED** for
the Dry Powder floor specifically.

## 8. What has and has not been validated

| Piece | Validation status |
|---|---|
| Stress Convergence v0.2.4 90-day TTC gate | Frozen, replayed (SC-RUN-0007) |
| JPY overlay as confidence-only, not AND-gate | Replayed and rejected-as-gate 2026-09-08 |
| Asset-price trigger > FX-only trigger for staging | Replayed 2026-09-08 (one asset pair, one historical path) |
| FX Benefit bounded modifier (×0.3–×1.2) | **Not backtested** — bound values are a design choice, not a measured optimum |
| EARLY_WARNING/TIGHTENING Stage-≤2 cap (as ×1.5 combined-intensity cap) | **REPLAYED 2026-09-08 — result argues against adopting this specific cap design; not promoted, not permanently rejected.** See `research/deployment-engine-v0.1-risk-gate-cap-backtest-result-2026-09-08.md`: on a 1993–2022 benchmark it cost ~0.1pp of annualized IRR versus no cap while leaving max drawdown statistically unchanged. |
| CRISIS_CONFIRMATION pause-and-require-reset (as ×0.3 forced multiplier) | **REPLAYED 2026-09-08 — same result and same caveat as the row above** (tested together as one combined cap/force design, not separately isolated). |
| Dry Powder 28% floor | **Not backtested** |
| The full five-stage pipeline end-to-end | **Not backtested as a single system** |

Per the Investment Research Loop's decision discipline, none of the
"Not backtested" rows should be treated as a hard rule. The next research
priority for this engine is an end-to-end replay of the full pipeline
against the same style of benchmark used for the FX and JPY replays,
reporting the same metric families (acquisition cost, IRR, max drawdown,
trigger frequency, FP/FN where applicable).

## 9. Portfolio-account reconciliation — RESOLVED 2026-09-08

Stage ⑤'s Portfolio Gap calculation requires the *active-sandbox
denominator*. `docs/governance/CLAUDE_HANDOVER_2026-09-08.md` had flagged a
possible second Samsung Electronics 79-share holding in a separate account
(which would have required recomputing the fixed-core/active-sandbox split).
**User-confirmed 2026-09-08: this was a mistake — Samsung Electronics is
79 shares in a single account, not 158 across two.** The fixed core stays
at 79 shares as originally documented in
`docs/governance/PORTFOLIO_ALLOCATION_RULE_v0.1.md`, and the active-sandbox
denominator structure is unchanged. This stage's Portfolio Gap calculation
is no longer blocked; the usual caveat still applies that current prices
and weights must be refreshed each session, independent of this
reconciliation.

## 10. Session-close record

```text
Lesson Learned: The project had a decision hierarchy stated in prose
(Market State → Risk Signal → Deployable % → Target Bucket → Residual
Dry Powder) but no explicit function computing it. Composing the already-
separately-validated pieces (Stress Convergence gate, JPY-as-modifier,
asset-price-led staging, bounded FX modifier) into one pipeline surfaces
where the real validation gaps are: the caps, the FX modifier bounds, and
the Dry Powder floor are all currently designed, not measured.

Rule Change: YES — this is a new governance document
(PORTFOLIO_DEPLOYMENT_ENGINE_v0.1.md), explicitly marked WORKING and
partially PROPOSED-UNVALIDATED per section 8.

Git Commit: YES — new governance document defining the deployment
decision framework called for in the 2026-09-08 handover's P2 list.
```
