# Lessons Learned — 2026-09-08 KOSPI 2026 AI-Bubble Crash: R5/R6 Regime Miss

## 1. Context

Following confirmation that the 2026 KOSPI move is real (see `LESSONS_LEARNED_2026-09-08_KR_2026_DATA_AUTHENTICITY_CAVEAT.md` §5), `research/scripts/run_kr_2026_case_study.py` was extended with a named-date lookup: what `KR_Regime` label did the candidate Market Regime v0.1 system (`MARKET_REGIME_JUDGMENT_FRAMEWORK_v1.0.md` §4.1/§6.2) assign on the specific, independently-confirmed dates of the 2026 KOSPI AI-bubble crash? Run in CI (`34228475554`).

## 2. The confirmed real-world event

Cross-checked via WebSearch against CNBC, Korea Herald, Yahoo Finance, Fortune, TechTimes, Trading Economics, and Korean financial media: KOSPI hit an intraday record of 9,385.59 on 2026-06-19, then crashed on AI-bubble/leveraged-ETF-deleveraging concerns (aggravated by intensifying AI competition from China pressuring Korean chip names), triggering circuit breakers on 06-26, 07-07, 07-13, 07-28, and 07-29 -- the last two the first-ever consecutive-day circuit breakers on the Korean exchange -- bottoming near 5,663-6,429 in late July (-31.5% to -38% from peak). Multiple independent sources describe July 2026's monthly decline as exceeding both the 1997 Asian Financial Crisis (-27%) and the 2008 Global Financial Crisis (-23%) -- the worst single month in KOSPI history. August brought a confirmed rebound to bull-market territory.

## 3. What the candidate system said

| Date | Event | Drawdown | VIX | Market_Score | KR_Regime |
|---|---|---:|---:|---:|---|
| 06-19 | Record high (peak) | -0.1% | 16.4 | 51.9 | R4 |
| 06-26 | 1st circuit breaker | -7.7% | 18.4 | 41.1 | R4 |
| 07-07 | Circuit breaker | -16.0% | 16.1 | 49.0 | R4 |
| 07-13 | Circuit breaker | -25.3% | 17.2 | 62.5 | **R2 (Normal Risk-On)** |
| 07-21 | Intraday low (-31.5%) | -26.0% | 17.0 | 55.3 | R4 |
| 07-28 | Circuit breaker (1st back-to-back) | -33.9% | 18.2 | 52.1 | R4 |
| 07-29 | Circuit breaker (2nd, historic first) | -37.9% | 20.7 | 48.0 | R4 |
| 08-13 | Confirmed bull-market return | -25.2% | 14.6 | 65.6 | **R2 (Normal Risk-On)** |

Full-year 2026: R5 (Risk-Off) 1.6% of days, **R6 (Panic) 0.0% of days**. On two dates during a still-severe drawdown, the system labeled the market actively "Risk-On," not merely "not panic."

## 4. Root cause (confirmed, not theoretical)

1. **Shared US VIX.** VIX stayed in the 14.6-20.7 range throughout, never approaching R5's `VIX > 25` or R6's `VIX > 35` thresholds, because the crisis was Korea/AI-chip-sector-specific and did not produce a matching US volatility spike. This is exactly the limitation the parent script's docstring already flagged as a simplification ("no free Korea-local volatility index equivalent was available") -- this episode confirms it is not a minor caveat but the primary reason the crisis was missed.
2. **Risk axis's realized-volatility and max-drawdown components are computed on the S&P 500, not KOSPI**, per `build_risk_score`'s call in `load_and_score()` (`build_risk_score(df["VIX"], df["SP500"], df["SP500"], df["HY_OAS"])`, used for both the KR and US regimes) -- so even the "local" pieces of the Risk axis were not actually local to Korea.
3. **A newly identified issue**: the Breadth axis proxy (KOSPI-vs-KOSDAQ relative 20-day return) scored unusually high (98-99.6) on the two dates that crossed into R2, plausibly because the crash was large-cap-led (SK Hynix, Samsung Electronics), so KOSDAQ (small-cap) held up better in relative terms -- a large-cap-led selloff mechanically resembles "broadening participation" under this proxy. This is a distinct failure mode from the already-documented "no true advance/decline data" limitation.

## 5. Why this matters more than the abstract §9.1 finding

§9.1 (the ~30-year score-bucket backtest) showed a statistical, aggregate non-monotonicity that could plausibly be attributed to thin samples or averaging artifacts. This episode removes that ambiguity: a -37.9% drawdown with two historic, consecutive-day circuit breakers is unambiguously a crisis by any reasonable definition, on a single well-documented date, and the system did not classify it as one. This is a concrete, falsifiable, and now falsified claim about the current R5/R6 design, not a pattern requiring further statistical interpretation.

## 6. Rule update

1. No existing hard rule changed -- the candidate framework was never authorized for live decisions (§13 of the framework document), so nothing regresses.
2. `MARKET_REGIME_JUDGMENT_FRAMEWORK_v1.0.md`: new §9.2 records this episode in full; falsification condition §11.2 marked triggered; three P0 items added/strengthened (recalibrate R1/R5/R6 cut points with this evidence, replace the shared-VIX Risk input with a Korea-local stress measure, investigate the Breadth proxy's large-cap-crash failure mode).
3. The Risk Gate mapping in §7 (already unvalidated per §9.1) is further from promotion: it would have told this project's user "Normal Risk-On, deploy capital normally" on 2026-07-13 and 2026-08-13, while KOSPI sat roughly 25% below its June high.

## Session close

```text
Lesson Learned: A real, independently-confirmed, historically severe KOSPI crash (-37.9% drawdown, two historic back-to-back circuit breakers, described by multiple sources as worse than 1997/2008) was classified as R4 (neutral) or even R2 (Normal Risk-On) throughout by the candidate Market Regime system, confirming the shared-US-VIX Risk-axis simplification is a real, not theoretical, detection gap, and surfacing a second candidate issue in the Breadth proxy's behavior during large-cap-led selloffs.
Rule Change: NO — no existing hard rule modified; the unvalidated candidate framework gained concrete falsifying evidence and three new P0 diagnostic/design items.
Git Commit: YES — the strongest single piece of evidence this framework has produced so far; material to its future design.
```
