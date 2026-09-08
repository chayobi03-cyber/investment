# Market Decision Framework Research — 2026-09-08

## 1. Research Objective

시장 상태를 정의하고 점수화한 뒤 종목별 의사결정과 포지션 사이징으로 연결하며, 그 판단법의 유효성을 검증하는 Market Decision Engine의 설계 원칙을 정립한다.

## 2. Core Architecture

권장 구조:

```text
RAW DATA
  ↓
Point-in-Time Control
  ↓
Market State Vector
  ├─ Trend
  ├─ Breadth
  ├─ Risk
  ├─ Macro/Liquidity
  └─ Cross-Asset Confirmation
  ↓
Regime Estimator (R1~R6 + probability)
  ↓
Horizon-specific Decision (Long / Mid / Short)
  ↓
Stock Score
  ↓
Opportunity + Risk
  ↓
Target Position
  ↓
Buy Intensity
```

핵심 원칙은 `시장수익률 예측기`보다 `시장상태 분류기 + 포지션 크기 조절기`로 설계하는 것이다.

## 3. Five Information Axes

### 3.1 Trend
- 단기/중기/장기 가격 추세
- 이동평균 정렬
- 고점 대비 낙폭
- 단일 기간의 임의 threshold보다 parameter sensitivity를 우선 검증

### 3.2 Breadth
- 상승 종목 비율
- 이동평균 위 종목 비율
- 신고가/신저가
- 업종 참여도

Breadth는 시장 내부 참여도와 상승의 질을 측정하는 확인 신호로 사용한다. 항상 독립적인 매매신호라고 가정하지 않는다.

### 3.3 Risk / Volatility
- VIX 및 한국 변동성
- 실현변동성
- 신용스프레드
- Drawdown / Tail Risk

동일한 위험정보를 중복 가점하지 않도록 축 내부에서 먼저 압축한다.

### 3.4 Rates / Liquidity / Credit
- 미국 2Y/10Y 및 term spread
- 실질금리/기대인플레이션
- 금융조건
- 신용스프레드
- 한국 금리 및 원화 금융환경

금리·유동성은 시장 방향의 결정자로 고정하지 않고 horizon-dependent한 환경 정보로 취급한다.

### 3.5 Cross-Asset
- 미국 주식/선물
- 금리
- 달러/엔화/원화
- 유가/금
- 반도체
- 한국 증시
- Crypto

개별 자산의 방향보다 자산 간 관계와 confirmation을 중시한다. 예: 달러 상승을 자동으로 Risk-Off로 분류하지 않는다.

## 4. Market Regime

R1~R6은 통계적으로 발견된 자연적 상태가 아니라 투자운영용 taxonomy로 정의한다.

- R1: 강한 Risk-On
- R2: 정상 Risk-On
- R3: 상승 후반/경계
- R4: 중립/전환
- R5: Risk-Off
- R6: Panic

최종 구현에서는 단일 label뿐 아니라 Regime Probability를 보존한다.

## 5. Scoring Principles

### 5.1 State Vector First

먼저 다음과 같은 상태 벡터를 저장한다.

```text
Trend       = 0~100
Breadth     = 0~100
Risk        = 0~100
Macro       = 0~100
CrossAsset  = 0~100
```

그 후 Market Score 또는 Regime을 산출한다. 25/20/20/20/15 같은 고정 가중치는 검증 전 가설로만 취급한다.

### 5.2 Market Score와 Risk Score 분리

예:

```text
Market Opportunity Score = 82
Risk Score               = 27
```

처럼 시장 기회와 위험을 별도 출력한다. 한 숫자로 모든 정보를 압축하지 않는다.

### 5.3 Horizon-specific Decision

장기/중기/단기는 단순히 동일 모델의 가중치만 바꾸는 방식보다 서로 다른 목적함수를 가진 decision layer로 설계한다.

초기 가설:

- 장기: 종목 중심, 시장 영향 낮음
- 중기: 종목과 시장의 균형
- 단기: 시장 risk/sentiment 영향 확대

기존 70/30, 60/40, 40/60 가중치는 검증 전 hypothesis로 유지하고 확정하지 않는다.

## 6. Stock Decision

`Stock Score × Market Modifier` 형태의 단순 곱셈은 사용하지 않는다.

권장 구조:

```text
Stock Quality / Opportunity
          ↓
Market Environment
          ↓
Risk Constraint
          ↓
Current Position
          ↓
Target Weight
          ↓
Trade Size / Buy Intensity
```

즉 좋은 종목이어도 위험환경과 현재 보유비중을 고려해 매수강도를 결정한다.

## 7. Validation Protocol

검증은 다음 순서를 기본으로 한다.

```text
1. Economic Rationale
2. Data Definition Freeze
3. Point-in-Time Dataset
4. Statistical Relationship
5. Historical Backtest
6. Purged / Embargo Validation when labels overlap
7. Walk-Forward OOS
8. Parameter Sensitivity
9. Transaction Cost / Slippage
10. Cross-Market Validation
11. Multiple Testing Control
12. PBO / DSR diagnostics
13. Falsification
14. Paper Trading
15. Live Monitoring
```

### 7.1 Benchmark

최소 benchmark:
- Buy & Hold
- 정기 적립식
- Cash / naive baseline
- 단순 이동평균 전략
- 기존 포트폴리오

### 7.2 Metrics

예측력:
- Rank IC / Spearman correlation
- horizon별 monotonicity

투자성과:
- CAGR
- Sharpe / Sortino
- Calmar
- MDD
- Recovery Time
- Turnover
- Transaction Cost / Slippage

안정성:
- 연도별
- Bull/Bear
- High/Low Volatility
- Crisis/Normal
- Cross-Market
- Parameter sensitivity

## 8. Overfitting / Data Snooping Controls

### Rule Freeze

OOS 결과를 확인한 뒤 룰을 수정하면 해당 OOS 데이터는 더 이상 독립적인 OOS가 아니다.

```text
Research
  ↓
Candidate
  ↓
Freeze
  ↓
Blind OOS
  ↓
Evaluation
  ↓
Promote / Reject
```

### Rule Registry

각 룰은 다음 메타데이터를 기록한다.

- Rule ID
- Hypothesis
- Feature Set
- Parameter Set
- Target Horizon
- Benchmark
- Development Period
- OOS Period
- Freeze Status
- Validation Results
- Falsification Conditions

### PBO / DSR / Reality Check

PBO와 DSR은 과적합과 선택편향을 진단하는 보조도구로 사용한다. 특정 값(예: DSR 0.95, PBO 0.10)을 보편적인 합격선으로 간주하지 않는다. White Reality Check / SPA 등 multiple-testing 방어도 후보 전략 수와 탐색 규모에 맞게 적용한다.

## 9. Falsification

모든 판단 룰에는 사전 반증 조건을 붙인다.

예:

```text
Hypothesis:
Market Score가 높을수록 이후 risk-adjusted return이 양호하다.

Falsification candidates:
- OOS 관계 소멸
- regime별 성과 차이 부재
- parameter 변화에 과민
- cross-market 재현 실패
- 비용 반영 후 edge 소멸
- MDD/tail risk가 기대와 반대
```

## 10. Governance Decision

이번 연구를 통해 다음을 투자 프로젝트의 Market Decision Engine 설계 원칙으로 채택한다.

1. 시장 상태와 시장 방향을 분리한다.
2. Trend/Breadth/Risk/Macro/Cross-Asset의 5개 정보축을 기본 골격으로 한다.
3. 상태 벡터를 먼저 저장하고 Regime을 산출한다.
4. Market Opportunity와 Risk를 분리한다.
5. R1~R6은 운영 taxonomy이며 검증 대상이다.
6. 장기/중기/단기 가중치는 가설로 시작하고 OOS 검증으로 확정한다.
7. Position sizing은 Stock Score와 Market State를 Risk Constraint와 함께 결합한다.
8. Point-in-Time, Rule Freeze, Purge/Embargo, Walk-Forward OOS를 검증 기본조건으로 한다.
9. Multiple Testing/PBO/DSR은 보조 검증으로 사용한다.
10. 각 룰에는 사전 반증 조건을 정의한다.

## 11. Research Lesson Learned

- 지표를 추가하는 것보다 중복정보를 제거하는 것이 중요하다.
- 점수의 숫자 자체보다 점수가 어떤 정보를 보존하는지가 중요하다.
- 검증 점수를 또 하나의 임의 점수로 만들기보다 Gate + Diagnostics 구조가 적절하다.
- OOS를 본 뒤 룰을 수정하면 OOS가 오염된다.
- 좋은 모델보다 틀렸을 때 빨리 폐기할 수 있는 모델이 중요하다.

## 12. Next Step

다음 단계는 실제 운용 가능한 `Market Decision Framework v1.0`으로 구체화한다.

1. 지표 후보와 데이터 출처 정의
2. Point-in-Time availability 기준 정의
3. 축별 중복 제거 및 대표 신호 선정
4. 0~100 정규화 규칙 설계
5. R1~R6 판정 후보식 정의
6. Regime probability 산출 후보 정의
7. 장기/중기/단기 decision layer 정의
8. 매수강도/리스크점수 연결 규칙 정의
9. 10~20년 검증 데이터셋 및 benchmark 설계
10. OOS/Walk-Forward/PBO/DSR 자동 검증 파이프라인 설계
