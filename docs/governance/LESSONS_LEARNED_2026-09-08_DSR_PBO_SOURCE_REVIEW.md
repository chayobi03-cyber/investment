# Lessons Learned — 2026-09-08 DSR/PBO Source Review

## 1. Context

A follow-up research memo to `MARKET_REGIME_JUDGMENT_FRAMEWORK_v1.0.md` proposed concrete formulas and numeric acceptance thresholds for the framework's L9 data-snooping step: the Deflated Sharpe Ratio (DSR), Probability of Backtest Overfitting (PBO) via CSCV, and White's Reality Check / Hansen's SPA test, citing roughly 15 web links. Per `INVESTMENT_RESEARCH_LOOP.md`'s evidence discipline, this was checked before being folded into the framework, rather than accepted at face value.

## 2. What was checked

- Searched for the primary academic sources behind each claimed method.
- Attempted to fetch the primary PDFs directly (davidhbailey.com, wikipedia.org, sdm.lbl.gov, arxiv.org) to verify formula text and any stated thresholds.

## 3. Findings

1. **The underlying methods are real, correctly-attributed academic work**, not fabricated: Bailey & López de Prado (2014, DSR, JPM 40(5)), Bailey/Borwein/López de Prado/Zhu (2017, PBO/CSCV, J. Computational Finance 20(4)), White (2000, Reality Check, Econometrica), Hansen (2005, SPA test, J. Business & Economic Statistics).
2. **Most of the memo's ~15 numbered citations are low-tier secondary sources** (SEO/blog restatements: saral.money, usekeel.io, surmount.ai, aifinhub.io, globalmarketstructure.com, etc.) that repeat the same primary papers. Per this project's rule against counting re-publications of one original as independent evidence, these are not adopted as citations; the four primary papers above are used instead.
3. **Direct PDF verification failed**: this session's network egress policy blocked WebFetch to all domains attempted (davidhbailey.com, en.wikipedia.org, sdm.lbl.gov, arxiv.org). The DSR formula and CSCV/PBO procedure recorded in the framework (§10.2) are therefore stated from established prior knowledge of these papers, not a fresh read in this session, and are flagged for re-verification when fetch access is available (P3 item).
4. **The specific numeric thresholds "DSR >= 0.95" and "PBO <= 0.10" from the memo are not being adopted as project pass/fail lines.** DSR is a probability-style statistic where 0.95 is a conventional significance-level choice, not a value mandated by the paper. The PBO paper presents PBO as a diagnostic (its own empirical examples include PBO near 0.5) without prescribing a universal cutoff. Importing an externally-asserted threshold as a hard rule without this project's own calibration would violate the existing "no threshold import without independent testing" discipline.

## 4. Rule update

1. No existing hard rule changed.
2. `MARKET_REGIME_JUDGMENT_FRAMEWORK_v1.0.md` §10.2 added: DSR formula, CSCV/PBO procedure, primary-source citation list, and an explicit rejection of the imported 0.95/0.10 thresholds as project rules.
3. New falsification condition added to the framework (§11.7): using a secondary-sourced DSR/PBO threshold to justify promoting a rule is itself a falsification trigger.
4. New P3 open-work item added: re-verify the DSR/PBO papers directly once fetch access allows.

## Session close

```text
Lesson Learned: The DSR/PBO/Reality-Check/SPA methods proposed are real and correctly attributed, but most supporting links were low-tier secondary sources, and the proposed numeric thresholds (DSR>=0.95, PBO<=0.10) are practitioner conventions, not paper-mandated values — they must not be imported as this project's hard acceptance rule without independent calibration on this project's own backtests.
Rule Change: NO — no existing hard rule modified; framework document amended with a sourcing caveat and a new falsification condition.
Git Commit: YES — governance/evidence-discipline record and framework amendment.
```
