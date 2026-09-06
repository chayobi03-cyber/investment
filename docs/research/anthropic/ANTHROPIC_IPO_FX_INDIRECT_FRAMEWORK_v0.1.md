# Anthropic IPO + FX + Indirect Exposure Framework v0.1

**Project:** Investment — Capital Preservation Research  
**Status:** WORKING FRAMEWORK  
**Effective date:** 2026-09-06

## Objective

Track the Anthropic IPO as a falsifiable market event and connect it to KRW investor outcomes through USD/KRW, JPY/KRW regime overlays, and public-market proxies.

## Event state

- Anthropic confidentially submitted a draft S-1 on 2026-06-01. Shares offered and IPO price were not set at that time.
- Latest Reuters reporting (2026-09-04): prospectus expected in late September; marketing expected around mid-October; listing potentially before the November U.S. midterm elections. Reported valuation ceiling is up to $2T; this is a scenario, not a confirmed IPO valuation.
- Anthropic Series H (2026-05-28): $65B financing at $965B post-money valuation; company reported $47B+ run-rate revenue.

## Exposure buckets

### 1. Direct Anthropic exposure
Unavailable pre-IPO. Reassess after public S-1 and IPO pricing.

### 2. Strategic corporate proxies

- AMZN: Anthropic equity + AWS cloud/Trainium economics.
- GOOGL: Anthropic relationship + Google Cloud/TPU economics.
- NVDA: GPU demand transmission; not a pure Anthropic proxy.
- AVGO: custom accelerator/networking transmission through Google/Broadcom relationship.
- MU / SK hynix / Samsung: memory/logic infrastructure transmission.

These are not interchangeable. Each must be mapped to a causal earnings mechanism before use as an IPO proxy.

### 3. ANTW thematic ETF

Harbor ETF Trust's Anthropic AI Lab Ecosystem ETF (ANTW) is a registered/effective fund vehicle with a 0.59% management fee. It is actively managed and non-diversified, normally invests at least 80% in companies judged economically connected to Anthropic, and may invest in IPO/privately offered securities. The prospectus explicitly states investors should **not** expect direct Anthropic exposure; direct private exposure, if available, is capped at 15% of net assets. The prospectus also states the fund had not commenced operations as of publication, so live NAV/holdings/performance must be verified before treating ANTW as an investable time series.

## FX layer

Primary: USD/KRW. Current reference around 1,344.55 KRW/USD on 2026-09-05.  
Secondary regime overlay: JPY/KRW. Current reference around 858.18 KRW per 100 JPY on 2026-09-06.

KRW investor return for a USD asset:

    R_KRW = (1 + R_asset_USD) * (USDKRW_t / USDKRW_0) - 1

Use exact transaction-date FX for event studies; do not substitute a monthly average unless explicitly specified.

## Core hypotheses

H1 — Anthropic IPO success supports AI risk appetite and strengthens public-market AI multiples.

H2 — Anthropic growth converts into compute demand, benefiting infrastructure providers more reliably than the model company itself if gross margin remains constrained.

H3 — AMZN/GOOGL should have distinct exposure because each combines strategic relationships with a much larger unrelated corporate base; therefore IPO reaction must be measured on an incremental-value basis rather than headline beta.

H4 — ANTW, once operational, should provide a cleaner ecosystem proxy than any single public company, but thematic-model error, concentration, turnover and premium/discount risk can create large tracking differences.

H5 — USD/KRW can amplify or offset a USD asset's KRW return; JPY/KRW is a regime variable and should not be treated as a causal input to Anthropic valuation without evidence.

## Required falsifiers

- S-1 reported revenue materially below externally cited run-rate claims.
- Gross margin/cash flow deteriorates as inference and training costs scale.
- IPO pricing implies a valuation materially below the $965B Series H reference or materially below the leading forward-revenue scenario.
- Anthropic demand grows while public infrastructure beneficiaries fail to show corresponding revenue/earnings transmission.
- AI valuation compresses despite Anthropic operating strength, indicating a macro/liquidity regime dominates idiosyncratic IPO strength.
- FX adjustment reverses the apparent USD-return advantage for a KRW investor.

## Event-study specification

Anchor t0 = first public S-1/prospectus release or confirmed IPO pricing event, depending on question.

Measure:
- t0, +1d, +5d, +20d, +60d
- absolute return
- abnormal return versus Nasdaq / SOX / a broad AI benchmark
- USD/KRW-adjusted KRW return
- JPY/KRW change as regime overlay
- correlation/beta to Anthropic event

For each proxy record:
- causal linkage
- exposure purity
- independent company-specific catalysts
- valuation regime
- FX-adjusted return

Do not rank proxies until these fields are populated.

## Decision rule

No trade signal from narrative alone. IPO event is a research trigger. Any action level requires the standard Investment Research Loop: hypothesis → data → threshold → backtest → falsification → action.

## Source hierarchy

Follow `docs/research/NARRATIVE_VALIDATION_WORKFLOW_v0.1.md`. Prefer SEC/official company filings for numerical and legal facts; use Reuters/FT/WSJ and similar sources for current event timing and market interpretation; explicitly record source independence.
