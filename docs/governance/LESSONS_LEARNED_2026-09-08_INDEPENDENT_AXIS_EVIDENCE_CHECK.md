# Lessons Learned — 2026-09-08 Independent Axis Evidence Check

## 1. Context

Following the DSR/PBO source review (`LESSONS_LEARNED_2026-09-08_DSR_PBO_SOURCE_REVIEW.md`), this session ran this project's own independent searches for primary/institutional evidence behind each of the five Market Regime axes in `MARKET_REGIME_JUDGMENT_FRAMEWORK_v1.0.md`, rather than continuing to review externally-supplied memos. Recorded in the framework as new §1.2.

## 2. What was checked

Independent WebSearch queries (not sourced from any pasted memo) for:

- Time-series momentum evidence (Trend axis)
- Market breadth / advance-decline predictive research (Breadth axis)
- VIX-credit spread combined regime research (Volatility/Risk axis)
- Yield curve recession models and Chicago Fed NFCI methodology (Rates/Liquidity/Credit axis)

Direct PDF fetch was attempted and blocked again (same network policy as the prior review), so findings rest on search-result summaries, not verbatim primary-text reads.

## 3. Key findings

1. **Axis A (Trend)** has a solid, specific academic anchor: Moskowitz, Ooi & Pedersen, "Time Series Momentum," *Journal of Financial Economics* (2012) — 58 futures/forwards, 25+ years, 1-12 month persistence with longer-horizon reversal. Note: their sample is futures/forwards on indices/FX/commodities/bonds, not a composite equity-market score, so applying the pattern to this framework's Trend axis is still an assumption pending this project's own test (§9), not an inherited result.
2. **Axis B (Breadth)** has a strong anchor: Zaremba, Szyszka, Karathanasopoulos & Mikutowski, "Herding for Profits: Market Breadth and the Cross-Section of Global Equity Returns," *Economic Modelling* (2019/2020) — breadth found predictive across 64 countries, 1973-2018, robust to standard controls.
3. **Axis C (Volatility/Risk)** has partial support: VIX and credit spreads are meaningfully but not perfectly correlated (independent, complementary information), and stress-regime cut points exist in the literature/practice (e.g., ~90th percentile volatility, credit Z-score > 2.0) — but these are recorded as candidates to recalibrate on this project's own data, not values to import directly, matching the discipline already applied to DSR/PBO thresholds.
4. **Axis D (Rates/Liquidity/Credit)** produced one concrete correction: the New York Fed's own official recession-probability model (Estrella & Mishkin, 1996) uses the **10-year minus 3-month** Treasury spread, not 10Y-2Y, and 10Y-3M reportedly outperforms 10Y-2Y post-1980. The framework's axis table is corrected to include both, not 10Y-2Y alone. Separately, the Chicago Fed's National Financial Conditions Index (105 series, Dynamic Factor Model, mean-0/SD-1 normalization since 1971; Brave & Butters 2010/2014) is a directly reusable methodological template for this axis's scoring transform.
5. **Axis E (Cross-asset flow)** is the weakest externally-anchored axis: no canonical academic/institutional composite was found analogous to NFCI or the breadth literature. This is now flagged as a new P0 item — this axis needs the project's own justified design rather than an assumed external template.

## 4. Rule update

1. No existing hard rule changed.
2. `MARKET_REGIME_JUDGMENT_FRAMEWORK_v1.0.md`: §1 Rates/Liquidity/Credit row corrected (10Y-3M added alongside 10Y-2Y); new §1.2 added documenting per-axis evidence status; new P0 item added for Axis E.
3. Framework validation status unchanged: still WORKING HYPOTHESIS, not validated on this project's own data. External evidence supports the axis choices' plausibility (Level 1, economic logic) but does not substitute for this project's own Level 2-10 testing.

## Session close

```text
Lesson Learned: Independent search (not the two prior externally-supplied memos) found credible primary/institutional anchors for the Trend, Breadth, and Rates/Liquidity/Credit axes, one concrete factual correction (NY Fed uses 10Y-3M, not 10Y-2Y, as its official spread), and confirmed the Cross-Asset axis is comparatively unanchored and needs this project's own design work before it can be treated as equally evidenced as the other four axes.
Rule Change: NO — no existing hard rule modified; framework document corrected and extended with sourcing.
Git Commit: YES — governance/evidence-discipline record and framework amendment.
```
