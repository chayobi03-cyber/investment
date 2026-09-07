# Investment Project — Claude Handover Package

**Handover date:** 2026-09-07  
**Repository:** `chayobi03-cyber/investment`  
**Default branch:** `main`  
**Purpose:** Enable Claude to take over the investment research project without rebuilding context from chat history.

---

## 0. Start Here — Operating Directive

You are taking over an existing investment research system. Do **not** treat this as a blank-slate portfolio-advice task.

Your first job is to preserve the existing research contract, understand the current state, identify what is validated versus provisional, and then continue the next unresolved experiment.

### Mandatory first-read order

1. `README.md`
2. `docs/governance/INVESTMENT_RESEARCH_LOOP.md`
3. `docs/governance/PORTFOLIO_ALLOCATION_RULE_v0.1.md`
4. `docs/governance/LESSONS_LEARNED_2026-09-07_FX_ACCUMULATION.md`
5. `docs/research/NARRATIVE_VALIDATION_WORKFLOW_v0.1.md`
6. `research/stress-convergence-v0.2.3-three-stage-daily-panel-2026-09-02.md`
7. `docs/research/market/2026-09-03-jpy-stress-confirmation-framework.md`
8. `docs/research/anthropic/ANTHROPIC_IPO_FX_INDIRECT_EXECUTION_2026-09-06.md`

Then inspect the latest Git history before making any methodological change.

### Non-negotiable research principles

- Capital preservation and long-term risk-adjusted compounding have priority over raw return maximization.
- Investment research is hypothesis-driven and falsifiable.
- Narrative is an input to investigation, not confirmation evidence.
- Backtest success alone does not justify deployment; falsification must follow.
- Do not optimize thresholds merely to fit historical results.
- Separate observation, evidence, interpretation, decision rule, and execution.
- Keep fixed/non-sellable holdings separate from the active reallocation denominator.
- Track economic overlap, not only ticker labels.
- Current market facts must be refreshed from current sources; repository snapshots are not live data.
- Material methodology/results/rule changes must be committed to Git.

---

## 1. Project Mission

This repository is a research program for a **capital-preservation-oriented public-equity investment system**.

Current milestone gates:

- **M0:** Risk Contract
- **M1:** Data Integrity
- **M2:** Portfolio Risk Engine
- **M3:** Asset Allocation Backtest

No strategy should be promoted through a gate while an upstream gate is not GREEN.

The project is not trying to predict every market move. It is trying to build a repeatable decision system that:

1. detects changing risk conditions early,
2. distinguishes early warning from actual damage,
3. deploys capital progressively rather than emotionally,
4. uses FX as an execution modifier rather than a standalone forecast,
5. preserves optionality and liquidity,
6. records evidence and failures so that the system improves over time.

---

## 2. Standard Research Loop

Every material research task follows:

```text
Hypothesis
  ↓
Minimum Data / Sources
  ↓
Quantitative Threshold (where applicable)
  ↓
Historical Replay / Backtest
  ↓
Falsification / Counterexamples
  ↓
Explicit Action or Monitoring Rule
  ↓
Lesson Learned
  ↓
Rule Change? YES / NO
  ↓
Git Commit? YES / NO
```

Required session-close record:

```text
Lesson Learned: <what changed>
Rule Change: YES / NO — <reason>
Git Commit: YES / NO — <artifact/reason>
```

---

## 3. Evidence and Source Discipline

Preferred hierarchy:

| Tier | Source class | Default use |
|---|---|---|
| S1 | Central banks, governments, statistical agencies, Treasury, SEC/company filings | Primary facts |
| S2 | Reuters, Bloomberg, FT, WSJ and equivalent | High-quality reporting / interpretation |
| S3 | Bank / institutional research with methodology | Analytical mechanism |
| S4 | Specialist finance/economics publications | Supporting context |
| S5 | General financial media | Narrative discovery |
| S6 | Individual commentary/social posts | Low-weight hypothesis input only |

For every material narrative claim:

1. extract testable claims,
2. search direct confirmation,
3. search the mechanism,
4. search counter-evidence,
5. search historical analogues,
6. check source independence,
7. compare against observable market evidence,
8. check for mechanical/non-discretionary flows,
9. test cross-asset convergence,
10. align time windows before classification.

Do not count multiple articles that reproduce one wire report or original note as independent evidence.

---

## 4. Current Portfolio Architecture

### Fixed Core

- Samsung Electronics: **79 shares**
- Working value in the 2026-09-07 portfolio review: about **KRW 15.50M**
- Whole-portfolio weight: about **14.6%**
- Treatment: **HOLD / excluded from the active reallocation sandbox**

### Active Allocation Sandbox

Working assets: about **KRW 90.41M**, or about **85.4%** of whole portfolio.

Functional buckets:

1. **Dry Powder** — CD-rate ETF + cash + SGOV
2. **Hedge** — gold + JPY
3. **US Core/Growth** — S&P 500 + Nasdaq-100 + NVIDIA
4. **US Dividend** — US Dividend Dow Jones + SCHD
5. **Domestic Equity** — KODEX 200 + KODEX semiconductor and other adjustable Korean equity positions
6. **Satellite/Risk** — India + Rigetti + other small high-risk positions

### Current working snapshot

| Bucket | Active-sandbox weight | Approx. value |
|---|---:|---:|
| Dry Powder | 52.0% | KRW 47.01M |
| Gold | 11.4% | KRW 10.31M |
| US Core/Growth | 13.5% | KRW 12.21M |
| US Dividend | 11.5% | KRW 10.40M |
| Domestic ETF | 6.5% | KRW 5.88M |
| India | 2.3% | KRW 2.08M |
| High-risk satellite | 1.2% | KRW 1.08M |
| JPY | 0.9% | KRW 0.81M |
| Other | 0.7% | KRW 0.63M |

**Important calculation correction:** “52% defensive” is incomplete. 52.0% is **Dry Powder only**. Dry Powder + gold is about **63.4%** (JPY excluded). Future records must define the denominator and bucket explicitly.

### Working target

Balanced allocation is currently the default working target unless a later validated risk-state rule overrides it.

- Dry Powder: 42%
- Gold: 10%
- US Core/Growth: 22%
- US Dividend: 11%
- Domestic ETF: 7%
- India: 2%
- High-risk satellite: 3%
- JPY: 1%
- Other: 2%

Current implication:

- reduce Dry Powder by roughly **KRW 9.04M** over time,
- increase US Core/Growth by roughly **KRW 7.68M** over time,
- do not force exact one-day rebalance.

Working staging rule for the planned deployment:

- Stage 0: 0–20%
- Stage 1 correction: +20%
- Stage 2 correction: +25%
- Stage 3 correction: +25%
- Stress/panic: final +30%

Exact triggers are intentionally **not frozen yet**. They must be linked to market-state/risk/FX evidence.

### Concentration constraints

- Samsung Electronics is already a large fixed Korean semiconductor exposure.
- Do not mechanically increase Korean semiconductor exposure while that fixed core remains large without a separate thesis and risk budget.
- NVIDIA is already indirectly held through broad US indices; direct NVIDIA exposure is a satellite rather than a separate core bucket.

---

## 5. FX Rule — Current Working Version

The key lesson from 2026-09-07 is:

> **FX weakness of USD/KRW (KRW strengthening) is not a sell signal for existing foreign assets. It is an execution-friendly condition for acquiring foreign assets more cheaply in KRW terms.**

However, FX is **not** a standalone buy signal.

Current conceptual rule:

```text
Buy Intensity
= Portfolio Gap × Asset Opportunity × Risk Gate × FX Benefit
```

Do not freeze actual weights or numeric multipliers until replay validates them.

### Decision order

1. Portfolio Gap — is the foreign-asset bucket below target?
2. Asset Opportunity — is the asset price in a reasonable accumulation zone?
3. Trend / Risk — is the risk regime compatible with adding risk?
4. FX Benefit — does the currency improve the KRW acquisition price?
5. Cash Budget — can the purchase be made without violating liquidity/risk limits?

### Operational FX bands (provisional triggers, not forecasts)

| USD/KRW | Working role |
|---:|---|
| 1,340–1,350 | 1st accumulation zone |
| 1,320–1,330 | consider increasing tranche |
| 1,300–1,320 | consider stronger accumulation |
| 1,280–1,300 | extreme KRW strength; verify market risk before adding more |
| 1,380–1,420 | reduce new USD purchase size |
| >1,450 | strictly limit new USD purchases; focus on existing foreign assets |

Longer-term validation should use distribution/rolling percentile, rate of change, and joint asset-price behavior rather than fixed absolute bands alone.

### Required falsification experiment

Replay the same historical benchmark under:

- **A:** flat periodic contribution,
- **B:** asset-price trigger,
- **C:** FX trigger,
- **D:** `FX × asset price × portfolio gap` combined trigger.

Evaluate:

- false positives (오탐),
- false negatives (미탐),
- early detection time (조기 탐지 시간),
- trigger frequency (경보 발생 횟수),
- acquisition cost,
- cumulative return / CAGR,
- maximum drawdown,
- cash depletion path.

The criterion is not “highest return”. It is a joint judgment on return, risk, alert stability, and liquidity.

---

## 6. JPY Overlay

JPY/KRW is a **secondary stress-confirmation indicator**, not a standalone crisis or buy signal.

Frozen observation levels for 100 JPY/KRW:

- 850
- 875
- 900
- 925
- 950

These are observation thresholds, not trade triggers.

Frozen temporal horizons:

- 1 day
- 7 days
- 30 days
- **90 days (primary operating horizon)**
- 365 days

A useful JPY confirmation requires agreement with independent evidence. Current candidate rule:

> Use **JPY/KRW + USD/JPY jointly** as the FX confirmation pair; do not treat JPY alone as global crisis evidence.

The overlay must be rejected if it materially increases false positives without reducing false negatives, adds no incremental information, is repeatedly confused with BOJ-specific repricing, or loses performance when the observation horizon changes.

The frozen temporal attribution rule remains authoritative and is not to be retroactively modified.

---

## 7. Stress Convergence — Current Research State

Three states must remain conceptually separate:

- **Early Warning** = macro stress is building
- **Tightening State** = rate/policy pressure is significant
- **Crisis Confirmation** = actual market/credit damage is appearing

The 2026-09-02 11-window daily-panel replay found:

| State | Main result | Interpretation |
|---|---|---|
| Early Warning | 0/4 crisis misses; 6/7 non-crisis false-alarm windows | Early, but too noisy for direct action |
| Tightening State | 1/4 crisis misses; 5/7 false-alarm windows | Useful to describe rate pressure, not universal crisis detection |
| Crisis Confirmation | 3/4 crisis misses before selected anchors; 1/6 evaluable non-crisis false-alarm windows | Specific but too late / sparse for universal confirmation |

Decision: **do not promote any one state as a single final action rule yet.**

Next research task from the frozen record:

> Freeze a rule for how long after Early Warning a Crisis Confirmation remains attributable, then rerun the same 11 windows.

Methodological caution:

- daily-panel replay is not a real-time publication-vintage backtest,
- HY OAS coverage is incomplete for 1994,
- the 11 windows are an adversarial benchmark rather than a population-wide estimate,
- “alert-start events” are state starts inside the windows, not a generic daily alarm rate.

---

## 8. Narrative Validation

The narrative-validation workflow is a frozen external validation layer.

Key separation:

1. **Narrative Strength**
2. **Evidence Strength**
3. **Crisis Confirmation**

Never collapse these into one risk label.

Mechanical/non-discretionary flow attribution must be checked before interpreting capital-flow statistics as investor sentiment.

A persuasive market article can create a hypothesis. It cannot by itself confirm systemic stress.

---

## 9. Anthropic / AI-IPO Workstream

Current classification from the 2026-09-06 research record:

- Narrative Strength: **HIGH**
- Evidence Strength: **MODERATE-HIGH**
- Crisis Confirmation: **NONE**

The workstream must keep these layers separate:

- Anthropic valuation thesis
- AI-capex thesis
- public-company proxy earnings thesis
- USD/KRW thesis
- JPY/KRW risk-regime thesis

Do not treat indirect proxy ownership as direct Anthropic exposure.

Next decisive data gate: the first public Anthropic S-1/prospectus. At that point replace estimates with filing data for revenue, gross margin, operating losses, cash flow, capex/commitments, customer concentration, SBC, share count/dilution, use of proceeds, strategic investor arrangements, and IPO price range.

Then test valuation scenarios around:

`$1.0T / $1.25T / $1.5T / $1.75T / $2.0T`

against forward revenue and gross-profit multiples.

---

## 10. Latest Repository State (2026-09-07)

Recent material commits include:

- `e6149d9` — refine FX accumulation rule v0.2
- `8e80ecf` — register 2026-09-07 FX accumulation lesson learned
- `b20ab13` — add portfolio allocation baseline v0.1
- `dc6cdfc` — amend narrative workflow for mechanical-flow attribution
- `6c669e9` — add Anthropic IPO FX execution record
- `8f6f236` — add Anthropic IPO FX indirect framework
- `7a3fcfb` — add JPY secondary stress-confirmation framework
- `f9fe7e8` — add stress-convergence reproducibility layer and v0.2.4 TTC validation

### Repository status interpretation

The project has a functioning governance/research scaffold and several validated research artifacts, but the final portfolio deployment engine is **not yet fully frozen**.

Do not infer “strategy complete” from the volume of documents.

---

## 11. Immediate Open Work

Priority order for the next Claude session:

### P0 — FX accumulation replay

Run the frozen same-period comparison of A/B/C/D above using a common benchmark, common data frequency, and explicit cash-budget assumptions.

Minimum outputs:

- acquisition cost,
- drawdown,
- CAGR/cumulative return,
- cash path,
- false positives / false negatives,
- lead time,
- trigger frequency,
- sensitivity to threshold definitions.

### P1 — Stress Convergence temporal attribution

Freeze the post-Early-Warning attribution window and rerun the identical 11-window benchmark.

Do not change the historical windows at the same time as changing the attribution rule.

### P1 — JPY overlay replay

Add JPY/KRW + USD/JPY as a secondary discriminator and quantify incremental impact on false positives, false negatives, lead time and trigger frequency.

### P2 — Portfolio deployment engine

Translate:

`Market state → risk signals → deployable % → target bucket → residual Dry Powder`

into explicit, auditable staged-deployment rules.

### P2 — Anthropic public-filing gate

Do not upgrade the thesis based on headlines before the first public S-1/prospectus is available.

---

## 12. What Claude Must Not Do

- Do not use FX alone to trigger a large buy.
- Do not sell existing foreign assets merely because USD/KRW fell.
- Do not call JPY strength a crisis without cross-asset confirmation.
- Do not treat a single article or repeated wire copies as independent evidence.
- Do not call a strategy validated because a backtest has attractive returns.
- Do not tune thresholds to the historical benchmark and then claim out-of-sample robustness.
- Do not mix fixed Samsung Electronics shares into the active reallocation denominator.
- Do not call Dry Powder + gold “52%” without defining the bucket.
- Do not treat ANTW or other public proxies as direct Anthropic ownership.
- Do not overwrite frozen historical records when testing a new methodology; create a new version/artifact.
- Do not silently replace missing primary data with lower-quality sources.
- Do not make current-market claims from this handover document without refreshing the current data.

---

## 13. Required Deliverable Format for Material Research

For each substantive research output, use this structure:

```text
1. Question / Hypothesis
2. Current Evidence
3. Mechanism
4. Counter-Evidence / Falsification
5. Quantitative Test
6. Result
7. Investment Interpretation
8. Action Rule or Monitoring Rule
9. Limitations
10. Lesson Learned
11. Rule Change: YES / NO
12. Git Commit: YES / NO
```

Keep “observation” and “decision” separate. If a result is not robust enough for deployment, explicitly label it **research only / not promoted**.

---

## 14. Claude Session Boot Prompt

Copy the following into a new Claude session after opening this repository:

```text
You are taking over the Investment — Capital Preservation Research project.

Repository:
https://github.com/chayobi03-cyber/investment

Read this file first:
docs/governance/CLAUDE_HANDOVER_2026-09-07.md

Then read the mandatory first-read files listed in Section 0.

Operating rules:
- preserve the existing governance contract;
- do not treat research snapshots as live market data;
- use current primary/high-quality sources for current claims;
- formulate falsifiable hypotheses;
- test mechanisms and explicit counter-evidence;
- keep Early Warning, Tightening State and Crisis Confirmation separate;
- treat USD/KRW as a foreign-asset acquisition modifier, not a standalone trade signal;
- treat JPY as a secondary stress discriminator, not a standalone crisis signal;
- exclude the fixed 79-share Samsung Electronics core from the active reallocation denominator;
- distinguish Dry Powder from Hedge and do not conflate their percentages;
- do not promote a backtest without falsification and liquidity/risk review;
- preserve frozen benchmark windows when changing only one methodological variable;
- create a new versioned artifact rather than rewriting historical evidence;
- at the end of every material session record Lesson Learned, Rule Change, and Git Commit.

First task unless a newer explicit user instruction supersedes it:
1) inspect the latest Git history;
2) identify the current open P0/P1 research item;
3) verify whether the required data are available and current;
4) execute the smallest reproducible next experiment;
5) report result, failure modes, and whether the rule should or should not change;
6) commit any material reproducible artifact to Git.
```

---

## 15. Handover Acceptance Criteria

Claude takeover is considered successful only when it can answer these five questions without relying on chat-history reconstruction:

1. **What is the portfolio architecture?**  Fixed Samsung core vs active sandbox, with functional buckets.
2. **What is the current FX rule?**  KRW strength improves foreign-asset acquisition conditions but cannot trigger buys alone.
3. **What is the current stress-detector status?**  Three states have different jobs; no single state is promoted as the final action rule.
4. **What is the next experiment?**  FX A/B/C/D replay and/or frozen temporal attribution depending on the latest completed artifact.
5. **What happens at session close?**  Lesson Learned → Rule Change decision → Git Commit decision.

---

## 16. Provenance

This handover package was synthesized from the current repository state and the latest material governance/research artifacts as of 2026-09-07. It is an onboarding/index artifact, not a replacement for the source documents referenced above.

Source-of-truth documents include:

- `README.md`
- `docs/governance/INVESTMENT_RESEARCH_LOOP.md`
- `docs/governance/PORTFOLIO_ALLOCATION_RULE_v0.1.md`
- `docs/governance/LESSONS_LEARNED_2026-09-07_FX_ACCUMULATION.md`
- `docs/research/NARRATIVE_VALIDATION_WORKFLOW_v0.1.md`
- `research/stress-convergence-v0.2.3-three-stage-daily-panel-2026-09-02.md`
- `docs/research/market/2026-09-03-jpy-stress-confirmation-framework.md`
- `docs/research/anthropic/ANTHROPIC_IPO_FX_INDIRECT_EXECUTION_2026-09-06.md`

**Status:** HANDOVER READY / RESEARCH CONTINUES
