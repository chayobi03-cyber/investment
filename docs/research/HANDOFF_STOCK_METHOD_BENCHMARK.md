# HANDOFF — 주식투자 방법론 벤치마크 후속 작업

- 작성일: 2026-10-16
- 프로젝트: 투자 / investment
- 상태: RESEARCH ONLY / M1 BLOCKED / 매수·실행 불허
- 기준 저장소: https://github.com/chayobi03-cyber/investment
- 기준 브랜치: main
- 기존 방법론 근거: [INVESTMENT_METHOD_BENCHMARK_2026-10-16.md](INVESTMENT_METHOD_BENCHMARK_2026-10-16.md)
- 기준 엔진 커밋: 2394db0bbc21b6ab36f4840b78dc227e4a84445c
- 현행 문서 HEAD(세션 종료 시 확인 필요): main

## 1. 이번 세션에서 완료한 일

1. GitHub Issue #27을 다시 확인했다. 상태는 OPEN.
2. M1 Data Integrity 관련 구현, 구성, 테스트, CI 워크플로를 원격으로 검사했다.
3. 기존 코드 기준선 EXPERIMENT_B0_ENGINE_2026-10-16을 원본 커밋 2394db0bbc21b6ab36f4840b78dc227e4a84445c로 고정하고 구현/구성/테스트 주요 blob SHA를 매니페스트에 기록했다.
4. M1 회귀 테스트 조건과 주식투자 방법론별 사전등록 test contract를 문서화했다.
5. Lesson Learned를 기록했다.
6. 기존 실행 규칙/임계값/가중치는 변경하지 않았다.

## 2. 필수 산출물

- [B0 기준선 동결 매니페스트](B0_BASELINE_FREEZE_2026-10-16.md)
- [주식 방법론별 Test Contracts v1](STOCK_METHOD_TEST_CONTRACTS_V1_2026-10-16.md)
- [Lesson Learned — B0 / M1 / 주식 방법론](../governance/LESSONS_LEARNED_2026-10-16_B0_M1_STOCK_METHODS.md)
- [방법론 근거 및 우선순위 벤치마크](INVESTMENT_METHOD_BENCHMARK_2026-10-16.md)

Baseline manifest는 B0가 재현성 기준선으로 동결되었음을 의미할 뿐, 데이터 품질·성능·매수 적격성이 승인됐다는 뜻이 아니다.

## 3. Issue #27 및 M1 조사 결과

Issue #27: https://github.com/chayobi03-cyber/investment/issues/27

확인된 결함:
- scripts/market_monitor/poll.py는 range=1d, interval=5m 결과 중 마지막 두 유효 종가로 change_pct를 계산한다. 이는 마지막 5분 봉 변화이며, 이름/구성의 15분 또는 일간 수익률을 보장하지 않는다.
- build_state()는 모든 성공 심볼 중 가장 최신 timestamp로 전체 freshness를 계산한다. 최신 USD/JPY quote가 오래된 KOSPI/KOSDAQ/한국 리더 데이터를 가릴 수 있다.
- config/market_monitor.json의 material_abs_pct_15m 임계값이 실제 측정 구간과 일치하는지 보장되지 않는다.
- 기존 tests/test_market_monitor.py는 상태 임계값, alert/delta, breadth, 실패 VIX 처리, state schema 등을 확인하지만 5m/15m/daily horizon parity 및 심볼별 freshness의 핵심 회귀 케이스를 직접 입증하지 않는다.
- tests/test_data_pipeline.py와 tests/r01/*은 completeness/PIT/provenance 게이트를 검사하지만 시장 모니터의 return horizon/freshness 문제를 대체하지 않는다.
- .github/workflows/collectors-ci.yml은 market monitor 관련 파일 변경 시 해당 테스트를 실행하도록 구성돼 있다.

검증 한계:
- GitHub commit status는 pending / check contexts 0으로 조회되었다.
- 연결된 workflow-run 조회에서 점검 커밋 실행 기록을 얻지 못했다.
- 로컬 clone/test는 실행 환경의 github.com DNS 해석 실패로 실행하지 못했다.
- 따라서 테스트 상태는 NOT VERIFIED이며 PASS가 아니다.

## 4. 동결 기준선과 명명 규칙

- EXPERIMENT_B0_ENGINE_2026-10-16: 기존 엔진 비교 기준선, source commit 2394db0bbc21b6ab36f4840b78dc227e4a84445c.
- BUY_TRIGGER_B0_NO_BUY: 기존 Buy Trigger Engine의 No Buy 권한 상태.
- 둘은 다른 개념이다. 실험 baseline 이름이 기존 매수 차단 상태를 변경하거나 우회하지 않는다.

동결 매니페스트에 코드·설정·테스트·CI 파일의 blob SHA가 있다. 향후 구현 변경은 별도 변경 커밋에서 만들고 기존 B0 기준선과 비교한다. 기준선을 조용히 덮어쓰지 않는다.

## 5. 절대 유지할 제약

- BUY_ALLOWED=false
- EXECUTION_ALLOWED=false
- PROMOTION=DISABLED
- M0 Risk Contract → M1 Data Integrity → M2 Portfolio Risk Engine → M3 Asset Allocation Backtest 순서를 보존한다.
- DATA_NOT_READY/BLOCKED는 fail-closed.
- M1 통과 전에 성능 백테스트를 매수 권한 근거로 사용하지 않는다.
- LOCKED 보유분은 위험 계산에 포함하지만 자동 매도 대상으로 처리하지 않는다.
- 계좌 총액과 개별 보유분의 중복 합산을 금지하고 ETF look-through는 별도 노출로 반영한다.
- 팩터·임계값을 OOS 결과 확인 뒤 선택하지 않는다.
- CAGR는 보조 지표다. MDD, tail loss, stress loss, recovery duration 및 생존성 제약이 우선이다.

## 6. M1 다음 작업 — 구현/CI

아래 회귀 테스트를 코드와 CI에 연결하고 증거를 보관한다.

1. 5분, 검증된 15분, 이전 정규 세션 종가 대비 일간 수익률을 별도 필드로 산출한다.
2. 15분 구간의 간격/누락/중복/역순 timestamp를 검증한다. 잘못된 바를 인접 5분 변화율로 대체하지 않는다.
3. prior regular-session close, endpoint timestamp, price basis를 보존한다.
4. freshness를 심볼별·필수 그룹별로 계산하고 session-aware 정책을 적용한다. 가장 신선한 무관 심볼로 전체 GREEN을 만들지 않는다.
5. quote conflict, stale/missing critical symbol, market holiday/session/timezone, corporate action 테스트를 추가한다.
6. DATA_NOT_READY/BLOCKED가 BUY_TRIGGER를 승격하지 못하고 BUY_ALLOWED/EXECUTION_ALLOWED가 계속 false인지 확인한다.
7. collectors-ci 경로에서 회귀 테스트를 실행하고, 음성 fixture와 전체 테스트 결과를 artifact로 저장한다.

모든 필수 M1 회귀 테스트와 출처/시간 검증 증거가 확보되기 전까지 M1은 GREEN으로 간주하지 않는다.

## 7. 방법론 실험 순서

M1 GREEN 이후에만 유효한 데이터 구간에서 empirical backtest를 시작한다.

1. EXPERIMENT_B0_ENGINE parity 재현.
2. B1: KOSPI/KOSPI 200 buy-and-hold 대조군.
3. B2: 고정 DCA 및 현금 기회비용 대조군.
4. B3/B3-M: 일간 200일 SMA와 월간 10개월 SMA를 별도 테스트.
5. C1: Cross-sectional momentum / relative strength.
6. C2: Quality / profitability.
7. C3: Value / valuation discipline.
8. C4: Low-risk / volatility-aware sizing.
9. C5: Time-series trend / exposure filter.
10. C6: Breakout / volume / entry setup.
11. C7: Lump sum vs fixed DCA vs risk-gated staging.
12. C8: 개별 테스트를 통과한 신호만 사용한 multifactor 조합.

각 실험은 universe/survivorship, PIT, 수식/lookback, rebalance, 실행가/비용, corporate actions, walk-forward OOS, purge/embargo, 사전등록 1차 지표, 최소 효과, 민감도/다중검정, 반증 조건을 명시한다. 상세 기준은 Test Contracts v1을 기준으로 한다.

## 8. 승격 게이트

- G0 Evidence-ready: source/provenance/PIT/기업행동/세션/비용 검증.
- G1 Baseline parity: B0와 대조군 재현.
- G2 Incremental value: 사전등록 지표의 증분 효과 및 tail-risk 제약.
- G3 Robustness: walk-forward OOS, regime/sector 분해, 비용/파라미터 민감도, falsification.
- G4 Paper/shadow: 신호/기록 정합성.
- G5 독립 검토 및 명시적 promotion 승인.

어떤 게이트도 BUY_ALLOWED 또는 EXECUTION_ALLOWED를 자동으로 true로 만들지 않는다.

## 9. Lesson Learned 및 룰 변경 판단

- Lesson Learned 파일과 baseline/test contract를 Git에 보관한다.
- 원인: 전략보다 상위인 데이터 유효성에서 수익률 기간과 freshness 집계 단위가 어긋나면 위험 상태를 반대로 표시할 수 있다.
- 개선 규칙: 수익률 필드 이름·threshold·실제 endpoint가 동일한 horizon을 나타내야 하고, freshness는 각 필수 관측치와 그룹에서 따로 판정한다.
- 식별자 규칙: 연구 기준선은 EXPERIMENT_B0_ENGINE, 매수 차단 상태는 BUY_TRIGGER_B0_NO_BUY로 구분한다.
- 이번 세션에서는 live rule, threshold, weight를 변경하지 않았다. M1 교정 후 별도 변경으로 테스트·리뷰한다.
- Git 저장은 필요하다. 아래 체크리스트는 해당 문서화 작업을 완료한 상태로 기록한다.

## 10. 다음 세션 시작 프롬프트

> investment 저장소의 HANDOFF_STOCK_METHOD_BENCHMARK.md, B0_BASELINE_FREEZE_2026-10-16.md, STOCK_METHOD_TEST_CONTRACTS_V1_2026-10-16.md를 읽고 이어서 진행하자. Issue #27은 OPEN이고 M1은 아직 GREEN이 아니다. scripts/market_monitor/poll.py에서 5m/15m/daily return horizon을 분리하고 symbol/group/session-aware freshness를 구현하라. quote conflict, missing/stale bars, holiday/timezone, corporate action 및 fail-closed decision gate 회귀 테스트를 추가하고 collectors-ci에 연결하라. 기존 EXPERIMENT_B0_ENGINE 기준선과 M0–M3 게이트를 보존하고 BUY_ALLOWED=false, EXECUTION_ALLOWED=false, PROMOTION=DISABLED를 유지하라. CI의 실제 결과와 artifact를 확인하기 전에는 테스트 PASS를 주장하거나 전략 성능 백테스트를 매수 권한 근거로 쓰지 말라. 마지막에 Lesson Learned, 규칙 변경 필요성, Git 커밋 여부를 검토하라.

## 11. 세션 종료 체크리스트

- [x] Issue #27 상태 및 관련 코드·테스트·CI 경로 확인
- [x] 기존 B0 source commit/파일 SHA 동결
- [x] 방법론별 test contract 및 사전등록 기준 작성
- [x] Lesson Learned 기록
- [x] Git 저장 필요성 검토 및 문서 커밋
- [ ] Issue #27 코드 수정 및 회귀 테스트 실행 (다음 작업)
- [ ] GitHub Actions artifact 기반 M1 승인 (다음 작업)
- [x] BUY_ALLOWED=false / EXECUTION_ALLOWED=false 유지
