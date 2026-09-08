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

## Session close

```text
Lesson Learned: This environment's free-data APIs (FRED, Yahoo Finance) returned 2026 KOSPI figures showing a historically unprecedented +109% then -29% swing within a session whose system clock is itself set to 2026-09-08 -- a combination that means "the API call succeeded" is not sufficient evidence the returned current-year data is real-world market history. Cross-verification against a primary source is now required before treating recent-period figures from these sources as fact.
Rule Change: YES — new cross-verification requirement for current-year/latest-period data pulled from these APIs in this environment.
Git Commit: YES — new governance rule, material to how this project should trust its own data pipeline going forward.
```
