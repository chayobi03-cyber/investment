# HANDOFF — 주식투자 방법론 벤치마크 후속 작업

- 작성일: 2026-10-16
- 프로젝트: 투자 / investment
- 상태: RESEARCH ONLY
- 기준 저장소: https://github.com/chayobi03-cyber/investment
- 기준 브랜치: main (기본 브랜치 기준)
- 기준 문서: [INVESTMENT_METHOD_BENCHMARK_2026-10-16.md](docs/research/INVESTMENT_METHOD_BENCHMARK_2026-10-16.md)
- 기준 커밋: 2394db0bbc21b6ab36f4840b78dc227e4a84445c

## 1. 다음 세션 목표

기존 투자 엔진을 보존하면서, 신규 주식투자 방법론이 기존 규칙 대비 실제로 유의미한 증분 효과를 내는지 검증할 실험 계약(test contract)을 작성한다. 구현이나 매매 적용보다 먼저 데이터 무결성 게이트 및 비교 기준선을 확인한다.

## 2. 현재 상태 / 고정 제약

- 투자 원칙: 자본 보존, MDD·tail loss·회복기간·생존성 우선. CAGR 단독 최적화 금지.
- Decision plane은 개발/연구 에이전트와 분리한다.
- BUY_ALLOWED=false, EXECUTION_ALLOWED=false를 유지한다.
- 데이터 상태가 DATA_NOT_READY 또는 BLOCKED이면 fail-closed.
- 규칙/임계값은 실험 전에 동결한다. OOS 결과를 본 뒤 수정하면 해당 구간은 독립 OOS로 간주하지 않는다.
- 신규 팩터는 기존 점수에 무조건 더하지 않고, 각각 독립 신호로 시험한다.
- 종목 기회, 시장 허가, 진입 셋업, 포지션 사이징, 자금투입 정책을 분리한다.
- LOCKED 보유분은 위험 계산에는 포함하되 자동 매도 대상으로 처리하지 않는다.
- 계좌 총액과 개별 보유분을 중복 합산하지 않는다. ETF look-through 노출을 별도 반영한다.

## 3. 선행 차단 항목

GitHub Issue #27 — https://github.com/chayobi03-cyber/investment/issues/27

기록된 문제:
- 5분 막대의 변화율을 15분/일간 변화율로 오인할 수 있음.
- 모든 심볼 중 최신 timestamp 하나만 사용해, 오래된 한국 지수 데이터가 최신인 타 자산 데이터에 의해 가려질 수 있음.
- 이런 경우 DATA_QUALITY=GREEN이 잘못 설정될 위험이 있음.

다음 세션에서 할 일:
1. Issue #27의 현재 상태와 관련 코드/테스트를 다시 확인한다.
2. 심볼별·필드별 timestamp/freshness를 검증한다.
3. 5m/15m/intraday/close-to-close 수익률 정의를 분리한다.
4. quote conflict, stale data, missing bars, market session, timezone, corporate action 테스트를 확인한다.
5. 회귀 테스트가 통과하고 M1 데이터 무결성이 승인되기 전까지 이 신호를 매수 허가에 연결하지 않는다.

## 4. 벤치마크 후보와 순서

우선순위는 아래와 같다. 한 번에 여러 요소를 추가하지 말고 각 후보의 증분 효과부터 시험한다.

1. Cross-sectional momentum / relative strength: 20/60/120 거래일 및 중기 모멘텀, 시장/섹터 대비 RS.
2. Quality / profitability: 현금흐름, 수익성, 레버리지, 일회성 이익, 재무 건전성.
3. Value / valuation discipline: 이익·현금흐름 대비 가격, 업종별 비교, value trap 통제.
4. Low-risk / volatility-aware sizing: 하방 변동성, 상관, 유동성, 공통 테마·ETF look-through.
5. Time-series trend filter: 200일 SMA와 월간 10개월 SMA를 비교군으로 평가.
6. Breakout / volume setup: 기존 D/W/M 및 RS 대비 진입 실패율·추격매수·MAE/MFE 개선 여부.
7. Capital deployment: lump sum vs fixed DCA vs risk-gated staged deployment.

## 5. 다음 세션의 구체적인 작업 순서

### Step A — 저장소 기준선 확인
- 기준 커밋과 문서가 존재하는지 확인.
- 기존 Market Regime Engine, Buy Trigger Engine, Portfolio Factor Exposure 규칙을 읽는다.
- 현행 엔진 B0의 코드·설정 버전, 데이터 컷오프, 산출물을 고정한다.

### Step B — Issue #27 / M1 게이트 검증
- 이슈 상태와 관련 구현/CI 테스트를 확인한다.
- 데이터 무결성 문제를 해결하기 전 성능 백테스트를 실행해 결론을 내리지 않는다.
- 수정이 필요하면 작은 변경 단위로 수정하고 회귀 테스트를 추가한다.

### Step C — Test Contract 작성
실험마다 다음 항목을 고정한다.
- hypothesis / mechanism
- universe / survivorship handling
- PIT availability timestamp and lag
- signal formula, lookback, rebalance frequency
- entry/exit and executable price assumptions
- corporate actions
- fees, taxes, spread, slippage, liquidity limits
- benchmark and frozen B0 version
- train / validation / walk-forward OOS windows
- overlapping-label purge/embargo when needed
- primary metrics and pre-registered pass/fail thresholds
- sensitivity grid and number of trials
- falsification conditions
- artifact path and run identifier

### Step D — 실험 순서
1. B0: frozen current engine.
2. B1: KOSPI/KOSPI 200 buy-and-hold plus current portfolio baseline.
3. B2: fixed DCA baseline.
4. B3: 200-day / 10-month trend filter.
5. C1: B0 + quality/profitability.
6. C2: B0 + value discipline.
7. C3: B0 + cross-sectional momentum/RS.
8. C4: B0 + low-risk sizing.
9. C5: 통과한 단일 신호만 결합한 multifactor.
10. C6: breakout/volume entry setup.
11. C7: risk-gated staged deployment.

### Step E — 평가 지표
필수:
- capital survival: MDD, 95% CVaR/Expected Shortfall, stress loss, worst forward return
- recovery: recovery duration, time underwater
- signal: horizon별 forward return, Rank IC/monotonicity, FP/FN, lead time
- entry: MAE/MFE, breakout failure, chase-entry frequency
- implementation: turnover, fees/taxes/slippage-adjusted results, liquidity capacity
- robustness: walk-forward OOS, year/regime/sector split, parameter sensitivity
- deployment: cash opportunity cost, loss probability/depth/duration

CAGR는 보조 지표로 보고한다. 데이터 무결성 실패나 생존 제약 악화가 있으면 높은 CAGR로 상쇄하지 않는다.

## 6. 승격 게이트

- G0 Evidence-ready: PIT, 데이터 계약, 기업행동, 시점, 비용/체결 가정 검증.
- G1 Baseline parity: B0와 단순 대조군 재현.
- G2 Incremental value: 사전 정의된 지표에서 증분 개선, tail risk/MDD의 부당한 악화 없음.
- G3 Robustness: walk-forward OOS, 국면별 결과, 비용·파라미터 민감도 및 반증 통과.
- G4 Paper/shadow: 실시간 신호와 기록 정확성 검증.
- G5 Promotion review: 독립 검토 후 별도 승인.

어떤 게이트도 BUY_ALLOWED 또는 EXECUTION_ALLOWED를 자동으로 true로 만들지 않는다. 승격은 별도 검토와 승인이 필요하다.

## 7. Lessons learned / 운영 규칙

- 전략을 많이 붙이는 것보다 기존 엔진 대비 검증 가능한 증분 가설이 우선이다.
- 동일 정보를 여러 신호가 중복 반영하지 않도록 opportunity, permission, entry, sizing, deployment를 분리한다.
- 한국 주식 팩터 연구는 현지 검증 가설의 근거이지 미래 수익 보장이 아니다.
- DCA는 초과수익 보장 전략이 아니라 자금투입 정책의 대조군이다.
- 데이터 품질 실패는 전략 성능보다 우선하는 차단 조건이다.
- 결과를 본 뒤 파라미터를 수정하면 그 OOS 기간은 더 이상 독립 검증 구간이 아니다.
- 현재 문서는 연구 프레임워크만 등록하며 live rule/threshold를 변경하지 않는다.

## 8. 다음 세션 시작 프롬프트

아래 내용을 다음 세션 첫 메시지로 사용한다.

> investment 저장소의 docs/research/HANDOFF_STOCK_METHOD_BENCHMARK.md와 docs/research/INVESTMENT_METHOD_BENCHMARK_2026-10-16.md를 읽고 이어서 진행하자. 먼저 GitHub Issue #27의 현재 상태와 M1 Data Integrity 관련 코드·CI 테스트를 확인하라. 기존 B0 및 M0–M3 게이트를 보존하고 BUY_ALLOWED=false, EXECUTION_ALLOWED=false를 유지하라. 데이터 무결성이 검증되기 전에는 신규 전략 백테스트 결과를 매수 권한 근거로 사용하지 말라. 그 다음 단일 신호별 test contract와 사전등록 합격/반증 기준을 작성하라. 변경이 필요하면 작은 단위로 구현·테스트하고, 유의미한 산출물은 Git에 커밋하라. 마지막에 Lesson Learned, 규칙 변경 필요성, 후속 작업을 기록하라.

## 9. 참고 링크

- Benchmark: https://github.com/chayobi03-cyber/investment/blob/main/docs/research/INVESTMENT_METHOD_BENCHMARK_2026-10-16.md
- Issue #27: https://github.com/chayobi03-cyber/investment/issues/27
- Repository: https://github.com/chayobi03-cyber/investment

## 10. 세션 종료 체크리스트

- [ ] 실제 수행한 작업과 확인하지 못한 항목을 구분해 기록
- [ ] 테스트 결과와 실행 ID / artifact 경로 기록
- [ ] Lesson Learned 작성
- [ ] 기존 룰 수정 여부와 근거 기록
- [ ] Git 커밋 필요 여부 검토 및 필요한 변경 커밋
- [ ] 다음 세션 시작 프롬프트 갱신
- [ ] BUY_ALLOWED=false / EXECUTION_ALLOWED=false 유지 여부 확인
