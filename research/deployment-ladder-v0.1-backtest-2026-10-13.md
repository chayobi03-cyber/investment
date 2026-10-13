# Dry Powder Deployment Ladder v0.1 — Backtest (2026-10-13)

- **Status:** RESEARCH EVIDENCE — supports [Deployment Trigger Table v0.1](../docs/portfolio/DEPLOYMENT_TRIGGER_TABLE_v0.1.md) (PROPOSAL)
- **Script:** `research/scripts/deployment_ladder_backtest.py` (tests: `tests/test_deployment_ladder_backtest.py`)
- **Data:** `research/deployment-ladder/data/sp500_shiller_monthly_to_2026-09.csv` — Shiller monthly S&P 500 via `github.com/datasets/s-and-p-500`, fetched 2026-10-13, sha256 `3a45dffa…ecac6`
- **Results:** `research/deployment-ladder/results/summary.json`

## 1. Question

[Allocation Rule v0.1 §7](../docs/governance/PORTFOLIO_ALLOCATION_RULE_v0.1.md) stages the move from Dry Powder into equities, but the stages have no triggers. Dry Powder rose from 52% to 60% between 2026-09-07 and 2026-10-13 ([portfolio review](../docs/portfolio/2026-10-13_portfolio_review.md), F1). The question is which deployment policy should move a cash tranche into broad US equity, judged by:

- terminal wealth versus investing everything at once;
- the path drawdown of the tranche (cash + equity);
- how much cash is still uninvested at the end.

## 2. Design

- One tranche, 100% cash at start month `t0`, evaluated after **36 months**.
- Start months 1900-01 … 2023-09 (1,485 overlapping starts). Overlapping starts are **not independent**, so the counts describe coverage, not statistical significance.
- Signal at month `t` uses data up to `t`; a buy decided at `t` executes at month `t+1`'s price (no look-ahead).
- Drawdown = monthly price ÷ trailing 12-month high − 1.
- Equity return includes dividends. Dividends are missing after 2023-06, so the last observed yield is carried forward.
- Two cash assumptions bracket the result: **0%** (penalizes waiting) and **10Y yield** (generous to waiting, since T-bills usually yield less).

| Policy | Rule |
|---|---|
| LUMP | 100% at `t0` |
| DCA6 / DCA12 | equal monthly buys over 6 / 12 months |
| LADDER | §7 ladder on drawdown only: 20% at `t0`, then cumulative 40/60/80/100% when drawdown touches −10/−15/−20/−30% (§7's 20/20/25/25/30 adds up to 120%, so it is normalized to five equal stages) |
| LADDER_STAB | LADDER, but a touched stage fires only in a month that closes up |
| HYBRIDn | each month, deploy up to max(time floor `(k+1)/n`, LADDER level) |
| HYBRIDn_STAB | the same, with the stabilized ladder |
| `@0.75` / `@1.25` | every ladder level × 0.75 / × 1.25 (sensitivity) |

## 3. Results (36 months; cash at 0% / cash at 10Y yield)

### All starts (n = 1,485)

| Policy | Median vs LUMP | P5 vs LUMP | Median tranche MDD | P5 tranche MDD | Mean still uninvested | Starts with >50% still uninvested |
|---|---:|---:|---:|---:|---:|---:|
| LUMP | 0 | 0 | −14.5% | −44.7% | 0% | 0% |
| DCA6 | −2.5% / −1.6% | −9.3% / −8.3% | −13.8% | −42.0% | 0% | 0% |
| DCA12 | −4.8% / −2.9% | −15.9% / −14.5% | −12.8% | −41.6% | 0% | 0% |
| **LADDER (current §7)** | **−10.4% / −4.3%** | **−38.4% / −32.3%** | −6.6% | −37.0% | **38%** | **36%** |
| LADDER_STAB | −10.3% / −4.1% | −38.4% / −32.3% | −6.0% | −26.7% | 39% | 38% |
| **HYBRID6_STAB** | **−2.0% / −1.2%** | **−8.4% / −7.6%** | −13.9% | −42.4% | 0% | 0% |
| HYBRID12 | −4.0% / −2.2% | −13.8% / −12.6% | −13.3% | −41.6% | 0% | 0% |
| HYBRID12_STAB | −4.1% / −2.2% | −13.8% / −12.6% | −13.1% | −41.6% | 0% | 0% |
| HYBRID24 | −7.0% / −3.5% | −21.1% / −19.0% | −11.1% | −40.4% | 0% | 0% |

### Starting near a high (drawdown > −5%, n = 930) — today's S&P 500 position

| Policy | Median vs LUMP | P5 vs LUMP | Mean still uninvested |
|---|---:|---:|---:|
| DCA6 | −2.6% / −1.8% | −8.6% / −7.9% | 0% |
| LADDER | −13.8% / −5.8% | −40.1% / −34.4% | **43%** |
| HYBRID6_STAB | −2.6% / −1.7% | −8.5% / −7.8% | 0% |
| HYBRID12_STAB | −5.0% / −3.1% | −13.9% / −12.8% | 0% |

### Starting inside a correction (drawdown ≤ −10%, n = 359) — today's KOSPI position

| Policy | Median vs LUMP | P5 vs LUMP | Mean still uninvested |
|---|---:|---:|---:|
| DCA6 | −1.1% / −0.4% | −11.4% / −10.5% | 0% |
| DCA12 | −3.9% / −2.3% | −18.3% / −17.1% | 0% |
| LADDER | −4.7% / −2.1% | −25.7% / −20.7% | 22% |
| HYBRID6_STAB | −0.1% / 0.0% | −7.3% / −6.6% | 0% |
| HYBRID12_STAB | −0.5% / −0.2% | −12.0% / −10.9% | 0% |

### 2000–2023 starts (n = 285)

The ordering is the same: LADDER −14.0% median vs LUMP with 43% still uninvested on average; HYBRID6_STAB −2.0%; HYBRID12_STAB −3.6%.

## 4. Findings

1. **A drawdown-only ladder does not deploy.** Under the current §7 design, after three years 38% of the tranche is still cash on average. In 36% of starts more than half is still cash, and in 45% of starts that began near a high. The low drawdown it shows comes from staying in cash, not from better entries. This is the failure seen in the 2026-10-13 review.
2. **A time floor fixes the failure. Its length is the main cost lever.** The median cost against LUMP is about 0.3 pp per extra month of floor (6 → 12 → 24 months: −2.0% → −4.1% → −7.0% with cash at 0%).
3. **Staging barely protects the tail.** Over 36 months the P5 tranche drawdown is −42% for HYBRID6 and −42% for HYBRID12, against −45% for LUMP. What actually limits the loss is the **tranche size**, not the schedule.
4. **Drawdown accelerators help when the start is already in a correction.** HYBRID6_STAB beats DCA6 there (median −0.1% vs −1.1%, P5 −7.3% vs −11.4%). Near a high they almost never fire within six months, so HYBRID6 ≈ DCA6.
5. **The stabilization filter is inert once a time floor exists.** HYBRID12 and HYBRID12_STAB differ by ≤ 0.1 pp everywhere. It only improves the tail of the ladder-only policy. Ablation rule (BUY_TRIGGER_ENGINE_V0.1 §14): it does not earn a place in the live rule.
6. **The ladder levels are not fragile.** Scaling every level by 0.75× or 1.25× moves medians by ≤ 1.1 pp. The P5 tail in correction starts moves more (−8.3% at 0.75× vs −12.0% at 1.0×, 0% cash), so earlier levels are slightly better, not worse.

## 5. Limitations

- Monthly **average** prices understate intra-month drawdowns. Live daily closes will hit each level earlier and more often, so live deployment will be somewhat faster than tested.
- US equity in USD only. The live instruments are KRW-listed, unhedged S&P 500 ETFs: **USD/KRW risk was not tested**.
- Overlapping starts, one market, a three-year horizon. This is descriptive evidence, not a validated predictive model. No OOS/walk-forward split, because no parameter was fitted.
- Taxes, fees and ETF tracking error are not modelled.
