# Stress Convergence v0.2 Validation Cycle — 2026-09-02

## 0. Cycle

`Hypothesis → Data → Threshold → Backtest → Falsification → Action → Lesson Learned → Rule → Git`

## 1. Hypothesis

The current early-warning hypothesis is not "2008-style crisis is already here". It is:

> A rates-led stress build-up can precede broad credit stress, and AI-capex financing can amplify the transmission from long-end yields to corporate credit and equity valuation.

Current transmission graph:

`Geopolitics → Energy → Inflation → Fed → Long Rates → Credit Cost`

parallel:

`AI CapEx → Financing → Private Credit / Corporate Debt → Credit Stress`

US layer principle:

`Long-end Treasury pressure + sticky inflation/energy + weakening labor + rising AI/corporate debt supply`

with HY/IG spreads and VIX as confirmation rather than the sole first trigger.

## 2. Data

Current repository evidence establishes the following 2026-09-02 snapshot:

- Fed funds target: 3.50%–3.75% after the 2026-07-29 FOMC.
- July 2026 CPI: +3.4% y/y; core CPI +2.5% y/y.
- July 2026 payroll: -23k; unemployment 4.1%; prior May/June payroll revisions combined -103k.
- 2026-09-01 Treasury yields: 10Y ~4.18%; 30Y ~5.27%.
- HY OAS: 2.63% on 2026-08-31, below July's 2.85%.
- VIX: 14.51 on 2026-08-27.
- AI financing: 2026 AI-related debt issuance reported around $220B; August US IG corporate borrowing reported at a record $164B.

Source-of-truth repository inputs: `docs/research/us-layer-2026-09-02.md` and `docs/research/market/2026-09-02_macro-risk-update.md`.

## 3. Threshold

The existing provisional architecture is retained for testing only:

### Level 1 — Watch
Any 2 signals inside 20 trading days:

1. Long-end yield pressure while inflation expectations fail to improve.
2. Unemployment +0.3pp from local low OR 3-month payroll trend negative.
3. AI/mega-cap credit spreads widen materially relative to IG.
4. HY OAS +75bp from local low.
5. VIX >20 for 5 trading days.

### Level 2 — Stress convergence
3 or more signals, including at least one rates/inflation signal and one credit/labor signal.

### Level 3 — Crisis confirmation
Broad credit + labor + equity volatility confirmation, e.g. HY OAS +150bp from local low, VIX >30, labor deterioration, and persistent long-end elevation.

**Important:** item 1 was not operationally defined in the original note. For future machine-testable use it should become a fixed numeric rule, not discretionary language.

## 4. First-pass historical backtest / falsification

Historical stress windows required by the project were reviewed against the structure using authoritative historical descriptions and market-series documentation.

### 2000–2003 dot-com bust

**Signal behavior:** VIX and equity drawdown eventually confirmed severe stress, while the key failure mode of a rates-led trigger is timing: long Treasury yields were not required to stay high throughout the equity bust.

**Result:** the proposed rates-led trigger can miss a valuation-driven equity crash if credit/labor have not yet confirmed.

**Classification:** partial FN risk for an equity-led shock.

### 2007–2009 global financial crisis

**Signal behavior:** credit stress, labor deterioration, and VIX ultimately confirmed together. Treasury yields did not provide a monotonic "higher is worse" signal throughout the crisis; they fell strongly during flight-to-quality phases.

**Result:** Level 2/3 structure is directionally valid as a convergence detector, but a static long-yield direction cannot be treated as a universal crisis variable.

**Classification:** broad crisis detection PASS; long-rate direction as universal trigger FAIL.

### March 2020 COVID shock

The New York Fed documented a rapid fall in the 10Y yield before and during the shock, while VIX surged and Treasury-market liquidity deteriorated. The Federal Reserve documented VIX reaching 82.7 and severe market moves.

**Result:** the proposed requirement that Level 2 include a positive long-rate signal would create a potential FN during the initial COVID shock.

**Classification:** explicit FN / architecture weakness.

### 2022 inflation / tightening regime

This is the closest historical analogue for the current rates-led hypothesis: inflation and policy tightening drove higher Treasury yields and equity repricing, while systemic credit stress was delayed and less severe than 2008.

**Result:** the rates + inflation + valuation channel is useful and should remain. However, VIX/HY confirmation should not be required for early Watch status.

**Classification:** leading-signal behavior PASS; confirmation timing PASS.

## 5. Falsification findings

### Falsified assumptions

1. **"Long-end yields rising" is not a universal crisis precursor.** 2008 and 2020 show crisis phases where yields fell or behaved non-monotonically.
2. **VIX/HY as initial trigger is too late for a rates-led regime change.** The current 2026 snapshot has VIX 14.51 and HY OAS 2.63% despite materially elevated long-end yields.
3. **AI financing cannot yet be treated as a long-history backtest feature.** It is structurally important but the series definition and history are not standardized enough for the core historical score.

### Surviving assumptions

1. A convergence model is superior to a single-indicator crisis trigger.
2. Rates/inflation can lead credit in a tightening-driven regime.
3. Credit and volatility are better treated as confirmation layers for the early-warning architecture.
4. Different shock types require separate sub-regimes: inflation/rates shock, credit/liquidity shock, and exogenous growth shock.

## 6. Action rule

Current 2026-09-02 status remains:

**US = YELLOW/ORANGE early warning, NOT Level 3 crisis.**

Action framework:

- Do not classify current conditions as a 2008-style systemic crisis.
- Keep Level 1 Watch active because rates/Fed/energy/AI-financing axes are simultaneously elevated.
- Do not wait for VIX >20 or HY +75bp before acknowledging a rates-led deterioration.
- Escalate to Level 2 only after an independent confirmation from labor or credit arrives.
- Escalate to Level 3 only when broad credit + labor + volatility jointly confirm.

Korea Layer implication:

A US Level 2 event should increase the weight of the US input in the KOSPI threshold model, but should not itself force a KOSPI entry decision without Korea-specific confirmation.

## 7. Lesson Learned

The original model mixed **shock direction** with **stress state**.

The stronger abstraction is:

> **Detect the shock regime first, then apply regime-specific thresholds.**

Three sub-regimes should be separated:

1. `Rates/Inflation Shock`
2. `Credit/Liquidity Shock`
3. `Growth/Exogenous Shock`

Stress Convergence is the cross-regime confirmation layer, not a rule that every crisis must exhibit the same directional movement in all variables.

## 8. Rule modification decision

**YES — Rule modification required.**

### v0.2 → v0.2.1 proposed change

Replace the universal Level-2 requirement:

`3 signals including 1 rates/inflation + 1 credit/labor`

with regime-aware gates:

- **Rates/Inflation regime:** rates + inflation + either labor or credit.
- **Credit/Liquidity regime:** credit + volatility/liquidity + either labor or market drawdown.
- **Growth/Exogenous regime:** growth/labor + market drawdown/volatility + either credit or policy shock.

AI financing remains an amplifier / secondary axis until a reproducible historical proxy is frozen.

## 9. Git decision

**YES — save.**

Reason:

- This cycle changes the interpretation of v0.2.
- The falsification result is durable project knowledge.
- The regime-aware rule is a methodological change that must remain auditable.

## 10. Next executable research task

Build a regime-specific backtest with fixed numeric definitions for:

- Rates shock: 10Y and 30Y change thresholds over fixed lookback windows.
- Inflation shock: CPI/core CPI or breakeven acceleration.
- Labor shock: unemployment change and 3M payroll trend.
- Credit shock: HY/IG OAS change from local low.
- Volatility shock: VIX persistence and peak level.
- Equity shock: S&P 500 drawdown.

Historical windows: 2000, 2008, 2020, 2022 + explicit false-positive periods.

Required outputs: `FP / FN / lead time / trigger frequency / regime confusion matrix`.

### Status

- Hypothesis: **SURVIVES, but regime-qualified**
- Data: **SUFFICIENT for first-pass architecture review**
- Threshold: **PROVISIONAL**
- Backtest: **FIRST-PASS / NOT FULL-SERIES VALIDATION**
- Falsification: **COMPLETED FOR CURRENT ARCHITECTURE**
- Action: **WATCH / NO CRISIS CONFIRMATION**
- Rule update: **REQUIRED**
- Git save: **REQUIRED**
