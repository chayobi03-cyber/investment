# Entry Gate & Price-Move Attribution v1.0

Date: 2026-09-22
Status: RESEARCH RULE — NOT YET PROMOTED TO LIVE TRADING

## 1. Purpose

A stock candidate must be evaluated on both:

1. **Price location / entry timing**
2. **Why the price moved**

A strong company or strong sector trend is not sufficient for entry.

## 2. Required observation fields

For every liquid stock in the frozen universe, record at each observation date:

- latest price and previous close
- 1d / 3d / 5d / 20d return
- consecutive up/down sessions
- distance to 20d / 60d / 120d / 52w high
- distance to 20d / 50d / 200d moving averages
- weekly trend state
- recent pullback magnitude and duration
- rebound / breakout state
- volume or turnover change when reliable
- sector relative strength
- market relative strength
- current market-regime state
- current macro/cross-asset state
- **move-attribution category**
- **attribution evidence**
- **attribution confidence**
- **expected persistence**
- event/catalyst date and age

## 3. Price-move attribution taxonomy

Classify the latest material move into one primary category and optional secondary categories:

### A. Company-specific
Examples:
- earnings / guidance
- estimate revision
- product / contract / backlog
- M&A / financing
- regulatory / legal event
- management announcement

### B. Sector / thematic
Examples:
- semiconductor cycle
- AI capex / infrastructure
- financial-sector move
- commodity-specific sector repricing

### C. Macro / cross-asset
Examples:
- Treasury yield move
- oil shock / reversal
- FX move
- geopolitical de-escalation / escalation
- broad risk-on / risk-off

### D. Technical / flow
Examples:
- breakout / short covering
- index rebalance
- ETF flow
- positioning squeeze

### E. Unresolved
Use when evidence is insufficient. Do not manufacture a causal explanation.

## 4. Attribution confidence

- **Verified**: primary/company/exchange/regulatory source directly supports the event.
- **Corroborated**: multiple high-quality independent sources support the same mechanism.
- **Inferred**: timing and cross-asset/sector behavior are consistent, but no direct catalyst evidence.
- **Unknown**: evidence insufficient.

Do not treat inferred or unknown attribution as equivalent to verified attribution.

## 5. Catalyst persistence state

The reason for a price move must be separated from whether it is likely to persist:

- **Structural**: likely multi-quarter / multi-year
- **Fundamental cyclical**: potentially multi-week / multi-quarter
- **Event-driven**: date-bounded
- **Macro regime**: persists while macro condition remains
- **Technical/flow**: potentially short-lived
- **Unknown**

Persistence is a state to monitor, not a forecast of future price.

## 6. Entry Gate

A stock can be a research candidate even when the entry gate is closed.

### Entry candidate requires:

- weekly trend is intact or credible reversal is confirmed;
- stock is not in an explicitly defined chase state;
- recent move has either a credible catalyst or a technically confirmed recovery;
- sector and market conditions do not contradict the thesis;
- price location provides a defined add/re-entry path;
- attribution confidence is not Unknown for a material abnormal move.

### Chase filter

Flag `CHASE_RISK` when several of the following coexist:

- multiple consecutive positive sessions;
- unusually strong 3d/5d return;
- close near recent/52w high;
- large distance above short/intermediate moving averages;
- gap or one-day event spike without consolidation.

A `CHASE_RISK` flag blocks the default new-scout action unless an explicitly validated breakout rule later overrides it.

## 7. Required output for each screened stock

The scanner should produce:

`Price → Delta → Weekly Position → Short-Term Extension → Market/Sector Context → Move Reason → Evidence Confidence → Persistence → Entry State`

Example:

`MSFT | 501.64 | +1.7% 1d | high-zone | moderate extension | tech risk-on | catalyst: AI/cloud + market move | inferred/verified | structural+macro | ENTRY-WATCH`

The final state is not a recommendation. It is an entry-timing state for downstream decision logic.

## 8. Validation requirements

Before operational use, test whether price-move attribution improves:

- forward 5d / 20d / 60d returns
- drawdown after entry
- false-positive rate
- chase-entry loss rate
- time-to-rebound
- signal persistence

Compare at minimum:

1. price-only entry gate
2. price + weekly position
3. price + weekly position + short-term extension
4. price + weekly position + attribution
5. full gate including market/sector context

All tests must use point-in-time information and frozen attribution definitions.

## 9. Current lesson incorporated

A prior screen advanced a strong semiconductor candidate despite five consecutive rising sessions. The candidate was subsequently recognized as a chase-risk case.

Therefore:

**Do not send a scout merely because the company, sector, or theme is strong. Check price extension and the causal reason for the latest move first.**

## 10. Governance

This rule is a research amendment to the Investment Market Decision Framework v1.0.

Promotion path:

`RESEARCH → VALIDATED → SHADOW → OPERATIONAL`

No operational promotion without OOS / walk-forward / robustness validation.