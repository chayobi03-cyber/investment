# Entry Gate & Price-Move Attribution — 냉정 감사 v0.1

Date: 2026-09-22
Audited commit: 0213ea6a90d92638610f4f480e3b672bfe077b93
Status: RESEARCH AUDIT — NO LIVE RULE PROMOTION

## 1. Audit conclusion

The Entry Gate v1.0 concept is directionally correct, but the current repository is still spec-first / implementation-incomplete.

The most important finding is not a missing indicator. It is a measurement-definition gap:

- the new rule requires 1/3/5/20D returns, multi-horizon trend distance, weekly state, pullback structure, rebound/breakout state, relative strength, attribution evidence, confidence, persistence and catalyst age;
- the current market monitor actually records mostly one-observation change percentages and state buckets;
- therefore the new Entry Gate cannot yet be reproduced from the current runtime state, and a PIT backtest cannot be trusted until the observation schema is expanded.

The rule should remain RESEARCH and the original frozen contract should not be rewritten from these preliminary results.

## 2. Existing rule strengths

Keep these architectural decisions:

1. Opportunity and market permission are separated.
2. Price extension is treated as an entry-timing problem, not as a company-quality score.
3. Attribution uses an explicit unresolved state rather than forcing a story.
4. PIT fields include observed_at, available_at, source, revision status and rule version.
5. Promotion is blocked until OOS / walk-forward / robustness validation.

## 3. Current implementation gaps

### G1. Historical state is not collected

Current poll.py fetches a short chart and stores latest price/previous price/change, but it does not persist the required 1D/3D/5D/20D/60D/120D feature vector.

Impact: the Entry Gate cannot be reconstructed from stored observations.

### G2. Trend is currently one-day movement, not trend

The current TREND is built from the average of KOSPI/NASDAQ/SOX one-observation changes.

Missing:
- multi-horizon return;
- MA slope/alignment;
- drawdown state;
- acceleration/deceleration;
- persistence.

### G3. Breadth is a watchlist proxy

The current breadth calculation is the fraction of configured leaders that are up.

This is not true market breadth:
- no A/D;
- no percentage above MA;
- no new-high/new-low breadth;
- no sector participation breadth.

It must remain explicitly labelled breadth_proxy until a broader universe is available.

### G4. Macro direction is lost

The current helper uses absolute percentage change to assign GREEN/AMBER/RED.

That means, for example, a large fall in Treasury yield and a large rise in Treasury yield can both become RED.

For entry permission this is structurally insufficient.

Required replacement: signed direction + magnitude + persistence, preferably normalized within each series.

### G5. Data freshness is aggregated too coarsely

DATA_QUALITY currently uses the newest observation timestamp across the whole payload.

A fresh symbol can therefore mask a stale symbol.

Required:
- freshness per field/series;
- missingness count;
- conflict state;
- source timestamp and availability timestamp per observation.

### G6. Attribution is not implemented

GEO is currently N/A, and no company/sector/macro/technical attribution evidence object is generated.

Therefore the new attribution rule is currently a research schema, not an executable detector.

### G7. Buy state is not actually calculated

BUY_TRIGGER remains UNCONFIRMED.

The monitor is not yet the Entry Gate engine; it is a raw-state collector/event detector boundary.

### G8. Alert logic can miss a single critical macro change

Current P1 logic requires state changes and a minimum number of changes. A materially important single-axis rate/FX/oil change does not have a sufficiently explicit hard-event path.

Macro shock detection should be separated from generic alert aggregation.

## 4. Variable audit — keep / add / defer / drop

| Variable | Decision | Role | Reason |
|---|---|---|---|
| Drawdown from 20/60/120D high | KEEP + ADD | Entry location | directly defines dislocation; required for price-zone logic |
| 20/50/200D MA distance | KEEP, but SOFT | Context / extension | useful state descriptor; not proven as universal gate |
| 1/3/5/20D return | KEEP + ADD | Extension | essential to detect acceleration/chase; direction must be tested |
| Consecutive up/down sessions | KEEP as RISK FLAG | Chase detector | preliminary data showed mixed forward-return direction across names |
| Distance to 20D high | KEEP as SOFT FLAG | Chase/context | mixed results; should not be a hard veto by itself |
| Pullback depth + duration | ADD | Entry structure | separates healthy consolidation from prolonged weakness |
| Rebound/breakout state | ADD | Entry structure | tests reversal quality instead of single-day reversal |
| Gap / overnight return | ADD | Event detector | helps separate event shock from continuous trend |
| Volume / turnover anomaly | KEEP as EVIDENCE | Attribution | useful to corroborate event/flow, not yet suitable as a standalone gate |
| Sector relative strength | ADD / HIGH PRIORITY | Leadership | directly addresses capital-return hypothesis |
| Market relative strength | ADD / HIGH PRIORITY | Leadership | prevents confusing market beta with stock-specific strength |
| Breadth (% above MA, A/D, NH/NL) | ADD / HIGH PRIORITY | Market confirmation | current watchlist breadth is only a proxy |
| Volatility regime | ADD | Risk | level + change + persistence should be explicit |
| Credit stress | ADD / HIGH PRIORITY | Systemic risk | useful independent shock cluster |
| Signed rates shock | ADD / HIGH PRIORITY | Macro gate | current absolute-change implementation loses direction |
| Signed FX shock | ADD / HIGH PRIORITY | Macro gate | same issue as rates |
| Signed oil shock velocity | ADD / HIGH PRIORITY | Macro gate | level alone is weaker than shock speed + persistence |
| Cross-asset dislocation / correlation | ADD | Transmission | tests whether shocks are propagating across assets |
| Geopolitical headline label | DEFER as score | Attribution context | preserve as event evidence only; do not score raw headline sentiment |
| Geopolitical market transmission | ADD | Attribution / risk | preferred observable representation |
| Catalyst date + age | ADD | Attribution | necessary to distinguish event-driven from persistent moves |
| Attribution confidence | KEEP | Evidence gate | prevents invented causal explanations |
| Expected persistence | REPLACE | Evidence state | current wording is forward-looking/subjective; use observed persistence instead |
| Valuation percentile | DEFER from Entry Gate | Slow fundamental context | useful for opportunity sizing, not yet justified as timing gate |
| Gold as standalone gate | DEFER | Cross-asset context | useful hedge/risk context, not a proven universal buy-permission variable |
| WTI + Brent as separate weights | MERGE | Cluster control | duplicate Energy information |
| DXY + USD/KRW + USD/JPY as separate full weights | MERGE | Cluster control | correlated Dollar/FX exposures |
| SOX + semiconductor ETF + leader returns | MERGE | Leadership cluster | correlation control required |

## 5. Actual-data preliminary test

Data source used for the empirical sanity check: connected Alpaca IEX daily bars, primarily 2022-09-01 through 2026-08-27 (1,000 trading-day retrieval limit in this run).

Test assets: AAPL, MSFT, NVDA, AMD, AVGO, META.

Execution convention: decision at observation close; return measured from the next session open to the close 20 trading days later.

This is screening evidence, not validation. It is not a promotion-grade backtest.

### 5.1 Short-term extension

Using the upper-quartile 5D return as an extension flag, the 20D forward-return effect was not directionally stable across the six names.

Examples from the run:
- AAPL: upper-quartile extension +1.23% vs remainder +2.21%.
- MSFT: +2.10% vs +1.68%.
- NVDA: +2.36% vs +4.73%.
- AMD: +7.57% vs +5.03%.
- AVGO: -0.24% vs +4.39%.
- META: +5.02% vs +3.71%.

Conclusion: do not turn 5D extension into a universal alpha signal. Keep it as an input to chase-risk/context and validate jointly with price location.

### 5.2 Four or more consecutive up sessions

Again, the direction was mixed:
- AAPL: +0.88% vs +2.05%.
- MSFT: +0.41% vs +1.90%.
- NVDA: +3.70% vs +4.18%.
- AMD: +14.14% vs +5.03%.
- AVGO: +0.79% vs +3.48%.
- META: -1.96% vs +4.62%.

Conclusion: consecutive_up_sessions is not a universal veto variable. It is useful as a risk flag because it identifies extension episodes, but the threshold needs episode-level validation.

### 5.3 Close within 2% of 20D high

Direction was also mixed:
- AAPL +1.79% vs +2.12%.
- MSFT +1.34% vs +2.13%.
- NVDA +2.99% vs +4.82%.
- AMD +9.29% vs +4.34%.
- AVGO +3.91% vs +2.91%.
- META +3.75% vs +4.24%.

Conclusion: near_20d_high should remain a soft price-location feature, not a hard block.

### 5.4 More than 10% above 50DMA

Strongly heterogeneous:
- AAPL -0.21%.
- MSFT +3.84%.
- NVDA +3.99%.
- AMD +6.44%.
- AVGO -3.11%.
- META +7.66%.

Conclusion: MA extension is useful for describing position, but not justified as a universal no-buy threshold from this evidence.

### 5.5 Cross-asset composite sanity check

For NVDA/AMD/AVGO/MSFT, a simple drawdown sample was conditioned on:
- QQQ 5D stabilization;
- SOXX relative strength vs QQQ;
- no top-quartile oil shock / bottom-quartile TLT shock / top-quartile UUP shock / bottom-quartile HYG shock.

This composite did not improve forward 20D returns consistently in the preliminary sample. Therefore the macro/leadership variables should not be combined into a hard positive gate by intuition.

The correct next step is independent cluster ablation with fixed definitions and episode clustering.

## 6. Revised architecture

The Entry Gate should be refactored into four independent evidence layers:

### A. Price Location
- drawdown_20/60/120;
- distance_MA20/50/200;
- 3D/5D/20D return;
- pullback depth/duration;
- gap;
- rebound/breakout state.

### B. Extension / Chase Risk
- 5D return percentile;
- consecutive up sessions;
- distance from MA20/50;
- distance to recent high;
- abnormal gap;
- volume anomaly.

This layer produces CHASE_RISK, but does not automatically claim negative expected return.

### C. Market Permission
- benchmark trend;
- true breadth;
- leadership relative strength;
- volatility regime;
- signed rates shock;
- signed FX shock;
- signed oil shock;
- credit stress;
- cross-asset transmission.

### D. Attribution / Evidence
- company event;
- sector/thematic;
- macro/cross-asset;
- technical/flow;
- unresolved;
- source IDs;
- observed/available timestamps;
- confidence;
- catalyst age;
- observed persistence.

The downstream action should consume:

Opportunity = Price + Fundamentals + Leadership
Permission = Market + Macro + Risk
Evidence = Attribution + DataQuality

No single soft variable should silently become a veto.

## 7. Required next empirical experiment

Do not tune a final threshold yet.

Run an episode-clustered ablation matrix:

- P0: price-only;
- P1: P0 + price location;
- P2: P1 + extension/chase;
- P3: P2 + market breadth/leadership;
- P4: P3 + rates/oil/FX/credit;
- P5: P4 + attribution evidence;
- P6: full model including fundamentals.

For every version report:
- N independent episodes;
- 5D / 20D / 60D forward return;
- positive-return rate;
- median return;
- worst return;
- max adverse excursion;
- drawdown after entry;
- false-positive rate;
- miss rate;
- trigger frequency;
- time-to-rebound;
- incremental lift vs prior layer.

Split requirements:
- time-ordered development / validation / OOS;
- walk-forward;
- 2000 / 2008 / 2020 / 2022 stress anchors where coverage exists;
- no repeated counting of the same drawdown episode.

Promotion rule:
RESEARCH → VALIDATED → SHADOW → OPERATIONAL

No threshold or weight should be promoted from the preliminary sanity check.

## 8. Immediate coding priority

1. Expand the observation schema before adding more indicators.
2. Replace absolute macro status with signed shock variables.
3. Persist per-series freshness rather than global newest timestamp.
4. Implement sector/market relative strength.
5. Replace watchlist breadth with a documented breadth source or keep the proxy explicitly isolated.
6. Build attribution records with UNKNOWN as a first-class state.
7. Add episode IDs / cooldown / re-arm rules.
8. Only then run the ablation matrix.

## 9. Lesson learned

The current risk is not too few indicators.

The larger risk is too many plausible variables without a consistent PIT observation model and independent episode definition.

The new rule should therefore optimize for:
- reproducibility;
- causal-evidence discipline;
- directionally correct shock encoding;
- incremental OOS contribution;
- capital-survival impact.

Intuitive variables stay in the research pool until they earn their place through ablation.

## 10. Git decision

This audit is material and reproducible, so it is recorded separately from the frozen v1.0 research rule.

Do not rewrite the frozen Entry Gate v1.0 from this preliminary result.
