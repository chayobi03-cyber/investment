# Next Session Handoff — Multi-Asset Expansion

Date: 2026-10-07
Previous session: `LESSONS_LEARNED_2026-10-07_MOBILE_PUSH_ASSET_REVIEW.md` (#16–#21)

## Goal

Extend review beyond crypto to **gold, bonds, rates, oil, JPY, equities (indices + leading companies) and emerging
technology themes**, built so that adding an asset or theme is a configuration change, not new code.

Fail-closed state is unchanged and stays so: `BUY_ALLOWED=false`, `EXECUTION_ALLOWED=false`, no threshold mutation.

## What already exists (reuse before building)

| Area | Existing pieces |
|---|---|
| Multi-asset control plane | `src/investment_pipeline/multi_asset_subagents.py` (`AssetClass` = EQUITY, GOLD, CRYPTO; data_pit / regime / permission / risk / evidence / decision agents), `config/multi_asset_subagents_v0.1.json`, `decision_gate.py`, hallucination guard + source retrieval/quality/conflict agents |
| Macro / rates / FX / oil / gold series | `config/market_monitor.json` (US10Y, US2Y fut, USD/KRW, USD/JPY, DXY, WTI, Brent, gold; KOSPI/KOSDAQ/S&P/Nasdaq/SOX/VIX), `scripts/auto_market_monitor_v1.py` (yfinance), `scripts/crypto/fetch_fred_permission_macro.py` (FRED: DGS10, DFII10, DCOILWTICO …) |
| Equities / leaders | `config/market_monitor.json` Korea leaders (Samsung, SK Hynix, …) + TSM, AVGO; `docs/investment/STOCK_SCORE_V1*.md`, `STOCK_DATA_SOURCE_REGISTRY_2026-09-08.md`, KRX/OpenDART connectors |
| Prior research | `docs/research/market/2026-09-02-gold-btc-overlay.md`, `2026-09-03-jpy-stress-confirmation-framework.md`, `2026-09-02_macro-risk-update.md`, Anthropic IPO indirect-investment notes, `MARKET_REGIME_ENGINE_V1.md`, stress-convergence research |
| Review pattern to generalize | `config/crypto_asset_review_v0.1.json` + `scripts/crypto/run_asset_review_v0_1.py`: preregistered contract, PIT data, frozen vs self-calibrated variant, 7-condition OOS gate, walk-forward, screen + tiers, weekly workflow |

## Proposed approach

1. **Asset registry, not code per asset.** One `config/asset_registry_v0.1.json` with an entry per instrument:
   class (`EQUITY`/`GOLD`/`RATES`/`FX`/`COMMODITY`/`CRYPTO`/`THEME`), PIT source + `available_at` rule, unit,
   trading calendar, liquidity proxy, and the role it plays (signal asset vs. permission/macro input).
2. **Classes the control plane doesn't model yet:** add `RATES`, `FX`, `COMMODITY`, `THEME` to `AssetClass`
   (enum + config + tests) without touching the crypto contract.
3. **Generalize the review runner** from crypto to any registry entry: the same frozen-vs-calibrated comparison and gate,
   with class-appropriate calendars (equities skip weekends; rates are in yield/bp, not price %).
4. **Cross-asset relationships as permission inputs, not signals:** e.g. real yields → gold, USD/JPY carry stress → risk
   assets, oil shock → inflation/rates, SOX/leaders → tech theme breadth. Each relationship is a preregistered,
   testable claim with PIT data and a stated lag.
5. **Leading companies and new-tech themes:** define a theme as a basket in the registry (e.g. AI semis: TSM, AVGO, SK Hynix,
   Samsung…) with explicit membership dates, so a basket can't silently gain today's winners (survivorship).
6. **Phone app:** extend the tabs and push to non-crypto assets only after (1)–(3), and only for sources reachable from a
   browser (Yahoo isn't CORS-accessible; FRED needs a key, so those would be served from Actions-built JSON on Pages).

## Constraints carried forward

- PIT and lookahead rules are never relaxed; macro data needs source-specific `available_at` (release time, not observation date).
- Preregister every new gate or threshold before looking at results; don't lower minimums after a failed run.
- Dispatch push-only workflows on the PR branch; use CI-pinned versions; parity tests for any duplicated logic.
- Theme or stock claims must pass the hallucination guard (source-backed, dated); no unsourced "latest technology" claims.

## Open decisions to settle at the start of the next session

- Scope of the first slice (suggested: gold + US10Y/real yield + USD/JPY + WTI as the macro core, then equities).
- Data sources per class and whether a FRED API key / KRX key will be provided as repo secrets.
- Market focus for equities and leaders (Korea, US, or both) and which themes to track first.
- Whether the phone app should show macro/equity state or stay crypto-only.

## Known issues inherited

- `r01-provenance.yml` has failed on every `main` push since at least 2026-09-26 (not investigated).
- The per-asset crypto OOS gate is underpowered (< 20 events per asset); any pooled gate must be preregistered.
