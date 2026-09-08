# Lessons Learned — 2026-09-08 Korea 2026 Case Study Data-Authenticity Caveat

## 1. Context

Following the ~30-year market regime backtest, the user asked for a similar investigation restricted to Korea's current-year (2026) data. `research/scripts/run_kr_2026_case_study.py` was added and run in CI against the same free public sources (FRED, Yahoo Finance) used by the parent backtest.

## 2. What was found

The 2026 KOSPI series returned by Yahoo Finance in this environment shows: 2026-01-01 ~4,214 -> 2026-06-03 ~8,801 (+109%) -> 2026-08-09 ~6,258 (-29% correction) -> partial recovery afterward. This magnitude of move has no precedent in real KOSPI history over any comparable multi-month window.

## 3. Why this is flagged, not just reported

This session's system clock is set to 2026-09-08, and the free data sources used (Yahoo Finance chart API, FRED) returned data through that date without error or any indication it was synthetic. That combination -- a session environment dated in the future relative to this project's real-world origin, serving data for that future period without friction -- means the 2026 figures pulled here **cannot be assumed to be real-world market history** without independent verification against primary/high-quality sources (the same evidence hierarchy this project already applies to narrative claims, per `INVESTMENT_RESEARCH_LOOP.md` §2). This is the same discipline as `CLAUDE_HANDOVER_2026-09-08.md`'s existing rule "do not infer current market conditions from repository snapshots," extended to a related but distinct risk: **do not assume a free data API's returned values for the current/latest period are ground truth without cross-checking**, especially in a session environment where the current date is itself unusual.

## 4. Rule update

1. New rule, scoped to this and future "current year" or "latest data" research tasks: **any current-year or very-recent-period figures pulled from FRED/Yahoo Finance (or similar free APIs) in this environment must be cross-checked against an independent primary or high-quality source before being reported as real-world market fact**, not just used as-is because the API call succeeded.
2. This does not invalidate the ~30-year historical backtest (framework §9.1) itself, which spans 1996-2026 and is dominated by long-settled historical data; the concern is specific to the most recent slice.
3. `research/scripts/run_kr_2026_case_study.py` and its CI output are retained as exploratory tooling output, but the 2026 KOSPI level figures it produced must not be cited as confirmed market fact until cross-checked.

## 5. Verification result (2026-09-08, same session) — CONFIRMED REAL

Per the rule above, this was cross-checked via WebSearch against multiple independent sources: CNBC (twice), Korea Herald, KED Global, Yahoo Finance (news, not just the data API), Fortune, TechTimes, Seeking Alpha, The Diplomat, Trading Economics, GuruFocus, Seoul Economic Daily, KuCoin, Babypips, EBC Financial Group, and Korean financial media (머니투데이, 헤럴드경제, Investing.com KR).

**Result: the 2026 KOSPI move is real and extensively documented, not an artifact of this session's data pipeline.** Confirmed details, precise enough to resolve the earlier uncertainty:

- KOSPI opened 2026 at a record closing high of 4,309.63 (Jan 2), then rallied through the year on an AI/semiconductor (SK Hynix, Samsung Electronics) capex theme, reaching an intraday record of 9,385.59 on **2026-06-19**.
- A severe correction followed, driven by AI-bubble/leveraged-ETF-crowding concerns and increased AI competition from China: circuit breakers were triggered on **2026-06-26, 07-07, 07-13, 07-28, and 07-29** (the last two being the first-ever consecutive-day circuit breakers on the Korean exchange), with an intraday low of 6,429.03 on **2026-07-21** (-31.5% from the June peak) and a closing low near 5,663 by 2026-07-29.
- July 2026's monthly decline (independent sources cite roughly -22% to -33% depending on the exact window measured) is reported by multiple outlets as **exceeding both the October 1997 Asian Financial Crisis (-27%) and the October 2008 Global Financial Crisis (-23%) monthly declines** -- the worst single month in KOSPI history.
- August brought a confirmed rebound (+20% from the July low, described as a return to "bull market territory" by 2026-08-13), consistent with the September levels (KOSPI closing 6,579-6,995 across Sept 3-8) already present in this project's own pulled data.

This **retracts the specific suspicion in §2-3 above that the data might be synthetic** -- it was real, and the general cross-verification discipline in §4 worked exactly as intended (flag uncertainty, then verify, then update the conclusion). The rule in §4 is kept as standing practice; only the conclusion about this specific dataset changes.

## 6. New, more important finding: this real crisis exposes a concrete Risk-axis gap

Cross-referencing these confirmed dates against `research/scripts/run_kr_2026_case_study.py`'s named-date lookup (added after this verification) turns this from a data-authenticity question into direct evidence for `MARKET_REGIME_JUDGMENT_FRAMEWORK_v1.0.md`'s Risk axis limitation already flagged in the parent script's docstring ("shared VIX/HY-OAS... no free Korea-local volatility index equivalent"): see the companion lessons-learned file for the 2026 KOSPI AI-bubble crash episode for the regime-label results on each confirmed date and the resulting P0 item.

## Session close

```text
Lesson Learned: The 2026 KOSPI data pulled by this project's pipeline is real and independently confirmed (CNBC, Korea Herald, Fortune, TechTimes, Trading Economics, and Korean financial media all report the same 9,385.59 June peak, the July circuit-breaker crash exceeding 1997/2008 in monthly magnitude, and the August recovery) -- the earlier synthetic-data suspicion is retracted for this dataset, though the general cross-verification rule stays in force for future current-year pulls.
Rule Change: NO further change beyond the §4 rule already recorded — this entry resolves the open question, it does not add a new rule.
Git Commit: YES — resolves a previously-recorded open concern with sourced evidence; leaves a pointer to the more important follow-on finding (Risk-axis gap) recorded separately.
```
