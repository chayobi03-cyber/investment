# HANDOFF — 하락장 단기매매 전략 스킬화 평가

- 작성일: 2026-10-16 (KST)
- 프로젝트: 투자 / investment
- 기준 저장소: https://github.com/chayobi03-cyber/investment
- 기준 브랜치: main
- 상태: ASSESSMENT_COMPLETE / IMPLEMENTATION_DEFERRED / RESEARCH_ONLY
- 다음 작업 우선순위: M1 Data Integrity 선행 차단 해소 → 전략 연구 계약 → Skill 런타임 확인 및 프로토타입
- 안전 제약: `BUY_ALLOWED=false`, `EXECUTION_ALLOWED=false`, `PROMOTION=DISABLED`

## 1. 이번 작업의 목적

장기 투자 적격성이 있는 주식을 하락 국면에서 관찰하고, 검증된 단기 반등 기회를 활용하는 전략을 AI Skill로 구현할 가치가 있는지 평가했다.

요청의 목적은 단순한 `SKILL.md` 생성이 아니라 다음 여섯 대안을 비교해 최소 복잡도의 재사용 가능한 구조를 결정하는 것이었다.

1. 일반 메타 프롬프트 유지
2. 단일 Skill
3. 다수의 하위 Skill
4. Skill + 데이터 파이프라인 + 결정론적 검증 엔진
5. 기존 투자 시스템에 기능 통합
6. 위 방식을 조합한 하이브리드 구조

## 2. 최종 판단

**권장 목표는 얇은 상위 Skill + 기존 결정론적 투자 엔진 + 기존 기록/검증 체계의 하이브리드 구조다.**

단, 현재 단계에서는 평가 문서까지만 저장하고 Skill의 실제 구현/배포는 보류한다. 다음 이유 때문이다.

- 저장소에는 이미 결정론적 Decision Gate, 멀티자산 오케스트레이터, PIT/data-quality 및 evidence 검증 모듈, 과거 기록 기반이 있다.
- 각 기존 모듈을 별도의 AI Skill로 다시 만드는 것은 중복 구현, 상태 충돌, 버전 관리 및 호출 오버헤드를 유발할 수 있다.
- 저장소의 현재 루트/구성 탐색에서 독립 Skill 로더 또는 실제 Skill 배포 규약을 확인하지 못했다. 파일을 추가하는 것만으로 실행 가능한 Skill이 된다고 가정하지 않는다.
- 단기매매 전략의 경제적 유효성은 별도로 검증되어야 하며 Skill의 출력 일관성과 혼동해서는 안 된다.
- Market monitor의 M1 무결성 차단이 해결되고 회귀 테스트/CI 증거가 확인되기 전에는 해당 모니터를 매수 타이밍 근거로 사용하지 않는다.

### 적용 원칙

- 최초 구현은 상위 Skill 하나로 제한한다.
- Skill은 호출 조건, 분석 절차, 필수 입력, 증거 보고 및 출력 계약을 표준화한다.
- 가격·손익·포지션 계산, PIT/freshness 검증, 데이터 품질, 위험 한도, 상태 전이 및 매매 권한은 코드/기존 게이트가 책임진다.
- 하위 Skill 분리는 독립적인 호출자, 명확한 계약, 별도 테스트/버전 관리 및 실질적인 재사용 이점이 입증될 때만 고려한다.
- 기존 B0 기준선을 덮어쓰거나 기존 임계값·권한 상태를 변경하지 않는다.

## 3. 이번 세션에서 확인한 저장소 구성

| 구성 | 경로 | 활용 판단 |
|---|---|---|
| 최종 결정 게이트 | `src/investment_pipeline/decision_gate.py` | 기존 매매 권한/상태 통제를 재사용한다. |
| 멀티자산 오케스트레이터 | `src/investment_pipeline/multi_asset_subagents.py` | Data/PIT, regime, risk, evidence 및 decision-plane 경계를 참조한다. |
| 주식 factor 파이프라인 | `src/investment_pipeline/pipeline.py`, `factors.py`, `completeness.py` | 데이터 완전성과 PIT 팩터 구성을 재사용 대상으로 검토한다. |
| 출처/증거/충돌/환각 검사 | `claim_contract.py`, `source_quality_agent.py`, `source_retrieval_agent.py`, `conflict_detection_agent.py`, `hallucination_guard_agent.py` | Skill 안에 동일한 검증 규칙을 다시 구현하지 않는다. |
| 진입 구현 사례 | `src/investment_pipeline/crypto_entry.py` | 구현·테스트 패턴 참고용이다. 암호자산 임계값을 주식 전략에 그대로 전이하지 않는다. |
| multi-asset 출력 스키마 | `schemas/multi_asset_decision_v0.1.schema.json` | 새 결과 계약은 기존 스키마 호환성을 확인한다. |
| 과거 이력/결과 기록 | `src/investment_pipeline/history/`, `docs/investment/HISTORICAL_INVESTMENT_DB_V1.md` | 의사결정 시점 데이터와 후속 outcome을 분리해서 기록한다. |
| 연구 운영 루프 | `docs/governance/INVESTMENT_RESEARCH_LOOP.md` | 가설 → 데이터 계약 → 사전등록 → QA/PIT → 백테스트 → 반증 → 증분 가치 → 승격 게이트를 재사용한다. |
| 시장 점검 계약 | `docs/market/MARKET_CHECK_WORKFLOW_V1.md` | D/W/M 및 fail-closed 원칙과 충돌하지 않도록 맞춘다. |

파일/문서의 존재를 확인한 것이며, 모든 기능이 운영에서 정상 실행됨을 뜻하지 않는다.

## 4. 중요한 차단 사항

### GitHub Issue #27

- 이슈: https://github.com/chayobi03-cyber/investment/issues/27
- 확인 시 상태: OPEN
- 요지:
  - 마지막 두 개 5분 봉으로 계산한 변화를 15분 또는 일간 변화율로 잘못 해석할 수 있다.
  - freshest symbol의 timestamp를 전체 freshness로 사용해, 최신 USD/JPY 관측이 stale KOSPI/KOSDAQ/한국 리더 시세를 가릴 수 있다.
  - 불완전하거나 모호한 관측이 DATA_QUALITY=GREEN처럼 보이며 신뢰할 수 없는 위험/매수 신호를 노출할 수 있다.
- 필수 해결 방향:
  - 5m / 검증된 15m / 이전 정규 세션 종가 대비 일간 변화율을 서로 다른 horizon으로 표현
  - 일간 기준으로 검증된 전일 종가 사용 및 기준 timestamp 보존
  - 종목별·필수 그룹별 freshness와 세션 인식 검증
  - 누락/불일치/출처 또는 timestamp 불확실 시 fail-closed
  - 회귀 테스트에서 stale Korean index와 fresh USD/JPY 사례를 검증

### M1 및 실행 상태

- M1: BLOCKED / NOT VERIFIED
- BUY_ALLOWED: false
- EXECUTION_ALLOWED: false
- PROMOTION: DISABLED
- Issue #27의 해결 및 회귀 증거가 확인되기 전에는 market monitor의 compact RISK/TREND/DATA_QUALITY 필드를 authoritative buy-timing 근거로 사용하지 않는다.
- 확인 가능한 GitHub 응답만으로는 관련 필수 테스트가 성공했다고 말할 수 없다. 이번 세션에서 코드 테스트를 실행하지 않았다.

## 5. 관련 산출물

### 스킬화 타당성 평가

- 문서: [DOWNTREND_TRADING_SKILLIZATION_ASSESSMENT_V1_2026-10-16.md](DOWNTREND_TRADING_SKILLIZATION_ASSESSMENT_V1_2026-10-16.md)
- URL: https://github.com/chayobi03-cyber/investment/blob/main/docs/research/DOWNTREND_TRADING_SKILLIZATION_ASSESSMENT_V1_2026-10-16.md
- 평가 문서 커밋: `cf951cbb2c9cc6e8f4877323f5c4f2b04b75bc52`

### 기존 기준 문서

- [B0 Baseline Freeze](B0_BASELINE_FREEZE_2026-10-16.md)
- [Stock Method Test Contracts](STOCK_METHOD_TEST_CONTRACTS_V1_2026-10-16.md)
- [Investment Method Benchmark](INVESTMENT_METHOD_BENCHMARK_2026-10-16.md)
- [Investment Research Loop](../governance/INVESTMENT_RESEARCH_LOOP.md)
- [Multi-Asset Sub-Agent Architecture](../investment/MULTI_ASSET_SUBAGENT_ARCHITECTURE_V0.1.md)
- [Historical Investment DB V1](../investment/HISTORICAL_INVESTMENT_DB_V1.md)
- [Issue #27](https://github.com/chayobi03-cyber/investment/issues/27)

## 6. 다음 세션 실행 순서

### P0 — M1 Data Integrity 차단 해소

1. Issue #27의 현재 상태와 구현을 다시 확인한다.
2. 5m/15m/daily horizon 계산, 종목별 freshness, 이전 정규 세션 종가, quote conflict를 각각 별도 테스트한다.
3. monitor, data pipeline, PIT provenance 및 decision gate 관련 회귀 테스트를 실행한다.
4. GitHub Actions 결과와 필요한 테스트 증거를 확인한다.
5. 결과가 미확인/실패이면 M1을 GREEN으로 표시하지 않는다.

완료 조건: Issue #27 acceptance criteria와 관련 회귀 테스트/CI가 실제 증거로 확인될 것. M1 승격 여부는 별도 게이트로 평가한다.

### P1 — 하락장 단기매매 연구 계약 정의

- 세 가지 후보를 독립적으로 사전등록한다.
  - 과매도 이후 반등 확인형
  - 지지 구간 반등형
  - 회복 신호 확인형
- 각 후보의 universe, PIT 기준, 가격/거래량 데이터, 진입·무효화·청산 조건, 최대 보유 기간, 거래비용, 슬리피지, episode/re-arm 기준을 정의한다.
- 비교군: 현금 보유, 동일 종목 단순 보유, 기존 기준선/전략.
- 결과 지표: 비용 차감 후 기대값, MDD, 95% ES/tail loss, MAE/MFE, 거래 빈도, 시장 국면별 성과, OOS/워크포워드 안정성.
- 임계값과 전략 변형은 OOS 결과를 본 뒤 고르지 않는다.
- M1이 GREEN이 아니면 백테스트 성과 주장을 승인된 매매 근거로 취급하지 않는다.

### P2 — Skill 런타임 확인 및 최소 프로토타입

1. 실제 Skill을 호출하는 제품/런타임, 로더, 경로 및 배포 규약을 먼저 확인한다.
2. 확인 후 최소 상위 Skill 하나만 만든다.
3. Skill 본문은 절차/호출 조건/계약/보고 형식만 두고 상세 규칙은 기존 문서에 연결한다.
4. 계산·데이터 QA·위험·승인은 기존 코드로 유지한다.
5. 동일 시나리오로 기존 메타 프롬프트와 Skill을 비교한다.

비교 지표:
- 필수 검사 누락률
- 잘못된 데이터에서의 차단 준수율
- 출력 계약 준수율
- 증거 추적 가능성
- input/output token 및 실행 비용
- 재현성과 변경 비용

비교 측정 없이 토큰 절감률이나 품질 개선을 주장하지 않는다.

### P3 — 통합 검토

- 기능 품질 실험과 전략 수익성 실험을 독립 판정한다.
- Skill이 좋아도 전략을 자동 승격하지 않는다.
- 전략 성과가 좋아도 BUY_ALLOWED/EXECUTION_ALLOWED를 자동 변경하지 않는다.
- 하위 Skill 분리는 독립 호출과 테스트 편익이 측정된 뒤 결정한다.

## 7. 다음 세션의 완료 보고 필수 항목

1. 현재 Issue #27 및 M1 상태와 근거
2. 수정한 경로와 변경 전/후 동작
3. 실행한 테스트 명령 및 실제 결과
4. CI 실행 URL/상태 또는 미확인 사유
5. B0 비교 기준선 불변 여부
6. BUY_ALLOWED / EXECUTION_ALLOWED / PROMOTION 상태
7. Lesson Learned 및 rule change 여부
8. Git 저장 여부와 commit SHA

테스트 실행 기록이 없으면 PASS로 쓰지 않는다. 파일 생성만으로 Skill이 배포되었다고 쓰지 않는다.

## 8. Lesson Learned / Rule Change / Git

- **Lesson Learned:** 기존 코드 에이전트와 오케스트레이터를 Skill로 복제하지 않는다. Skill은 반복 절차와 표현을 표준화하고, 결정론적 코드는 계산·무결성·권한을 강제하며, 백테스트는 전략의 경제적 가치를 검증한다.
- **Rule Change:** NO. 이번 handoff는 기존 투자 규칙/임계값을 변경하지 않는다.
- **Git:** YES. 이 handoff 자체가 다음 세션에서 재사용할 상태와 순서를 고정하므로 별도 문서 커밋으로 저장한다.
- **테스트:** 이 문서는 문서 전용 변경이며 코드 테스트를 수행하지 않았다.


## Session follow-up — Issue #27 remediation candidate

- Inspected the existing draft PR #30 instead of duplicating the fix: https://github.com/chayobi03-cyber/investment/pull/30
- The PR branch now includes verified close-endpoint handling and fail-closed behavior if an active required series lacks a verified prior-session close. Regression tests cover an incomplete prior session close and missing prior close.
- Current PR head: `6c9ba73cae60c32eded9f25a0024a9d17fd58037`.
- `collectors-ci` run #38839367370 passed on that exact head (36 tests passed in 1.22s): https://github.com/chayobi03-cyber/investment/actions/runs/38839367370
- Verification is limited to the PR branch's collectors suite. No local tests were run, the patch is not merged to `main`, and end-to-end deterministic workflow/Historical DB/HOTL evidence remains unverified.
- Static review follow-up still required: test and justify the 30-minute active-series freshness tolerance against a 15-minute return horizon; rerun review/CI with the current base. Issue #27 and Issue #31 remain OPEN.
- Safety remains unchanged: M1 BLOCKED / NOT VERIFIED; `BUY_ALLOWED=false`, `EXECUTION_ALLOWED=false`, `PROMOTION=DISABLED`. No baseline, threshold, or production permission changes.
