# Gold + Bitcoin Overlay — 2026-09-02

## 목적

기존 Stress Convergence 구조에 **Gold**와 **Bitcoin (BTC)**을 추가한다.

핵심 원칙은 두 자산을 동일한 성격의 안전자산으로 취급하지 않는 것이다.

- **Gold**: 지정학·인플레이션·실질금리·달러·재정불안의 교차확인자
- **Bitcoin**: 글로벌 유동성·위험선호·레버리지·크립토 금융스트레스의 고베타 확인자

따라서 자산 가격의 방향 자체보다 **가격 반응과 거시 변수의 조합**을 신호로 사용한다.

---

## 1. Gold Layer

### 역할

Gold는 다음 경로를 확인하는 자산으로 정의한다.

`Geopolitics → Inflation expectations → Real rates / USD → Gold`

동시에 재정·통화 신뢰 문제의 보조 신호로 사용한다.

### 중요한 해석 규칙

Gold 상승 = 즉시 금융위기라고 판정하지 않는다.

특히 다음을 분리한다.

1. **Inflation hedge regime**
   - 기대인플레이션 상승
   - 실질금리 하락 또는 안정
   - 달러 약세
   - Gold 상승

2. **Geopolitical hedge regime**
   - 지정학적 충격 확대
   - Gold 상승
   - Oil 상승

3. **Debasement / fiscal-risk regime**
   - 장기재정 우려 확대
   - 통화가치/국채 신뢰 우려
   - Gold와 장기채 금리의 동반 불안 가능성

4. **Forced-liquidity regime**
   - 신용·유동성 스트레스 급증
   - USD 및 Treasury 수요가 급증
   - Gold도 일시적으로 하락 가능

4번 때문에 **Gold의 단기 하락을 단순 risk-on으로 해석하지 않는다.**

### 현재 관측

2026-09-02 Reuters 보도에서 현물 Gold는 약 **$4,303/oz**까지 하락했다. 중동 충돌로 유가가 상승하고 인플레이션·Fed 금리인상 우려가 커지는 동시에 미국 국채금리와 달러가 강해지면서 무이자 자산인 Gold가 압박받는 구조였다. citeturn161051news36turn161051news35

이는 현재 Gold가 **지정학 리스크 자체보다 실질금리·달러·Fed 경로의 영향을 강하게 받고 있음**을 보여주는 확인 사례다.

### Gold 모니터링 지표

- Gold spot / front-month futures
- Gold 20D / 60D return
- Gold / USD
- Gold / real yield (10Y TIPS)
- Gold / Brent
- Gold / S&P 500
- Central-bank gold demand
- Gold ETF flows

### Gold trigger 후보

**G1 — Inflation hedge confirmation**

`Gold ↑ + 10Y breakeven ↑ + real yield ↓`

**G2 — Geopolitical confirmation**

`Gold ↑ + Oil ↑ + geopolitical risk ↑`

**G3 — Fiscal/debasement confirmation**

`Gold ↑ + USD ↓ + long-end yields ↑`

**G4 — Forced liquidation warning**

`Gold ↓ + USD ↑ + Treasury yields ↑ + credit spreads ↑`

G4는 Gold 자체의 약세를 risk-on으로 오판하지 않도록 하는 방어 규칙이다.

---

## 2. Bitcoin Layer

### 역할

BTC는 현재 Stress Convergence에서 **유동성·위험선호·레버리지 스트레스의 고베타 변수**로 편입한다.

주 경로는 다음과 같다.

`Global liquidity → USD / real rates → Risk appetite → BTC`

보조 경로:

`Crypto leverage / ETF flows / funding → BTC → broader risk sentiment`

### 중요한 해석 규칙

Bitcoin을 Gold와 동일한 safe haven으로 모델링하지 않는다.

2026년 9월 발표된 연구는 2014-12~2026-02 일별 데이터를 대상으로 Gold와 Bitcoin의 미국 주식 스트레스 방어력을 재검토한 결과, 두 자산 모두 일관된 safe-haven protection을 제공하지 않았다고 보고한다. Gold는 불안정한 분산효과에 가깝고 Bitcoin은 스트레스와의 상호작용이 오히려 양(+)의 방향으로 나타났다. citeturn161051search10

따라서 본 프로젝트에서는 BTC를 **crash insurance**가 아니라 **financial-conditions / liquidity thermometer**로 관리한다.

### 현재 관측

2026-09-01 BTC는 장중 약 **$77,946**까지 하락했고, 8월에는 약 25% 상승한 뒤 다시 $80,000 아래로 움직였다. 최근 시장에서는 BTC와 Gold가 달러 약세·재정불안에 대한 대안자산 수요를 같이 받은 구간이 있었지만, 2026-09-02에는 금·BTC 모두 전반적인 시장 스트레스 속에서 약세를 보였다. citeturn161051news0turn161051news44turn161051news34

즉, BTC 상승을 단독으로 **risk-off**로 해석하지 않는다.

### BTC 모니터링 지표

- BTC spot
- BTC 20D / 60D return
- BTC realized volatility
- BTC / Nasdaq relative strength
- BTC / Gold relative strength
- Spot BTC ETF net flows
- Perpetual futures funding
- Open interest
- Stablecoin supply / liquidity
- USD / real-rate sensitivity

### BTC trigger 후보

**B1 — Liquidity/risk-on confirmation**

`BTC ↑ + Nasdaq ↑ + real yields ↓/stable + USD ↓`

**B2 — Speculative excess**

`BTC ↑ + leverage/OI ↑ + funding ↑ + ETF flows deteriorate`

**B3 — Liquidity stress**

`BTC ↓ sharply + equities ↓ + credit spreads ↑ + USD ↑`

B3는 BTC가 유동성 stress를 확인하는 방향이다.

**B4 — Crypto-specific stress**

`BTC ↓ + equities stable + funding/OI stress + major crypto credit failure`

B4는 거시 위기와 분리해 크립토 내부 문제를 식별한다.

---

## 3. Gold × Bitcoin Cross-Signal

두 자산을 같이 보는 것이 핵심이다.

### 조합 A — Debasement / liquidity expansion

`Gold ↑ + BTC ↑ + USD ↓ + real yields ↓`

해석: 통화·재정 신뢰 및 유동성 확장에 대한 대안자산 수요 가능성.

**경보:** 낮음~중간. 금융위기보다 regime shift 후보.

### 조합 B — Geopolitical inflation shock

`Gold ↑ + Oil ↑ + BTC flat/↓ + real yields ↑`

해석: 전쟁·에너지 충격이 inflation/Fed channel로 연결되는 전형적인 조합.

**경보:** 높음.

### 조합 C — Broad liquidity / credit stress

`Gold ↓/flat + BTC ↓↓ + equities ↓ + credit spreads ↑ + USD ↑`

해석: 안전자산 선호 이전보다 **강제 현금화 및 dollar liquidity stress** 가능성을 우선 검토.

**경보:** 매우 높음.

### 조합 D — Risk-on / speculative melt-up

`Gold flat/↓ + BTC ↑↑ + equities ↑ + credit spreads stable`

해석: 금융 스트레스가 아니라 risk appetite 확대 가능성.

**경보:** 낮음. 다만 valuation / leverage 과열은 별도 감시.

### 조합 E — Divergence warning

`Gold ↑↑ + BTC ↓↓`

해석: 전통적 안전자산 수요는 증가하지만 고베타 유동성 자산에서는 위험회피가 발생하는 상태.

**경보:** 중간~높음. 다른 credit / rates 변수와 결합될 경우 escalation.

---

## 4. Stress Convergence에 추가하는 위치

기존 구조:

`Geopolitics → Energy → Inflation → Fed → Rates → Credit`

병렬 구조:

`AI CapEx → Financing → Private Credit → Credit Stress`

추가:

`Geopolitics / Fiscal → Gold`

`Liquidity / Rates / Risk Appetite → Bitcoin`

통합 모델:

```text
                         ┌→ Gold
Geopolitics → Energy → Inflation → Fed → Rates → Credit
        │                                  │
        └──────────────────────────────→ Real Yield / USD
                                           │
                                           └→ Bitcoin → Risk Appetite / Liquidity

AI CapEx → Financing → Private Credit → Credit Stress
```

Gold와 BTC는 **동일 가중치의 독립 위기축으로 추가하지 않는다.**

- Gold = macro/fiscal/geopolitical confirmation
- BTC = liquidity/risk-appetite confirmation

---

## 5. Preliminary score design

초기 설계에서는 각각 0~2점의 보조 점수로 시작한다.

### Gold score

- 0: 정상 / 혼조
- 1: 방향성 확인
- 2: 다른 macro 변수와 강한 동조

### BTC score

- 0: 정상 / 위험선호
- 1: 유동성 또는 risk-off 신호
- 2: equity/credit와 동시 stress

### Cross-signal bonus

Gold와 BTC 자체에는 큰 가중치를 주지 않고, **금리·신용·에너지 신호와의 동시성**에 가점을 둔다.

예:

`Stress Score = Core Macro Score + Credit Score + AI/Private Credit Score + Gold Confirm + BTC Confirm + Convergence Bonus`

정확한 가중치는 백테스트 전에는 고정하지 않는다.

---

## 6. Falsifiers

다음 결과가 반복되면 Gold/BTC를 조기경보 변수로 과대평가한 것으로 판정한다.

1. Gold/BTC 신호가 credit/rates stress보다 지속적으로 후행한다.
2. Gold/BTC trigger 추가 후 FP가 의미 있게 증가한다.
3. 추가 변수 없이도 동일한 KOSPI stress detection 성능이 나온다.
4. BTC 신호가 crypto-specific 이벤트에만 반응하고 macro stress와 재현성 있게 연결되지 않는다.
5. Gold signal이 real-yield/USD 통제로 설명되고도 독립적인 설명력을 갖지 못한다.

따라서 **가중치 확대는 백테스트 후에만 허용**한다.

---

## 7. Current snapshot — 2026-09-02

현재 시장은 미국-이란 충돌 재확대 → 유가 상승 → 인플레이션 우려 → 미 국채금리 급등 → Fed 인상 기대 상승이라는 핵심 스트레스 경로가 실제로 작동하고 있다. Reuters는 2026-09-02 아시아 증시 급락, Brent 약 $95, 미국 10Y 약 4.81%, KOSPI 약 -4%를 보도했다. Gold와 Bitcoin 역시 시장 스트레스 속에서 약세를 보였다. citeturn161051news34turn161051news35

이 조합은 현재 모델에서 다음처럼 분류한다.

| 변수 | 현재 해석 | 모델 역할 |
|---|---|---|
| Gold | 금리/달러 압력으로 약세 | Geopolitical/Inflation cross-check |
| Bitcoin | 고베타 risk/liquidity asset 약세 | Liquidity/financial-conditions check |
| Oil | 상승 | Inflation shock |
| 10Y Treasury | 급등 | Rates stress |
| Credit | 추가 확인 필요 | Systemic transmission |
| KOSPI | 급락 | Korea manifestation |

**현재 결론:** Gold와 BTC를 추가하면 Stress Convergence가 더 완전해지지만, 두 자산을 안전자산으로 취급해서는 안 된다. 특히 2026-09-02의 동반 약세는 `safe haven failure → liquidity/real-rate stress`를 구분하는 데 유용하다.

---

## 8. Next validation

다음 정량 검증에서 Gold/BTC를 기존 변수에 추가해 다음을 비교한다.

- Baseline: 기존 Stress Convergence v0.2
- Model G: + Gold
- Model B: + Bitcoin
- Model GB: + Gold + Bitcoin

평가 항목:

- TP / FP / TN / FN
- Lead time to KOSPI stress
- Precision / recall
- Warning persistence
- Trigger overlap / redundancy
- Incremental explanatory power

**승격 조건:** Gold 또는 BTC가 독립적인 예측력을 보이는 경우에만 Core Score 가중치를 상향한다.

---

## Sources

1. Reuters, 2026-09-02, Asian markets / U.S.-Iran / oil / yields / KOSPI:
   https://www.reuters.com/world/china/global-markets-wrapup-1-2026-09-02/
2. Reuters, 2026-09-02, Gold / rate-hike fears:
   https://www.reuters.com/world/india/gold-hits-over-3-week-low-mideast-tensions-fan-rate-hike-fears-2026-09-02/
3. Reuters, 2026-09-02, Dollar / oil / Fed expectations:
   https://www.reuters.com/world/china/dollar-holds-firm-two-week-high-amid-middle-east-hostilities-2026-09-02/
4. Yahoo Finance, 2026-09-01, Bitcoin intraday price:
   https://finance.yahoo.com/personal-finance/investing/article/bitcoin-and-ethereum-prices-today-tuesday-september-1-2026-crypto-prices-falling-as-inflation-concerns-persist-123554224.html
5. MarketWatch, 2026-09-01, August Bitcoin performance / debasement trade:
   https://www.marketwatch.com/livecoverage/stock-market-today-dow-jones-sp-500-nasdaq-s&p-500-nvidia-earnings/card/bitcoin-best-month-since-november-2024-comes-with-warning
6. Finance Research Letters, Volume 106, September 2026, Gold, Bitcoin, and equity market stress:
   https://www.sciencedirect.com/science/article/pii/S1544612326007221

## Status

- Integration design: **ADDED**
- Production weight: **NOT YET FIXED**
- Backtest requirement: **MANDATORY**
- Next action: run Baseline vs G vs B vs GB against the existing Korea-layer stress benchmark.
