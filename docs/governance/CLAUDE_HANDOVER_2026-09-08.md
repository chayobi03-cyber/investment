# Investment Project — Claude Handover Package v2026-09-08

**Handover date:** 2026-09-08  
**Repository:** `chayobi03-cyber/investment`  
**Default branch:** `main`  
**Purpose:** Claude가 투자 프로젝트의 기존 맥락·규칙·검증상태를 재구성하지 않고 즉시 이어서 작업할 수 있도록 하는 단일 인수인계 문서.

> **중요:** 이 문서는 투자 권고문이 아니라 기존 연구 시스템의 운영/검증 컨텍스트다. 현재 시장가격·환율·금리 등 실시간 수치는 이 문서에서 가져오지 말고 반드시 최신 원자료로 새로 확인한다.

---

## 0. Claude 시작 지시문 — 가장 먼저 읽을 것

당신은 완전히 새로운 투자상담을 시작하는 것이 아니다. 이미 운영 중인 **자본보존 우선형(public-equity) 투자 연구 시스템**을 인수한다.

첫 목표는 새로운 전략을 제안하는 것이 아니라:

1. 기존 연구 계약과 의사결정 규칙을 보존하고,
2. 무엇이 검증되었고 무엇이 아직 작업 가설인지 구분하고,
3. 최신 시장정보를 별도로 갱신하고,
4. 미완료 검증 실험부터 이어가는 것이다.

### 필수 첫 읽기 순서

1. `README.md`
2. `docs/governance/INVESTMENT_RESEARCH_LOOP.md`
3. `docs/governance/PORTFOLIO_ALLOCATION_RULE_v0.1.md`
4. `docs/governance/LESSONS_LEARNED_2026-09-07_FX_ACCUMULATION.md`
5. `docs/governance/LESSONS_LEARNED_2026-09-08_MARKET_SESSION.md`
6. `docs/research/NARRATIVE_VALIDATION_WORKFLOW_v0.1.md`
7. 최신 `stress-convergence` 연구 파일
8. `docs/research/market/2026-09-03-jpy-stress-confirmation-framework.md`
9. `docs/research/anthropic/ANTHROPIC_IPO_FX_INDIRECT_EXECUTION_2026-09-06.md`
10. 이 문서의 마지막 `Current State` 및 `Immediate Open Work`

그 다음 최신 Git history를 확인하고 작업을 시작한다.

---

## 1. 프로젝트 목적

Repository README 기준 프로젝트는 **capital-preservation-oriented public-equity investment system**이다. 목표는 단순 최고수익률이 아니라 장기 생존성과 위험조정 복리수익이다.

현재 milestone gate:

- **M0:** Risk Contract
- **M1:** Data Integrity
- **M2:** Portfolio Risk Engine
- **M3:** Asset Allocation Backtest

상위 게이트가 GREEN이 아니면 다음 단계로 전략을 승격하지 않는다.

프로젝트가 만들려는 것은 시장을 매번 맞히는 예측기가 아니라 다음을 반복 가능한 체계로 만드는 것이다.

- 위험상태 변화 조기탐지
- 조기경보와 실제 손상 분리
- 감정적 일괄매수 대신 단계적 자본투입
- FX를 예측변수가 아니라 실행조건의 조정자로 사용
- 유동성과 선택권 보존
- 실패와 반례를 기록하여 규칙 개선

---

## 2. 연구 운영 규칙

모든 중요한 연구는 다음 순서를 따른다.

```text
가설
 ↓
최소 필요 데이터/원자료
 ↓
정량 기준(필요시)
 ↓
과거 구간 재현(backtest/replay)
 ↓
반증/반례 검증
 ↓
명시적 의사결정 또는 모니터링 규칙
 ↓
Lesson Learned
 ↓
Rule Change? YES / NO
 ↓
Git Commit? YES / NO
```

### 증거 규율

자료 우선순위:

1. 중앙은행·정부·통계기관·재무부·SEC·기업 공시 등 1차 자료
2. Reuters/Bloomberg/FT/WSJ 등 고품질 보도
3. 방법론이 명시된 기관/은행 리서치
4. 전문 경제·금융 매체
5. 일반 금융미디어
6. 개인 코멘터리/소셜 — 가설 생성용 저가중치

시장 narrative는 증명이 아니라 **검증할 가설**이다.

동일 원문을 재전파한 기사 여러 개를 독립 증거로 세지 않는다.

중요한 narrative는 항상:

- 직접 확인
- 작동 메커니즘 확인
- 반대 증거 확인
- 역사적 유사구간 확인
- 자료 독립성 확인
- 시간창 정렬
- 기계적/비재량 자금흐름 여부 확인
- cross-asset 수렴 여부 확인

을 거친다.

---

## 3. 포트폴리오 구조 — 현재 작업 기준

### Fixed Core

기존 governance baseline은 다음을 **고정·비매도 코어**로 정의한다.

- Samsung Electronics: **79 shares**
- 2026-09-07 working value: 약 **KRW 15.50M**
- 전체 포트폴리오 비중: 약 **14.6%**
- Active reallocation 대상에서 제외

### 계좌 수량 정합성 주의

최근 포트폴리오 대화에서는 별도 계좌에 **Samsung Electronics 79 shares가 추가로 존재**한다는 정보가 있었다.

따라서 다음 포트폴리오 재계산 시 반드시:

1. 계좌별 삼성전자 보유량을 재확인하고,
2. 어느 79주가 truly fixed/non-sellable core인지 구분하고,
3. 추가 79주가 active allocation 대상인지 확인한 뒤,
4. 전체 포트폴리오와 active sandbox의 분모를 다시 계산한다.

**기존 14.6%/15.50M 수치는 2026-09-07 작업용 스냅샷이며, 이를 그대로 실시간 전체비중으로 사용하지 않는다.**

### Active Allocation Sandbox

기존 baseline상 약 **KRW 90.41M**, 전체의 약 **85.4%**를 active allocation sandbox로 운용한다.

기능별 bucket:

1. **Dry Powder** — CD-rate ETF + cash + SGOV
2. **Hedge** — gold + JPY
3. **US Core/Growth** — S&P 500 + Nasdaq-100 + NVIDIA
4. **US Dividend** — US Dividend Dow Jones + SCHD
5. **Domestic Equity** — KODEX 200 + KODEX semiconductor 등
6. **Satellite/Risk** — India + Rigetti 등 소형 고위험 자산

### 2026-09-07 working snapshot

| Bucket | Active-sandbox weight | Approx. value |
|---|---:|---:|
| Dry Powder | 52.0% | KRW 47.01M |
| Gold | 11.4% | KRW 10.31M |
| US Core/Growth | 13.5% | KRW 12.21M |
| US Dividend | 11.5% | KRW 10.40M |
| Domestic ETF | 6.5% | KRW 5.88M |
| India | 2.3% | KRW 2.08M |
| High-risk satellite | 1.2% | KRW 1.08M |
| JPY | 0.9% | KRW 0.81M |
| Other | 0.7% | KRW 0.63M |

### 숫자 해석 주의

- Dry Powder only = 약 **52.0%**
- Dry Powder + Gold = 약 **63.4%** (JPY 제외)

앞으로 “방어적 자산 52%”처럼 쓰지 말고 분모와 bucket을 반드시 적는다.

---

## 4. 목표배분 baseline

### Balanced — Base Case

현재 working target:

- Dry Powder 42%
- Gold 10%
- US Core/Growth 22%
- US Dividend 11%
- Domestic ETF 7%
- India 2%
- High-risk satellite 3%
- JPY 1%
- Other 2%

2026-09-07 스냅샷 기준 해석:

- Dry Powder 약 **KRW 9.04M** 감소 여지
- US Core/Growth 약 **KRW 7.68M** 증가 여지
- 단, 하루에 정확한 목표비중으로 강제 rebalance하지 않는다.

### Staging baseline

계획된 이동자금에 대해:

- Stage 0: 0–20%
- Stage 1 correction: +20%
- Stage 2 correction: +25%
- Stage 3 correction: +25%
- Stress/Panic: final +30%

**정확한 시장 trigger는 아직 완전히 동결되지 않았다.**

의사결정 순서는:

```text
시장상태
 → 위험/조기경보 신호
 → 투입 가능한 자본 비율
 → 목표 bucket
 → 잔여 Dry Powder
 → 개별 종목
```

---

## 5. 집중도/중복 노출 규칙

### Korean semiconductor overlap

고정 삼성전자 코어가 이미 큰 비중을 가지므로 KODEX 200/KODEX semiconductor 등 한국 반도체 노출을 기계적으로 늘리지 않는다.

추가 매수는 별도 thesis + risk budget이 있어야 한다.

### NVIDIA overlap

NVIDIA는 S&P500/Nasdaq-100을 통해 간접 노출되어 있다.

직접 NVIDIA는 독립적인 core로 보지 않고 satellite 성격으로 취급한다.

**경제적 중복노출을 ticker 수만으로 판단하지 않는다.**

---

## 6. FX 규칙 — 현재 working version

핵심 lesson:

> **USD/KRW 하락(원화 강세)은 기존 해외자산 매도 신호가 아니다. 해외자산을 원화 기준으로 더 유리하게 취득할 수 있는 실행조건이다.**

단, FX 자체는 독립적인 매수 신호가 아니다.

개념식:

```text
Buy Intensity
= Portfolio Gap × Asset Opportunity × Risk Gate × FX Benefit
```

### 의사결정 순서

1. Portfolio Gap — 외화자산 bucket이 목표보다 부족한가?
2. Asset Opportunity — 가격이 축적하기 좋은 구간인가?
3. Trend/Risk — 위험을 늘려도 되는 상태인가?
4. FX Benefit — 환율이 KRW 취득가격을 개선하는가?
5. Cash Budget — 유동성/리스크 한도를 넘지 않는가?

### 임시 FX 관찰 band

| USD/KRW | 역할 |
|---:|---|
| 1,340–1,350 | 1차 축적 후보 |
| 1,320–1,330 | tranche 확대 검토 |
| 1,300–1,320 | 강한 축적 검토 |
| 1,280–1,300 | 극단적 원화 강세 — 시장위험 재검증 후 판단 |
| 1,380–1,420 | 신규 달러매수 규모 축소 |
| >1,450 | 신규 달러매수 엄격 제한 |

이 수치는 **예측구간이 아니라 working trigger 후보**이며 재검증 전에는 hard rule로 승격하지 않는다.

장기적으로는 절대수준뿐 아니라 rolling percentile, 변화율, 자산가격과의 joint behavior를 이용한다.

### 필수 FX 실험

공통 benchmark/공통 빈도/공통 현금예산으로:

- **A:** 고정 주기 분할투자
- **B:** 자산가격 trigger
- **C:** FX trigger
- **D:** `FX × asset price × portfolio gap`

비교 지표:

- 오탐(false positives)
- 미탐(false negatives)
- 조기 탐지 시간(lead time)
- 경보 발생 횟수(trigger frequency)
- 취득비용
- 누적수익률/CAGR
- 최대낙폭
- 현금 소진경로

목표는 최고수익률이 아니라 **수익·위험·경보안정성·유동성의 결합 우수성**이다.

---

## 7. JPY overlay

JPY/KRW는 **보조적인 stress confirmation indicator**다. 단독 위기판정 또는 매수/매도 trigger가 아니다.

기존 관찰 레벨:

- 850
- 875
- 900
- 925
- 950 (100 JPY/KRW)

시간창:

- 1일
- 7일
- 30일
- **90일 — primary operating horizon**
- 365일

현재 candidate 방향:

> **JPY/KRW + USD/JPY를 joint pair로 사용**하여 FX 자금 재배치/위험회피 여부를 점검하고 JPY 단독 신호는 사용하지 않는다.

### 2026-09-08 추가 lesson

- **USD/JPY 155 하회** 같은 엔화 급강세는 자금 재배치 또는 엔화 조달 포지션 축소 가능성을 점검하는 **보조 경보 후보**로만 둔다.
- 155는 현재 hard trading rule이 아니다.
- 별도 replay/backtest가 필요하다.
- 엔화 강세만으로 기존 해외자산을 매도하지 않는다.

검증 기준:

- 오탐 감소 여부
- 미탐 감소 여부
- 조기 탐지 개선 여부
- 경보 횟수 안정성
- 추가 정보가 정말 incremental한지
- BOJ-specific repricing을 일반적인 global stress와 혼동하지 않는지

---

## 8. Stress Convergence 연구 상태

세 상태를 반드시 분리한다.

- **Early Warning:** 거시 스트레스가 형성되는 단계
- **Tightening State:** 금리/정책 압력이 커진 단계
- **Crisis Confirmation:** 실제 시장/신용 손상이 나타나는 단계

2026-09-02 11-window replay의 working result:

| State | 결과 | 해석 |
|---|---|---|
| Early Warning | 0/4 crisis misses; 6/7 non-crisis false alarms | 빠르지만 noisy |
| Tightening State | 1/4 misses; 5/7 false alarms | 금리압력 설명에는 유용, 보편적 위기탐지에는 부족 |
| Crisis Confirmation | 3/4 misses before selected anchors; 1/6 evaluable non-crisis false alarm | 구체적이지만 늦고 드묾 |

결론:

**어느 한 상태도 아직 단일 최종 action rule로 승격하지 않는다.**

### 다음 핵심 실험

Early Warning 이후 Crisis Confirmation을 얼마 동안 같은 episode로 귀속할지 **attribution window를 먼저 동결**한 뒤 동일한 11개 window를 다시 실행한다.

주의:

- daily-panel replay는 완전한 real-time publication-vintage backtest가 아니다.
- 일부 과거구간 HY OAS 데이터가 불완전할 수 있다.
- 11개 window는 모집단 전체가 아니라 adversarial benchmark 성격이다.
- alert-start event는 window 내부 state 시작이며 전체 일별 alarm rate와 동일하지 않다.

---

## 9. 2026-09-08 시장점검 lesson

시장점검 전에 반드시 **거래일/휴장일/현재 시각**을 검증한다.

특히 미국 휴장일에는 존재하지 않는 정규장 결과를 해석하지 않는다.

미국 다음 세션 판단은 필요에 따라:

```text
마지막 정규장
+ 미국 선물
+ 금리
+ 유가
+ USD/JPY / USD/KRW
+ 글로벌 주식
+ 반도체
```

을 결합한다.

### 위험선호 해석 원칙

AI/반도체 강세 ≠ broad risk-on.

다음이 동시에 악화될 경우:

- 장기금리 상승
- 유가 상승 / 인플레이션 위험
- 엔화 강세

반도체 강세는 **상대강세(relative strength)**로 분리해서 기록한다.

### 매수강도

단일 지표로 정하지 않는다.

```text
매수강도
= 성장주/반도체 상대강도
+ 국채금리 방향
+ 유가/인플레이션 위험
+ USD/JPY 등 FX 자금흐름
+ 목표비중/집중도
```

원칙:

> 강한 자산을 추격하기보다, 조건이 개선될 때 분할매수 강도를 높인다.

이 내용은 `docs/governance/LESSONS_LEARNED_2026-09-08_MARKET_SESSION.md`로 기록되어 있다.

---

## 10. Narrative Validation

외부 narrative는 다음 세 층으로 분리한다.

1. **Narrative Strength** — 이야기가 얼마나 강하게 퍼지는가
2. **Evidence Strength** — 객관적 근거가 얼마나 강한가
3. **Crisis Confirmation** — 실제 손상/위기가 확인되었는가

세 항목을 하나의 risk label로 합치지 않는다.

자금흐름 통계를 투자심리로 해석하기 전에 기계적/비재량 흐름 여부를 확인한다.

설득력 높은 기사 하나가 systemic stress를 확인해 주는 것은 아니다.

---

## 11. Anthropic / AI IPO workstream

2026-09-06 기준 working classification:

- Narrative Strength: **HIGH**
- Evidence Strength: **MODERATE-HIGH**
- Crisis Confirmation: **NONE**

분리해서 보아야 할 thesis:

- Anthropic valuation
- AI capex
- public-company proxy earnings
- USD/KRW
- JPY/KRW risk regime

간접 proxy 보유를 Anthropic 직접 보유로 표현하지 않는다.

### 다음 decisive gate

첫 공개 **S-1/prospectus**가 나오면 추정치 중심 분석을 공시 기반으로 교체한다.

필수 항목:

- revenue
- gross margin
- operating loss
- cash flow
- capex/commitments
- customer concentration
- SBC
- share count/dilution
- use of proceeds
- strategic investor arrangements
- IPO price range

가치평가 sensitivity 후보:

`$1.0T / $1.25T / $1.5T / $1.75T / $2.0T`

forward revenue 및 gross-profit multiple을 중심으로 검증한다.

---

## 12. Current Repository State — 2026-09-08

Repository는 투자 연구를 위한 governance/research scaffold를 이미 갖추고 있다.

중요 문서:

- `README.md`
- `docs/governance/INVESTMENT_RESEARCH_LOOP.md`
- `docs/governance/PORTFOLIO_ALLOCATION_RULE_v0.1.md`
- `docs/governance/AUTO_COMMIT_POLICY_v0.1.md`
- `docs/governance/LESSONS_LEARNED_2026-09-07_FX_ACCUMULATION.md`
- `docs/governance/LESSONS_LEARNED_2026-09-08_MARKET_SESSION.md`
- `docs/research/NARRATIVE_VALIDATION_WORKFLOW_v0.1.md`
- `docs/research/market/2026-09-03-jpy-stress-confirmation-framework.md`
- `docs/research/market/ANTHROPIC_IPO_INDIRECT_INVESTMENT_RULES_v0.1.md`
- `research/stress-convergence-v0.2.2-B-vs-C-vs-D-backtest-2026-09-02.md`
- `research/stress-convergence-v0.2.2-D2-sensitivity-expanded-FP-2026-09-02.md`
- `research/stress-convergence-v0.2.2-candidate-C-bounded-persistence-backtest-2026-09-02.md`
- `research/scripts/run_v0.2.3_daily_panel.py`

최근 중요한 commit 흐름:

- `e6149d9` — refine FX accumulation rule v0.2
- `8e80ecf` — register FX accumulation lesson learned
- `b20ab13` — portfolio allocation baseline v0.1
- `dc6cdfc` — mechanical-flow attribution amendment
- `6c669e9` — Anthropic IPO FX execution record
- `8f6f236` — Anthropic IPO FX indirect framework
- `7a3fcfb` — JPY secondary stress-confirmation framework
- `f9fe7e8` — stress-convergence reproducibility layer / TTC validation
- `bea17d3` — 2026-09-08 market-session lessons and rules
- `adfb80c` — Claude investment project handover package
- `b348922` — automatic commit policy

**Repository의 문서량이 많다는 사실을 전략 완성으로 해석하지 않는다.** 최종 portfolio deployment engine은 아직 완전히 고정되지 않았다.

---

## 13. Immediate Open Work — 우선순위

### P0 — FX accumulation A/B/C/D replay

같은 benchmark, 같은 시간빈도, 같은 현금예산 가정으로 다시 실행한다.

필수 출력:

- 취득비용
- CAGR/누적수익
- 최대낙폭
- 현금잔액 경로
- 오탐
- 미탐
- 조기 탐지 시간
- 경보 발생 횟수
- threshold sensitivity

### P1 — Stress Convergence temporal attribution

Early Warning → Crisis Confirmation attribution window를 먼저 동결하고 기존 11개 window 그대로 재실행한다.

**attribution rule 변경과 historical window 변경을 동시에 하지 않는다.**

### P1 — JPY overlay replay

`JPY/KRW + USD/JPY`를 기존 benchmark에 추가하고:

- 오탐
- 미탐
- 조기 탐지 시간
- 경보 발생 횟수
- incremental information

을 평가한다.

특히 USD/JPY 155 하회는 candidate warning으로만 테스트한다.

### P1 — Walk-forward validation harness (implemented 2026-09-08)

`src/investment_pipeline/walkforward.py` now implements the point-in-time / walk-forward validation ("Experiment A: score monotonicity", Level 3-5) that the Market Decision Framework and Market Regime Engine specs required but had no code for. See `docs/investment/WALKFORWARD_VALIDATION_METHODOLOGY_V1.md`. It is validated on synthetic fixtures only (`tests/test_walkforward.py`); no real market/stock score has been run through it yet because `data/` does not exist in this repository. Before any `_score` column is connected to BuyStrength/Action, run `scripts/run_walkforward_validation.py` against the real `normalized_factors.csv` and require at least `NOT_FALSIFIED_CANDIDATE`, then continue with Levels 6-10 (parameter sensitivity, transaction costs, cross-market validation, multiple-testing correction, shadow operation).

### P2 — Portfolio deployment engine

다음 매핑을 명시적인 audit 가능한 규칙으로 만든다.

```text
Market State
→ Risk Signal
→ Deployable %
→ Target Bucket
→ Residual Dry Powder
```

### P2 — Anthropic filing gate

첫 S-1/prospectus 전에는 headline만으로 thesis를 상향조정하지 않는다.

### P2 — Portfolio account reconciliation

다음 재계산 전에 계좌별 실제 보유수량을 다시 받아 전체 포트폴리오 분모와 fixed/non-fixed Samsung exposure를 정합화한다.

---

## 14. Claude가 하지 말아야 할 것

- FX만으로 대규모 매수를 트리거하지 않는다.
- USD/KRW가 하락했다고 기존 해외자산을 자동 매도하지 않는다.
- JPY 강세만으로 금융위기를 선언하지 않는다.
- AI/반도체 강세만으로 broad risk-on을 선언하지 않는다.
- 백테스트가 좋다는 이유만으로 바로 실전배치하지 않는다.
- 역사적 성과에 맞추기 위해 threshold를 사후 최적화하지 않는다.
- narrative를 evidence로 취급하지 않는다.
- 동일 뉴스 원문을 여러 독립 증거처럼 세지 않는다.
- fixed core와 active allocation을 하나의 분모로 혼합하지 않는다.
- ticker 기준만으로 concentration risk를 계산하지 않는다.
- 현재 시장상황을 repository의 과거 snapshot으로 대신하지 않는다.
- 아직 검증되지 않은 working rule을 “확정 규칙”으로 표현하지 않는다.

---

## 15. 세션 시작시 표준 점검 순서

실전 시장점검이 필요한 세션은 다음 순서를 고정한다.

```text
① 현재 날짜/시간 + 미국 거래일/휴장 여부
② 마지막 정규장 상태
③ 미국 선물
④ 미국 국채금리
⑤ 유가
⑥ USD/KRW + USD/JPY
⑦ 글로벌 주식/반도체 상대강도
⑧ 현재 포트폴리오 목표비중/실제비중
⑨ 매수 가능 현금
⑩ 자산별 매수강도
⑪ 규칙 위반 여부
⑫ 오늘 새로 검증할 가설
```

마지막에 반드시:

- 관찰
- 증거
- 해석
- 결정
- 다음 검증

을 분리해 기록한다.

---

## 16. 세션 종료 규칙

모든 세션 종료 시 다음을 검토한다.

```text
Lesson Learned: <무엇을 배웠는가>
Rule Change: YES / NO — <이유>
Git Commit: YES / NO — <대상>
```

### Git 저장 판단

다음이면 원칙적으로 commit:

- 새로운 rule
- 기존 rule 수정
- 중요한 falsification 결과
- benchmark/방법론 변경
- 포트폴리오 구조 baseline 변경
- 중요한 market-session lesson
- Claude handover/context 변경

단순 검색결과 나열이나 일회성 숫자는 별도 commit 필요성이 낮다.

현재 repository에 자동 commit 정책이 있으므로, material change가 생겼는데 Git 기록이 없다면 세션 종료 전에 정합성을 확인한다.

---

## 17. Claude가 다음 세션에서 출력해야 할 기본 형식

실전 작업을 시작할 때 다음 구조를 사용한다.

### A. Current State
- 무엇이 고정 규칙인가?
- 무엇이 working hypothesis인가?
- 직전 검증 결과는 무엇인가?

### B. Fresh Market Evidence
- 오늘 새로 확인한 1차/고품질 자료
- 날짜/시각
- 핵심 수치
- 서로 충돌하는 증거

### C. Decision Impact
- 포트폴리오 gap
- risk gate
- FX benefit
- 매수강도
- 예상 현금소진

### D. Falsification / Caveat
- 무엇이 이 판단을 틀렸다고 입증할 수 있는가?
- 데이터 한계는 무엇인가?

### E. Action
- BUY / HOLD / REDUCE / WATCH
- tranche
- 대상 bucket
- rule reference

### F. Session Close
- Lesson Learned
- Rule Change
- Git Commit

---

## 18. One-paragraph startup prompt for Claude

다음 문단을 그대로 Claude 세션 첫 메시지로 사용할 수 있다.

> You are taking over the existing `chayobi03-cyber/investment` project. Read `README.md`, `docs/governance/INVESTMENT_RESEARCH_LOOP.md`, `docs/governance/PORTFOLIO_ALLOCATION_RULE_v0.1.md`, the latest lessons-learned files, and this handover before acting. Preserve the existing capital-preservation-first, falsification-driven research contract. Separate fixed holdings from the active allocation denominator. Treat FX as an execution modifier, not a standalone signal. Keep Early Warning, Tightening, and Crisis Confirmation separate. Do not infer current market conditions from repository snapshots; refresh current facts from primary/high-quality sources and verify the US trading calendar/time first. The immediate research priorities are FX A/B/C/D replay, stress-convergence temporal attribution, JPY/US-dollar-yen overlay validation, and explicit portfolio deployment rules. Do not promote working hypotheses to hard rules without replay/falsification. At session close, record Lesson Learned, Rule Change, and Git Commit status, and commit material methodological or governance changes.

---

## 19. Handover completeness check

인수받은 Claude가 아래에 모두 답할 수 있으면 인수인계가 정상적으로 된 것으로 본다.

- 프로젝트의 최우선 목표는 무엇인가?
- fixed core와 active sandbox의 차이는 무엇인가?
- 현재 Balanced target은 무엇인가?
- Dry Powder 52%와 Dry Powder+Gold 63.4%의 차이는 무엇인가?
- FX 하락을 왜 매도신호로 사용하지 않는가?
- JPY 155 신호의 현재 지위는 무엇인가?
- Early Warning과 Crisis Confirmation을 왜 분리하는가?
- 지금 가장 우선해야 할 검증은 무엇인가?
- 현재 portfolio 숫자 중 어떤 것은 live가 아니라 working snapshot인가?
- 세션 종료 시 무엇을 기록하고 언제 Git에 저장하는가?

---

**Document status:** ACTIVE HANDOVER  
**Authority:** Existing repository governance + latest lessons learned through 2026-09-08  
**Next expected update:** After the next material validation result or portfolio-account reconciliation

**2026-09-08 addendum:** Added the walk-forward/point-in-time validation harness (`src/investment_pipeline/walkforward.py`, `docs/investment/WALKFORWARD_VALIDATION_METHODOLOGY_V1.md`, `docs/governance/LESSONS_LEARNED_2026-09-08_WALKFORWARD_VALIDATION.md`). It is tooling only, validated on synthetic fixtures — it does not itself constitute a validated score, and the KRX/OpenDART data connection (P2 in this section) is still the blocking gate before it can be run on real data.
