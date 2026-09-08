# Per-Asset Buy Intensity / Risk Score Framework v0.1

- Date: 2026-09-08
- Status: WORKING BASELINE
- Scope: fills the "ticker selection comes after this sequence" step at the
  end of `docs/governance/PORTFOLIO_ALLOCATION_RULE_v0.1.md` section 8's
  decision hierarchy, and sits downstream of the **Target Bucket** output
  of `docs/governance/PORTFOLIO_DEPLOYMENT_ENGINE_v0.1.md`'s five-stage
  pipeline.
- Origin: session correction (2026-09-08) of an earlier error — a prior
  answer blended a single market-wide "매수강도" (buy intensity) number
  into a per-ticker table. That conflation is rejected going forward.

## 1. The core correction

**Market regime and individual-asset decisions must be kept separate.**

A single aggregate "오늘 매수강도 65" (today's market buy intensity is 65)
describes the *macro backdrop* (rates, oil, FX flows, growth/semiconductor
relative strength — see `LESSONS_LEARNED_2026-09-08_MARKET_SESSION.md`
section 4). It is **reference context only**. It must never be written
directly into a per-ticker decision table as if it were that ticker's own
score. Every asset gets its own two independent numbers.

## 2. The two independent scores

For every candidate asset:

- **Buy Intensity (0–100):** how attractive is *adding to this position at
  the current price*, right now. Higher = more attractive entry.
- **Risk Score (0–100):** how much loss/variance/event risk exists *at the
  current price*, right now. **Higher = riskier** (this polarity is fixed
  going forward — do not flip it in later documents).

**These two numbers are never combined into one score.** A high-quality
asset can have low Buy Intensity (great company, bad entry price, e.g. at
a local high) and a mediocre-trend asset can have high Buy Intensity if the
price is unusually favorable relative to its own history and the portfolio's
target weight.

### Supporting sub-scores that feed the two headline numbers

- 추세점수 (trend score)
- 수급점수 (flow/positioning score)
- 밸류에이션 (valuation)
- 포트폴리오 목표비중 갭 (target-weight gap from the relevant bucket's
  Portfolio Gap, per Portfolio Allocation Rule v0.1 / Deployment Engine
  Stage ⑤)

These sub-scores are inputs; Buy Intensity and Risk Score are the two
outputs a decision is actually made from.

## 3. Decision order

```text
종목(Ticker)
  → 현재가격 (current price, refreshed from a primary/high-quality source)
  → 매수강도 (Buy Intensity)
  → 리스크 점수 (Risk Score)
  → 적정 행동 (BUY / HOLD / WATCH / REDUCE)
  → 투입비율 (tranche size, bounded by the Deployment Engine's
     Deployable % for that asset's Target Bucket)
```

This is the ticker-selection layer that
`PORTFOLIO_ALLOCATION_RULE_v0.1.md` section 8 already reserved
("Ticker selection comes after this sequence") but never specified in
detail. It does not replace the Deployment Engine's bucket-level Deployable
% — it allocates *within* whatever amount the Deployment Engine assigns to
a bucket, among that bucket's candidate tickers.

### Reading combinations (examples, not a lookup table to memorize)

- High Buy Intensity + Low Risk → strong candidate for a larger tranche.
- High Buy Intensity + High Risk → candidate for a smaller, staged tranche,
  not a full-size one.
- Low Buy Intensity + Low Risk → fine to hold, not a reason to add now.
- Low Buy Intensity + High Risk → lowest priority regardless of how good
  the underlying asset is otherwise considered.

"좋은 종목인가?" (is this a good asset?) and "지금 사기 좋은가?" (is now a
good time to buy it?) are different questions and must be answered
separately.

## 4. Provenance caveat on today's example table — READ BEFORE USING

The following table was supplied by the user in this session as an example
of the intended format, covering Samsung Electronics, SK Hynix, semiconductor
equipment/materials names, gold, silver, JPY, BTC, ETH, and a CD-rate ETF:

| Asset | Buy Intensity | Risk Score | Note (as supplied) |
|---|---:|---:|---|
| Samsung Electronics | 50/100 | 45/100 | Strong trend but near highs — do not chase |
| SK Hynix | 55/100 | 60/100 | Very strong momentum but volatility/high-level concern |
| Semiconductor equipment/materials | 60/100 | 65/100 | Possible sector rotation, but wide dispersion by name |
| Gold | 65/100 | 35/100 | Defensive + favorable trend |
| Silver | 70/100 | 60/100 | Strong momentum but high volatility |
| JPY | 65/100 | 40/100 | Currency diversification; caution chasing after a sharp rebound |
| BTC | 50/100 | 70/100 | Recovering, needs confirmation above $80k |
| ETH | 45/100 | 75/100 | Weaker relative strength than BTC |
| KODEX CD-rate active (ETF) | HOLD | 10/100 | Dry powder / defensive anchor |

**This table is an unverified, user-supplied illustrative example, not a
research-loop output from this repository.** Per this project's own
evidence discipline (`docs/governance/INVESTMENT_RESEARCH_LOOP.md` and
`docs/research/NARRATIVE_VALIDATION_WORKFLOW_v0.1.md`):

- No source, timestamp, or calculation method was provided for these
  specific numbers.
- This session did not independently verify current prices, trend state, or
  volatility for any of these tickers before this table was supplied.
- **These scores must not be used to make or justify an actual buy/hold/
  reduce decision until they are re-derived from current primary/
  high-quality market data in a live session**, following the decision
  order in section 3.

The table is retained here **only as a format example** for how Buy
Intensity and Risk Score should be tabulated per asset going forward — not
as today's confirmed market read.

## 5. What changes in existing documents

- `docs/governance/LESSONS_LEARNED_2026-09-08_MARKET_SESSION.md` section 4
  ("매수강도") describes the **market-level** composite; add a
  cross-reference there that ticker-level decisions must use this
  document's two-score framework instead of the market composite directly.
- `docs/governance/PORTFOLIO_DEPLOYMENT_ENGINE_v0.1.md` Stage ⑤ selects a
  **Target Bucket**; this document is the next step down, selecting
  **which ticker(s) within that bucket** and at what tranche size, bounded
  by the bucket-level Deployable %.

## 6. Session close

```text
Lesson Learned: A market-wide buy-intensity composite was being blended
into per-ticker decision tables. Corrected: Buy Intensity and Risk Score
are now two independent, asset-level numbers, never merged into one,
and market regime is explicit reference context only.

Rule Change: YES - new governance document defining the per-asset
scoring framework and decision order; the example score table is
explicitly flagged as unverified and non-actionable until re-derived
from current data.

Git Commit: YES - governance/methodology change affecting future
per-asset decisions.
```
