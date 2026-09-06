# Anthropic IPO — FX + Indirect Investment Research Record v0.1

**Date:** 2026-09-06  
**Status:** RESEARCH FREEZE v0.1  
**Scope:** Anthropic IPO event, USD/KRW and JPY/KRW overlays, public-market proxy routes  
**Repository:** `chayobi03-cyber/investment`

## 1. Executive finding

Anthropic IPO should be modeled as an event chain rather than a single security trade:

```text
Anthropic IPO
  → valuation discovery
  → AI risk appetite / public-market validation
  → compute spending expectations
  → semiconductor / networking / data-center beneficiaries
  → USD/KRW translation for KRW investors
  → JPY/KRW as an Asian risk/liquidity overlay
```

The September 4, 2026 Reuters update moved the expected IPO marketing start to mid-October at the earliest, with the public prospectus now expected in late September. A valuation as high as $2T is being discussed, but this is a market scenario, not a confirmed IPO valuation. Reuters also reported a prospective $15B revolving credit facility. [Reuters, 2026-09-04]

## 2. Valuation sanity anchors

Reuters reported that Anthropic is being evaluated using a roughly $190B–$200B 2028 revenue forecast, while its disclosed May run-rate was about $47B. This implies that the public-market underwriting is explicitly forward-looking and depends on the assumption that revenue will grow faster than compute, training and hiring costs. [Reuters, 2026-08-14]

Reference multiples for scenario analysis:

| Scenario | Valuation | 2028E Revenue | EV/2028E Revenue |
|---|---:|---:|---:|
| Low | $1.0T | $190B | 5.3x |
| Mid-low | $1.25T | $190B | 6.6x |
| Mid | $1.5T | $195B | 7.7x |
| High | $1.75T | $200B | 8.8x |
| IPO headline | $2.0T | $190B–200B | 10.0–10.5x |

These are arithmetic scenario multiples, not fair-value estimates.

## 3. Critical accounting rule

Anthropic headline run-rate revenue MUST NOT be treated as GAAP revenue or as directly comparable with another AI company's headline revenue without reconciling accounting treatment, partner economics and gross-margin presentation.

For IPO validation, the required fields are:

- GAAP revenue
- revenue growth
- gross profit / gross margin
- compute cost
- operating cash flow
- free cash flow
- committed compute spend
- customer concentration and contract terms

## 4. Indirect investment map

### Tier A — economic linkage

- **AMZN:** Anthropic equity exposure + AWS/Trainium compute economics.
- **GOOGL:** Anthropic-related strategic/economic exposure + Google Cloud/TPU economics.
- **NVDA:** primary GPU/accelerated-compute demand transmission.
- **AVGO:** custom accelerators and networking / AI infrastructure transmission.
- **MU / SK hynix / Samsung Electronics:** memory/HBM and semiconductor-capex transmission.

The correct interpretation is not “Anthropic up means all beneficiaries up.” Each link must be tested against earnings sensitivity and valuation already embedded in the public company.

## 5. ETF proxy: ANTW

SEC filings confirm the **Anthropic AI Lab Ecosystem ETF (ANTW)** is structured as an actively managed ETF intended to invest in companies Harbor Capital believes are most closely positioned to benefit from the Anthropic ecosystem. The prospectus states a 0.59% management fee and allows exposure to companies across cloud computing, semiconductors, memory, networking hardware, data-center infrastructure, power/cooling and related AI-support industries. [SEC Harbor ETF filing, 2026-08-07]

Important status correction: the August 7 prospectus states that the funds had **not commenced operations as of the prospectus date**. Therefore ANTW must be classified as **registered/launch-stage proxy**, not as an already validated live performance instrument, until live operations and holdings are confirmed. [SEC Harbor ETF filing, 2026-08-07]

The prospectus also explicitly states the ETF is **not affiliated with Anthropic**, is not sponsored/endorsed by Anthropic, and that Anthropic does not select or influence its holdings. Therefore ANTW is an ecosystem proxy, not Anthropic equity exposure.

## 6. FX overlay

Current reference observations for this research date:

- USD/KRW ≈ 1,344.55
- 100 JPY/KRW ≈ 858.18

For a USD-denominated public-market proxy, KRW investor return should be evaluated as a combined equity and FX effect, not as equity return alone.

For a simple unhedged position:

```text
KRW return = (1 + USD asset return) × (1 + USD/KRW return) − 1
```

JPY/KRW is not a direct Anthropic factor. It is an Asian liquidity/risk overlay and should be used to test whether an apparent USD/AI signal is part of a broader regional capital-flow regime.

## 7. Required event-study benchmark

For the IPO event window, track at minimum:

### Event variables
- Anthropic prospectus publication
- IPO price range
- final IPO price
- first-day close
- first 5 trading days
- 20 trading days

### Market controls
- Nasdaq / QQQ
- S&P 500
- USD/KRW
- JPY/KRW
- DXY
- U.S. 10Y and 30Y Treasury yields

### Equity proxies
- AMZN
- GOOGL
- NVDA
- AVGO
- MU
- SK hynix
- Samsung Electronics

### Outcome metrics
- abnormal return vs benchmark
- peak/trough response
- lead/lag relative to IPO event
- cross-asset confirmation
- whether AI infrastructure equities respond more strongly than broad AI/software proxies

## 8. Falsification cases

The Anthropic IPO thesis should be weakened or rejected when one or more of the following occur:

1. IPO valuation falls materially below the market's pre-IPO headline range despite strong demand.
2. S-1 reveals weak gross margins or compute economics that prevent operating leverage.
3. Revenue growth decelerates materially relative to the valuation-implied path.
4. Public AI infrastructure beneficiaries do not confirm the claimed compute-demand transmission.
5. AI equities rally while USD/KRW or JPY/KRW signals point to a broader unrelated liquidity move, making Anthropic attribution weak.
6. ANTW holdings diverge materially from the intended Anthropic transmission chain.

## 9. Research classification

**Narrative strength:** HIGH — major financial media and bankers/investors are actively discussing a potentially record-scale AI IPO.  
**Evidence strength:** MEDIUM — growth evidence is strong, but public-company-quality margin/cash-flow disclosure is not yet available through the public S-1.  
**Crisis confirmation:** NONE — this is an investment-event study, not a crisis confirmation signal.

## 10. Next execution trigger

The next material trigger is **public S-1 / prospectus availability**. At that point, replace headline run-rate assumptions with audited/filing data, rebuild valuation scenarios, and run the event-study against the fixed benchmark above.

## Sources

- Reuters, 2026-09-04, “Anthropic IPO launch shifts toward mid-October, sources say.”
- Reuters, 2026-08-14, “Anthropic IPO valuation hinges on $190-200 billion 2028 revenue forecast, sources say.”
- SEC / Harbor ETF Trust, Form 485BPOS, August 7, 2026, Anthropic AI Lab Ecosystem ETF prospectus and SAI.
