# 2026-10-13 Portfolio Review — Three-Account Snapshot

## Record status

- **Record type:** PORTFOLIO_REVIEW / RESEARCH_ONLY
- **As-of:** 2026-10-13 (intraday screenshots supplied by the user; exact capture time not shown)
- **Sources:** user-supplied app screenshots of (1) crypto exchange KRW account, (2) Toss Securities default account, (3) pension savings account (연금저축)
- **FX used:** USD/KRW ≈ 1,336.1, implied from the Toss screen (KRW-converted total minus domestic holdings ÷ USD holdings). Consistent with the 2026-10-12 local close of 1,335.0.
- **Not covered:** the LOCKED Samsung Electronics 79-share core is not in these screenshots. Where it is mentioned below, its value is an **estimate** at the 2026-10-12 close (₩250,500 × 79 ≈ ₩19.79M), not an observed balance.
- **Market context:** [2026-10-13 pre-open review](../market/2026-10-13_0737_preopen_research.md) — RISK-OFF, `BUY_ALLOWED=false`.
- **This is not an execution instruction.** It is a diagnosis against [Portfolio Allocation Rule v0.1](../governance/PORTFOLIO_ALLOCATION_RULE_v0.1.md) and [Portfolio Factor Exposure Rule v1.1](PORTFOLIO_FACTOR_EXPOSURE_RULE_V1.md).

## 1. Raw holdings

### 1.1 Crypto exchange

| Item | Value (KRW) | Note |
|---|---:|---|
| KRW balance | 2,003,592 | Fully orderable |
| BSV / XEC / USDT | 3 | Dust. The displayed 99,308% return is a cost-basis artifact on a ~₩1 position, not performance |
| Unclaimed deposit interest | 1,183 | Not yet claimed |

### 1.2 Toss Securities (taxable)

Cash: KRW 26,902,598 + USD 1,042.37 (≈ ₩1.39M). Invested: ₩22,355,999 (−₩1,984,008, −8.1%).

| Holding | Qty | Value | P/L |
|---|---:|---:|---:|
| Samsung Electronics pref. | 2 | ₩348,196 | −5.0% |
| Korea Aerospace (KAI) | 3 | ₩329,537 | −13.6% |
| NAVER | 2 | ₩349,193 | −12.0% |
| SK hynix | 4 | ₩5,906,357 | −5.1% |
| TIGER US S&P500 | 11 | ₩284,842 | −0.1% |
| TIGER US Nasdaq100 | 7 | ₩1,262,877 | +3.2% |
| TIGER US Dividend Dow Jones | 37 | ₩523,607 | −6.3% |
| TIGER JPY futures | 100 | ₩778,265 | −1.9% |
| Rigetti Computing | 51 | $666.65 | −19.9% |
| Broadcom | 1 | $350.12 | −2.9% |
| NVIDIA | 2 | $447.04 | +1.7% |
| SCHD | 76 | $2,528.85 | +0.5% |
| SGOV | 54 | $5,417.77 | −0.2% |

### 1.3 Pension savings (tax-deferred)

Total ₩74,563,072; P/L −₩702,181; cash (T+2) ₩12,494,977. Holdings sum + cash reconciles exactly to the total.

| Holding | Qty | Value | P/L |
|---|---:|---:|---:|
| KODEX 200 | 29 | ₩2,760,945 | +7.65% |
| KODEX Semiconductor | 21 | ₩2,731,575 | +41.67% |
| TIGER US Nasdaq100 | 32 | ₩5,775,200 | +38.53% |
| TIGER US S&P500 | 171 | ₩4,428,900 | +0.49% |
| ACE KRX Gold Spot | 385 | ₩9,632,700 | −19.45% |
| KODEX India Nifty50 | 180 | ₩1,879,200 | −18.22% |
| TIGER US Dividend Dow Jones | 489 | ₩6,921,795 | −7.48% |
| KODEX CD Rate Active (synthetic) | 26 | ₩27,937,780 | −0.09% |

## 2. Functional-bucket view (Allocation Rule v0.1)

Denominator: the three accounts above = **₩127.22M** (active sandbox, LOCKED Samsung excluded).

| Bucket | Members | Value | Weight | 2026-09-07 | Balanced target | Gap vs target |
|---|---|---:|---:|---:|---:|---:|
| Dry Powder | CD ETF, pension cash, Toss KRW/USD cash, SGOV | ₩75.97M | **59.7%** | 52.0% | 42% | **+₩22.5M** |
| Hedge | Gold, JPY futures | ₩10.41M | 8.2% | 12.3% | 11% | −₩3.6M |
| US Core/Growth | S&P500, Nasdaq100 (both accounts), NVDA, AVGO | ₩12.82M | **10.1%** | 13.5% | 22% | **−₩15.2M** |
| US Dividend | Dividend Dow Jones (both), SCHD | ₩10.82M | 8.5% | 11.5% | 11% | −₩3.2M |
| Domestic Equity | KODEX 200, KODEX Semi, SK hynix, Samsung pref., KAI, NAVER | ₩12.43M | **9.8%** | 6.5% | 7% | **+₩3.5M** |
| Satellite | India, Rigetti | ₩2.77M | 2.2% | 3.5% | 5% | −₩3.6M |
| Crypto | Exchange KRW (+dust) | ₩2.00M | 1.6% | — | (Other 2%) | — |

The sandbox grew from ~₩90.4M (2026-09-07) to ~₩127.2M. Whether this is new money or an account that was missing from the 09-07 snapshot is **unverified**; it should be confirmed before comparing returns across the two dates.

## 3. Findings

### F1. Dry Powder drifted *further* from target, and the deployment rule still has no triggers

Dry Powder rose from 52.0% to 59.7% while the Balanced base case is 42%. The ₩9.0M staged deployment planned on 2026-09-07 did not happen, and Allocation Rule §7 still says "exact trigger conditions are to be defined separately".

Meanwhile KOSPI is ~30% below its 2026-06-22 record and −8.85% since 2026-10-02 — exactly the kind of drawdown the staging ladder was written for. With no predeclared trigger, the result is the failure mode the rule itself predicted: a discretionary "buy now vs wait" decision under stress. Holding cash today is consistent with `BUY_ALLOWED=false`; the defect is that no state of the world is yet defined in which it becomes `true`.

### F2. Korean semiconductor exposure was increased against the concentration rule

Allocation Rule §6: *do not increase Korean semiconductor exposure mechanically while the fixed Samsung core remains this large.* Since 2026-09-07, SK hynix (₩5.91M, now the largest single tradable stock position) and Samsung pref. were added. Domestic Equity is now 9.8% vs a 7% target.

Tradable Korean semiconductor exposure, direct only: SK hynix ₩5.91M + KODEX Semiconductor ₩2.73M + Samsung pref. ₩0.35M = **₩8.99M (7.1% of sandbox)**. Adding the estimated LOCKED Samsung core (~₩19.79M) gives ≥ ₩28.8M, about **19.6% of the ~₩147M whole portfolio** — before KODEX 200 look-through, which is **UNKNOWN** (no PIT constituent snapshot; per Factor Rule §4 it must not be treated as zero).

No thesis or risk budget for the SK hynix addition is recorded in the repository. On 2026-10-12 SK hynix fell 4.52% and SOX fell 2.7%; the screenshot price (~₩1.48M/share) implies a further decline on 2026-10-13.

### F3. Global AI/semiconductor is one factor across many wrappers

SK hynix, KODEX Semiconductor, Samsung (locked + pref.), NVIDIA, Broadcom, Rigetti and the semiconductor-heavy Nasdaq-100 all load on the same AI/semiconductor cycle. The 2026-10-12 session showed it moving together (KOSPI semis −4.4%/−4.5%, SOX −2.7%, Nasdaq −0.44%). The portfolio looks diversified by ticker count (21 instruments) but its equity risk is dominated by one factor plus Korea beta.

### F4. Same ETFs held in both the taxable and the pension account

TIGER S&P500, Nasdaq100 and Dividend Dow Jones are held in both Toss (₩2.07M total) and the pension account (₩17.13M). Domestic-listed overseas-equity ETFs are taxed as dividend income (15.4%, counted toward financial-income aggregation) in a taxable account, but are tax-deferred inside the pension account. The Toss lots are small, but every new purchase of these three ETFs in the taxable account is the less tax-efficient choice.

### F5. Small single-stock positions without a recorded thesis

KAI (₩0.33M), NAVER (₩0.35M), Samsung pref. (₩0.35M), Broadcom (1 share), NVIDIA (2 shares) are each < 0.5% of the sandbox. They cannot move portfolio returns but each one adds monitoring load and decision noise. Rigetti (−19.9%) is the largest loss in percentage terms in the taxable account. Allocation Rule §6 already says direct NVIDIA is satellite, not core; the same treatment applies to Broadcom.

### F6. Cash is fragmented across four places with different yields

| Location | Amount | Comment |
|---|---:|---|
| Pension cash (T+2) | ₩12.49M | Idle inside the account where the CD ETF already sits |
| Toss KRW cash | ₩26.90M | Largest idle balance; yield depends on Toss deposit terms (not verified) |
| Toss USD cash | $1,042 | Idle while SGOV is held in the same account |
| Crypto exchange KRW | ₩2.00M | Earmarked dry powder for the crypto entry monitor; deposit interest unclaimed |

### F7. The gold hedge did not hedge this drawdown

Gold is −19.45% at the same time Korean equities are falling. In a rates/oil/inflation-driven selloff (US 10Y ~5.24%, Brent ~$107) higher real yields can hurt gold and equities together. This is an observation, not a sell signal: the hedge bucket is already under target (8.2% vs 11%), and the role of gold should be re-examined by regime rather than by its P/L.

### F8. Data hygiene

- The 99,308% crypto return is a dust artifact and must never be ingested as a performance number.
- The LOCKED Samsung core lives outside these screenshots; any whole-portfolio number needs that account captured on the same date.
- The 09-07 → 10-13 denominator change (F1/§2) is unexplained.

## 4. Improvement directions

Ordered by priority. Items marked **[PROPOSAL]** change a rule and must go through Allocation Rule §10 (evidence, old rule, new rule, reason, failure mode) before adoption.

### P1. Define the deployment triggers before the next buy decision **[PROPOSAL]**

Write the missing trigger table for Allocation Rule §7, using the project's existing signals (market monitor regime, KOSPI/S&P drawdown from 52-week high, long rates, USD/KRW, JPY, breadth). It should fix in advance:

- the deployable amount per stage (currently ~₩22.5M excess Dry Powder vs Balanced, not the ₩9.0M from 09-07);
- what confirms a stage (drawdown level **and** a stabilisation condition, so a stage is not a falling-knife trigger);
- the destination bucket for each stage (see P2);
- what happens if the monitor is invalid — today it is (Issue #27), so the answer must be "no stage fires".

Thresholds must come from a backtest in this repo, not from this note.

### P2. Point new equity money at the US Core gap, not at Korea

The largest underweight is US Core/Growth (−₩15.2M); Domestic Equity is already overweight (+₩3.5M). When P1 permits deployment, the default destination is broad US index exposure (TIGER S&P500 first, Nasdaq-100 second given F3) **inside the pension account**, funded first from the ₩12.49M pension cash. No further Korean semiconductor additions until a written thesis and risk budget exist (Allocation Rule §6).

### P3. Record a thesis or a plan for SK hynix

Either record why SK hynix was added (thesis, size limit, invalidation level) or classify it as a Domestic Equity overweight to be reduced on strength. Per the market note, a down day is not an add signal, and averaging down would deepen F2. Selling into today's RISK-OFF session is likewise not implied by this review; the requirement is a predeclared rule.

### P4. Account placement rule **[PROPOSAL]**

- Domestic-listed overseas ETFs (S&P500, Nasdaq100, Dividend Dow Jones, India, gold): buy only in the pension account. Leave the small Toss lots as they are (no forced sale); stop adding there.
- Toss (taxable): direct US ETFs/stocks and Korean stocks only.
- Before deploying Toss KRW cash, check remaining 2026 pension contribution room (annual cap ₩18M; tax-credit base ₩6M, ₩9M with IRP). Contributions already made this year are not visible in the screenshots.
- Year-end: review US realised gains vs unrealised losses (e.g. Rigetti) against the ₩2.5M annual capital-gains allowance.

### P5. Satellite discipline

Satellite (India, Rigetti, and single names KAI/NAVER/Samsung pref./NVDA/AVGO) totals ≈ ₩4.86M (≈ 3.8%). For each: one line of thesis plus an exit/size rule, or consolidate. Do not add new single names until each existing one has that line.

### P6. Cash housekeeping (no market-timing content)

- Pension cash ₩12.49M → hold in the CD Rate ETF until a P1 stage fires (same liquidity, earns the CD rate).
- Toss USD $1,042 → SGOV, or keep as USD for the next US purchase.
- Confirm the Toss KRW deposit yield; park in a short-rate instrument if it is materially below the CD ETF.
- Crypto: claim the ₩1,183 interest; hide dust; the ₩2.0M stays gated by the crypto entry monitor.

### P7. Implement the portfolio snapshot schema

Factor Rule §10 already specifies the snapshot fields and §11 the tests (T1–T12). This review was done by hand from screenshots; the next step is a snapshot file (one row per holding with account, tradability, factor map, provenance) so F2/F3 are computed, and KODEX 200 look-through becomes a real number instead of UNKNOWN.

## 5. Lessons learned

1. A staging ladder without triggers is not a deployment rule. The cash reserve grew from 52% to 60% across a 30% KOSPI drawdown because no stage could fire.
2. Concentration rules erode through small adds in a second account. SK hynix entered via the taxable account while the rule was written around the pension/Samsung view; the rule must be checked across all accounts on every buy.
3. Account placement is part of allocation. The same ETF in two accounts has two different after-tax returns.
4. Hedges must be evaluated by regime. Gold falling with equities in a rates-driven selloff is a known failure mode, not noise.
5. Exchange-reported return percentages on dust positions are not data.

## 6. Follow-up checklist

- [ ] Capture the Samsung 79-share account on the same date; recompute whole-portfolio weights
- [ ] Explain the ₩90.4M → ₩127.2M denominator change
- [ ] Draft the §7 trigger table (P1) with a backtest
- [ ] Record SK hynix thesis / plan (P3)
- [ ] Check 2026 pension contribution room (P4)
- [ ] Cash housekeeping (P6)
- [ ] Portfolio snapshot file + T1–T12 tests (P7)
