# JPY Stress / Confirmation Framework — 2026-09-03

## Purpose

Treat JPY/KRW as a **secondary confirmation indicator** for the Stress Convergence system, not as a standalone crisis or buy signal.

The immediate objective is to test whether yen strengthening adds incremental information after the primary stress indicators are considered.

## Research contract

### Fixed observation levels

The following 100 JPY/KRW levels are frozen for observation:

- 850 KRW
- 875 KRW
- 900 KRW
- 925 KRW
- 950 KRW

These are **observation thresholds**, not trade triggers.

### Fixed temporal horizons

Use the same temporal horizons already frozen in the Stress Convergence temporal attribution work:

- 1 day: ultra-short-term
- 7 days: short-term
- 30 days: medium-term
- 90 days: primary operating horizon
- 365 days: long-term context

The temporal horizons describe persistence / attribution windows. They do not permit retrospective relabeling.

### Attribution principle

A JPY move is not classified as a crisis confirmation merely because it is large or occurs before a crisis. It becomes useful evidence only when the predeclared threshold and temporal conditions are satisfied and it agrees with independent stress dimensions.

The existing SC-FIX-0002 rule remains authoritative: a crisis confirmation is attributable to an early warning only when it occurs after the warning and within the declared time window. The currently frozen windows are 1/7/30/90/365 days, with 90 days as the primary operating window.

## Current market snapshot — 2026-09-03

### JPY/KRW

- 100 JPY/KRW: **859.022 KRW** at 2026-09-03 04:38 UTC according to the cited historical FX record.
- 2026-09-02: 855.546 KRW.
- 2026-09-01: 857.975 KRW.

This places JPY/KRW in the **850–875 observation band**, above the 850 line but below the first structural-confirmation candidate at 875.

Source: Myfin daily JPY/KRW record.

### USD/JPY

Reuters reported that the yen strengthened sharply on 2026-09-03, with USD/JPY reaching **156.36**, the strongest level in about a month. The move was attributed primarily to stronger expectations for a BOJ rate hike rather than confirmed intervention. BOJ board member Hajime Takata's hawkish comments were a central catalyst.

Source: Reuters, 2026-09-03.

### Gold

Reuters reported spot gold at approximately **$4,422/oz**, up **0.8%** on 2026-09-03 as the dollar and Treasury yields eased ahead of the U.S. nonfarm payrolls report.

Source: Reuters, 2026-09-03.

### Bitcoin

A contemporaneous market record placed BTC/USD around **$77.7k** on 2026-09-03. Recent daily data showed BTC near $77.3k at the 2026-09-02 close.

Interpretation: BTC is currently **not providing a strong independent stress confirmation** from this snapshot alone.

Sources: StatMuse Money / contemporaneous BTC market record, 2026-09-03.

### Equities

For 2026-09-02 close:

- S&P 500: **+0.46%**
- Nasdaq: **+0.45%**
- Nikkei 225: **-2.85%**
- KOSPI: **-3.99%**

Interpretation: the equity signal is **mixed by region**, not uniformly risk-on or risk-off. The prior statement that Asian stocks and bonds were simultaneously rebounding is therefore not retained as a current-state conclusion.

Source: AP / The Close Report daily market snapshots.

### Volatility

No independently verified VIX observation is frozen in this record yet. Do not infer a volatility state from equity moves alone.

## TIGER 일본엔선물 reference mapping

Latest independently located quoted value: approximately **7,940 KRW** for TIGER 일본엔선물 (292560), 2026-09-03 08:33 KST reference.

For a simple scenario mapping only:

`reference ETF price × target JPY/KRW ÷ current JPY/KRW`

Using 7,940 KRW at 859.022 JPY/KRW:

| 100 JPY/KRW | Simple reference ETF value | Change vs. reference |
|---:|---:|---:|
| 850 | 7,857 | -1.05% |
| 875 | 8,088 | +1.86% |
| 900 | 8,319 | +4.77% |
| 925 | 8,550 | +7.68% |
| 950 | 8,781 | +10.59% |

This is a **scenario conversion only**. It is not a price target. The ETF can diverge because it tracks an exchange-traded futures index and is affected by futures pricing, roll effects, NAV/market-price differences and tracking error.

## Frozen interpretation bands

| Level | Interpretation | Current status |
|---:|---|---|
| < 850 | rebound not established / loss of current strength | Not current |
| 850 | baseline watch line | Current area |
| 875 | early structural-strength candidate | Not reached |
| 900 | primary structural-strength checkpoint | Not reached |
| 925 | strengthening regime candidate | Not reached |
| 950 | strong yen-strength regime candidate | Not reached |

Important: crossing a level does **not** equal crisis confirmation.

## Cross-asset confirmation logic

JPY should become a useful secondary confirmation only when multiple dimensions agree.

### Level 1 — JPY-only observation

JPY/KRW moves above a fixed observation line.

Result: **Watch only**.

### Level 2 — FX confirmation

JPY/KRW strengthens while USD/JPY continues to decline over the same declared observation horizon.

Result: **Early confirmation candidate**.

### Level 3 — Macro confirmation

JPY strength is accompanied by evidence consistent with a broader risk regime, such as sustained increases in gold or other independently defined stress indicators.

Result: **Cross-asset confirmation candidate**.

### Level 4 — System confirmation

JPY + gold + BTC + equities + volatility + credit/liquidity measures satisfy the already-defined Stress Convergence rules within their declared windows.

Result: only here can JPY contribute to a **system-level crisis classification**.

## Current judgment — 2026-09-03

**JPY: WATCH → EARLY-CONFIRMATION CANDIDATE**

Rationale:

1. JPY/KRW is above 850 but below 875.
2. USD/JPY has moved materially lower, providing an independent FX confirmation dimension.
3. The current yen move is plausibly linked to BOJ policy repricing, so it cannot yet be interpreted as a generic global-flight-to-safety signal.
4. Gold is firm, but equity behavior is regionally divergent and BTC is not showing a strong stress signature in the same snapshot.
5. Therefore the evidence supports **monitoring and structured replay**, not an action signal.

## Required backtest / replay

For the next research run, record at each JPY threshold:

1. JPY/KRW level and distance from prior threshold.
2. USD/JPY direction.
3. Gold direction.
4. BTC direction.
5. U.S. and Asian equity direction.
6. VIX / volatility state when verified.
7. Credit / liquidity stress state where available.
8. Whether the JPY condition persisted for 1/7/30/90/365 days.
9. Whether a crisis confirmation occurred within the matching declared temporal window.
10. Incremental effect on FP, FN, lead time, and trigger frequency when JPY is added as a secondary discriminator.

## Falsification conditions

Reject the JPY overlay as useful if any of the following is demonstrated on a frozen benchmark:

- JPY thresholds materially increase false positives without a compensating reduction in false negatives.
- JPY adds no incremental information after existing stress dimensions are included.
- JPY signals are systematically driven by BOJ-specific repricing but are repeatedly misclassified as global crisis stress.
- Threshold performance disappears when the observation window changes from one fixed horizon to another.

## Governance / provenance

This record is a measurement-layer artifact. It must not modify the frozen SC-FIX-0002 temporal attribution rule, and it must not be used to retroactively relabel earlier warnings.

The existing SC-FIX-0002 record remains **BLOCKED for promotion** pending complete scope-corrected upstream fixtures/provenance.

## Sources

- Reuters — yen rally / BOJ hike expectations, 2026-09-03.
- Reuters — gold market update, 2026-09-03.
- Myfin — daily JPY/KRW record, 2026-09-03.
- AP / The Close Report — 2026-09-02 equity closes.
- StatMuse Money / contemporaneous BTC records — BTC around 2026-09-02/03.
- Repository record: `docs/research/executions/SC-FIX-0002_VERIFICATION_RECORD_2026-09-03.md`.

## Lesson Learned

**JPY strength is not equivalent to crisis stress.** It can be caused by domestic Japanese policy repricing, global dollar weakness, intervention expectations, or broader risk aversion. The overlay therefore has to be treated as a secondary discriminator whose value is measured by incremental benchmark performance, not by narrative plausibility.

## Rule modification check

No change to the frozen temporal attribution rule.

New rule candidate to test (not yet promoted): **use JPY/KRW and USD/JPY jointly as the FX confirmation pair; do not classify JPY alone as crisis evidence.**

## Git storage decision

Persist this record as durable research evidence. The current market snapshot and threshold framework are sufficiently material to warrant a Git commit.
