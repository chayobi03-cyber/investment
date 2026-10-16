# 하락장 단기매매 전략 스킬화 타당성 평가 v1

- 평가일: 2026-10-16 (KST)
- 저장소: chayobi03-cyber/investment
- 상태: ASSESSMENT_COMPLETE / IMPLEMENTATION_DEFERRED / RESEARCH_ONLY
- 대상: 장기 투자 적격 주식의 하락 국면 단기 반등 거래
- 결정: **하이브리드 구조를 목표로 하되, 현재는 평가 문서만 저장한다. 실행 가능한 Skill 배포와 신규 전략 코드 구현은 보류한다.**
- 안전 제약: BUY_ALLOWED=false, EXECUTION_ALLOWED=false, PROMOTION=DISABLED

## 1. 핵심 결론

전략 분석 절차는 반복성이 높아 Skill 형태로 표준화할 가치가 있다. 다만 현재 저장소에는 이미 결정론적 게이트, 멀티자산 오케스트레이션, 데이터/PIT 검사, 소스 품질, 충돌 탐지, 환각 방지, 과거 기록 및 테스트가 있다. 같은 책임을 여러 하위 AI Skill로 다시 구현하면 중복·불일치·호출 오버헤드를 키울 수 있다.

권장안은 다음과 같다.

1. **지금:** 이 평가 문서를 기준으로 두고, 기존 투자 프레임워크와 중복되는 지침을 새로 복제하지 않는다.
2. **선행 차단 해소:** Issue #27 및 M1 데이터 무결성 검증을 완료하고, 테스트/CI 결과를 실제 증거로 확인한다.
3. **전략 연구:** 단기 하락 반등 아이디어를 사전등록된 연구 계약으로 정의해 기존 기준선과 비교한다. Skill 구현을 전략 성과 검증의 대체물로 취급하지 않는다.
4. **런타임 확인 후:** 실제 소비 주체가 확인되면 얇은 상위 Skill 하나를 작성한다. 세부 판단·계산·상태 전이는 기존 엔진과 모듈을 재사용한다.
5. **분리 조건:** 하위 Skill은 독립 호출, 독립 버전 관리, 독립 테스트, 다른 워크플로에서의 재사용이 입증된 기능만 대상으로 한다.

**핵심 구분:** Skill은 분석 절차와 증거 보고를 표준화한다. 결정론적 엔진은 계산·데이터 무결성·권한을 강제한다. 백테스트는 전략의 경제적 유효성을 평가한다. 이 셋은 서로 대체할 수 없다.

## 2. 저장소에서 확인된 현재 자산

원격 GitHub 기본 브랜치의 다음 항목을 확인했다.

| 기존 구성요소 | 실제 경로 | 스킬화 설계에 대한 의미 |
|---|---|---|
| 마지막 결정 통제 | src/investment_pipeline/decision_gate.py | 상위 권한 게이트가 이미 존재한다. 새 Skill이 권한을 판정·상향하면 안 된다. |
| 멀티자산 오케스트레이션 | src/investment_pipeline/multi_asset_subagents.py | PIT, 레짐, 위험, 증거, 출처, 충돌 및 환각 통제를 결합하는 구조가 이미 있다. |
| 종목 팩터 파이프라인 | src/investment_pipeline/pipeline.py, factors.py, completeness.py | 데이터 완전성 및 PIT 기반 팩터 생성 기능을 재사용 대상으로 검토한다. |
| 단기 진입 연구 구현 | src/investment_pipeline/crypto_entry.py | 가격/거래량 검증 및 진입 상태 구현 사례는 존재한다. 단, 암호자산 임계값과 로직을 주식 전략에 그대로 이식하지 않는다. |
| 출처·증거 통제 | claim_contract.py, source_quality_agent.py, source_retrieval_agent.py, conflict_detection_agent.py, hallucination_guard_agent.py | 증거 근거와 출처 검증을 새로운 Skill에 중복 구현하지 않고 계약으로 참조한다. |
| 출력 계약 | schemas/multi_asset_decision_v0.1.schema.json | 신규 출력은 기존 계약과의 호환성·확장 필요성을 먼저 확인한다. |
| 과거 기록 및 결과 평가 기반 | src/investment_pipeline/history/, docs/investment/HISTORICAL_INVESTMENT_DB_V1.md | 거래·판단·후속 결과를 별도 레코드로 누적하는 체계가 이미 정의돼 있다. |
| 테스트 계층 | tests/test_decision_gate.py, tests/test_multi_asset_subagents.py, tests/test_crypto_entry.py, tests/test_walk_forward_folds.py 등 | 기존 회귀 테스트 위에 새 전략 계약 테스트를 추가하는 방향이 적절하다. |
| 연구 운영 규칙 | docs/governance/INVESTMENT_RESEARCH_LOOP.md | 가설 → 데이터 계약 → 사전등록 → QA/PIT → 백테스트 → 반증 → 증분 가치 → 승격 게이트를 재사용한다. |
| 시장 점검 계약 | docs/market/MARKET_CHECK_WORKFLOW_V1.md | D/W/M와 연구 전용 권한 통제를 중복 정의하지 말고 기존 계약과 일치시킨다. |

이 항목들의 존재는 파일·문서를 확인한 결과다. 이것이 모든 기능이 운영 환경에서 성공적으로 실행된다는 의미는 아니다.

### 현재 제한 사항

- 저장소 루트 목록에서 독립적인 skills/ 배포 규약 또는 Skill 로더는 확인되지 않았다. 따라서 SKILL.md를 생성하더라도 어떤 실행 환경이 이를 불러올지 미확정이다.
- GitHub Issue #27은 OPEN이다: https://github.com/chayobi03-cyber/investment/issues/27
- 확인한 기준 문서상 해당 결함은 5분 봉 변화율을 일간/15분 변화율처럼 취급할 수 있고, 가장 최신인 다른 시장 심볼이 오래된 한국 지수 시세를 가릴 수 있는 문제를 포함한다.
- B0 기준선은 연구 비교용으로 동결되어 있지만 M1 통과나 전략 성과를 인증하지 않는다.
- 이번 조사에서 테스트 실행이나 최신 CI의 성공을 확인하지 않았다. 테스트 상태를 PASS로 간주하지 않는다.

## 3. 아키텍처 대안 비교

점수는 현재 저장소와 요구사항을 기준으로 한 설계 판단(1=불리, 5=유리)이며, 토큰 절감률이나 성과의 실측값이 아니다.

| 대안 | 일관성 | 안전 경계 | 중복 억제 | 유지비용 | 판단 |
|---|---:|---:|---:|---:|---|
| A. 긴 일반 프롬프트 유지 | 2 | 2 | 3 | 3 | 긴 지침 재입력과 실행 누락 위험 때문에 장기 기본안으로는 부적절 |
| B. 하나의 거대한 Skill | 4 | 2 | 2 | 2 | 출력은 표준화할 수 있으나 계산·승인까지 Skill 지침에 맡기면 통제력이 부족 |
| C. 기능별 다수 하위 Skill | 4 | 3 | 2 | 2 | 독립성이 입증되지 않은 분리는 호출·컨텍스트·버전·충돌 관리 비용을 증가 |
| D. 기존 시스템에 전부 코드로 통합 | 3 | 5 | 4 | 3 | 계산·검증에는 적절하나 분석 UX/절차 표준화 요구까지 코드로만 해결할 필요는 없음 |
| E. 얇은 Skill + 기존 결정론적 엔진 + 기존 저장소 | 5 | 5 | 5 | 4 | **권장 목표 구조**. 다만 런타임 및 데이터 게이트 확인 후 단계적으로 적용 |

## 4. 권장 목표 구조

User Request
→ Thin Downtrend-Trading Skill
  - 목적/호출 조건
  - 필수 입력 체크리스트
  - 기존 계약 호출 순서
  - 근거 중심 설명과 보고서
→ Existing Investment Pipeline
  - Data completeness / PIT / source quality
  - Market regime / permission / asset signal
  - Risk / evidence / conflict / hallucination controls
→ Existing Deterministic Decision Gate
  - DATA_NOT_READY / BLOCKED / RESEARCH_ONLY
  - BUY_ALLOWED=false
  - EXECUTION_ALLOWED=false
  - PROMOTION=DISABLED
→ Existing History Store + Experiment Artifacts
  - decision-time snapshot
  - strategy/run/data version
  - forward outcomes / error review

이 구조에서 새 Skill은 매수 권한이나 포트폴리오 위험 한도를 소유하지 않는다. 상태 계약을 소비하고 설명한다. 실제 입력값, 계산 결과, 출처 또는 CI 결과가 없으면 이를 지어내지 않고 상태를 미확인으로 남긴다.

### Skill 분할 정책

최초 구현은 상위 Skill 하나로 제한한다. 다음 기능을 즉시 각각 AI Skill로 쪼개지 않는다.

- 장기 투자 적격성
- 시장 레짐
- 진입·청산
- 위험 관리
- 전략 성과 검증
- 거래 사후 검토

대신 각 기능은 기존 코드·문서·스키마에 연결되는 명확한 계약으로 정의한다. 나중에 기능 하나가 독립적으로 여러 워크플로에서 사용되고, 별도 테스트·버전·호출이 실익을 준다는 근거가 생기면 그때 분리한다.

## 5. 신규 전략과 기존 기능의 경계

### 재사용할 영역

- PIT, 출처 provenance, 데이터 완전성 및 품질 검사
- 기존 시장/섹터/자산 신호와 위험·권한 계층
- D/W/M 분석 요구사항 및 공통 출력 계약
- 결정 상태, 증거, 거래 기록, forward outcome 저장 구조
- Walk-forward/OOS 및 사전등록 연구 운영 규칙

### 신규 연구로 남길 영역

- 장기 투자 적격 종목의 하락 구간에 특화된 진입 가설
- 과매도 반등 확인형, 지지 구간 반등형, 회복 확인형의 주식별 비교
- 단기 포지션 기간, 청산 및 시간 손절 가설
- 단순 보유·현금 유지 대비 증분 가치
- 거래비용 차감 후 기대값과 손실 꼬리 위험에 대한 반증 실험

기존 Buy Trigger/Market Regime 엔진을 교체하거나 새 점수에 중복 가중치를 추가하지 않는다. 별도 실험 ID와 고정된 계약으로 비교하고 기존 B0를 변경하지 않는다.

## 6. 입력·출력 계약 및 보안 경계

### 입력 최소 요건

- 종목 ID, 거래소, 분석 기준 시각
- 데이터 출처·관측 시각·사용 가능 시각
- 기준 종가와 검증된 OHLCV, 일봉·주봉·월봉
- 펀더멘털/공시 PIT 자료
- 시장·업종 상태, 거래비용/유동성 가정
- 포지션 크기 계산이 필요하다면 확인된 잔고·기존 노출·위험 한도
- 기존 파이프라인이 반환한 gate/status 및 blocker code

필수 입력 누락 시 종목의 현재 매수 가격이나 수량을 확정해서는 안 된다.

### 출력 최소 요건

- analysis_status
- data_quality
- market_regime
- long_term_eligibility
- short_term_setup
- entry_conditions
- invalidation_conditions
- risk_summary
- expected_value_status
- backtest_status
- buy_allowed
- execution_allowed
- evidence
- unresolved_issues
- next_action

새 필드가 기존 JSON Schema를 깨뜨리지 않는지 확인한다. 신호 점수와 권한 상태를 분리한다. 상위 Decision Gate가 내려준 false/blocked 상태를 Skill이 재해석하거나 높이지 못하도록 한다.

## 7. 단계별 실행 계획

### Phase 0 — 설계 및 선행 게이트 (현재)

산출물: 본 평가 문서.

완료 조건:
- 기존 구성요소와 중복 영역 확인
- 선택 아키텍처와 보류 사유 기록
- 매수·실행·승격 권한 유지

실패/정지 조건:
- 기존 권한·데이터 상태를 확인할 수 없으면 구현을 시작하지 않는다.

### Phase 1 — M1/Data QA 신뢰성 회복

선행 작업: Issue #27 요구사항을 만족하는 별도 변경 및 회귀 테스트.

최소 확인:
- 5m, 검증된 15m, 일간 close-to-close를 서로 다른 필드로 유지
- 일간 기준으로 검증된 전일 정규 세션 종가 사용
- 종목별/필수 그룹별 freshness
- 최신 USD/JPY가 stale KOSPI/KOSDAQ/리더 관측을 가릴 수 없게 처리
- 누락·불일치·시점 모호 시 fail-closed
- 회귀 테스트와 실제 CI 실행 증거 확인

완료 조건: 코드, 테스트 결과 및 필수 CI 증거가 확인되어 M1 상태가 공식적으로 재평가될 것. 테스트가 실행되지 않았거나 결과가 없으면 NOT VERIFIED로 유지한다.

### Phase 2 — 전략 연구 계약

산출물 후보: 독립된 downtrend 실험 계약, 가설/임계값 사전등록표, fixture 및 실패 시나리오.

완료 조건:
- 세 진입 유형의 가설·무효화 조건을 사전에 고정
- PIT/비용/유니버스/세션 및 체결 가정을 명시
- 현금·단순 보유·기존 전략을 비교군으로 지정
- 미래 정보 누수, 생존 편향, 시도한 모든 변형 기록을 통제

M1이 GREEN이 아니면 매매 관련 백테스트 또는 승격 주장을 허용하지 않는다. 문제를 연구용으로 탐색할 때도 증거 상태를 낮춰 표시한다.

### Phase 3 — 얇은 Skill의 런타임 적합성 확인 및 프로토타입

실제 Skill 소비 환경/로더/배포 경로가 확인된 경우에만 실행한다. 단순히 문서를 skills/에 놓는 것으로 활성화되었다고 주장하지 않는다.

동일 입력 시나리오를 기존 메타 프롬프트와 Skill에 공급하여 다음을 비교한다.
- 필수 검사 누락률
- 잘못된 데이터에서의 차단 준수율
- 출력 계약 준수율
- 근거 추적 가능성
- 평균 입력/출력 토큰과 실행 비용
- 결과 재현성 및 수정 비용

비교 수치가 없으면 절감률을 추정값으로 제시하지 않는다.

### Phase 4 — 통합 및 제한적 승격 검토

기능 비교와 별도로 전략 성과를 OOS/워크포워드, 거래비용, MDD, tail loss, MAE/MFE, cash/hold benchmark로 검증한다.

Skill 품질이 우수해도 전략 성과가 통과한 것은 아니다. 전략 성과가 우수해도 Decision Gate와 인간 승인 없이 BUY_ALLOWED/EXECUTION_ALLOWED를 변경하지 않는다.

## 8. 테스트 매트릭스

| 케이스 | 기대 상태/행동 |
|---|---|
| 필수 시계열 누락 또는 stale | DATA_NOT_READY, 거래 신호 유효화 금지 |
| 호가·기준 종가·당일 범위 충돌 | DATA_QUALITY 경고/차단, 조정될 때까지 fail-closed |
| 일봉·주봉·월봉 기준 시각 불일치 | 미해결로 표시, 가격/수량을 확정하지 않음 |
| 공시의 available_at이 판단 기준 시각보다 늦음 | PIT 제외, 관련 판단 차단 |
| 장기 사업/재무 구조 훼손 증거 | 장기 적격성을 재평가, 단순 낙폭 반등 근거 금지 |
| 하락 추세 지속이고 반등 확인이 없음 | 관찰/거래 안 함이 유효한 결론 |
| 손익비 또는 위험 예산 미달 | 후보 신호가 있어도 위험 게이트에서 차단 |
| 기존 gate가 BLOCKED/DATA_NOT_READY | Skill 결과가 상태를 상향할 수 없음 |
| 상위 모든 연구 검사가 PASS | 현 정책 아래 RESEARCH_ONLY, PROMOTION=DISABLED 유지 |
| 백테스트 성공, 실거래 증거 없음 | 연구 결과만 보고, 체결 성과로 주장하지 않음 |
| 가상 신호와 실제 체결 기록이 혼재 | 데이터에서 기록 유형을 분리 |
| 토큰 사용 감소, 출력 누락 증가 | 개선으로 간주하지 않고 프로토타입 수정/보류 |

## 9. 도입·보류·폐기 기준

### 도입 가능
- Skill을 실제로 불러오는 실행 환경이 확인됨
- 반복 업무/검사 누락을 줄인 효과가 비교 테스트로 확인됨
- 기존 모듈·스키마와의 중복 및 충돌이 통제됨
- 유지보수 비용이 실측된 편익을 상쇄하지 않음

### 현 단계에서 보류
- Skill 런타임/배포 경로가 확인되지 않음
- Issue #27 및 M1 증거가 미해결
- 단기매매 전략 자체의 OOS 유효성이 아직 입증되지 않음
- Skill 평가와 투자 성과 평가가 하나의 성공 지표로 혼합됨

### 분리 또는 폐기
- 새 하위 Skill이 기존 모듈의 중복 설명에 그침
- 독립적인 호출자·계약·테스트가 없음
- 유지 비용이 재사용 편익보다 큼

## 10. 리스크 및 롤백

- Skill의 지침과 코드의 동작이 달라질 수 있으므로 버전/계약 링크를 고정한다.
- 프롬프트 변경만으로 실험 임계값이나 프로덕션 설정을 변경하지 않는다.
- 신규 신호는 별도 experiment ID에 기록하고 기존 B0 기준선을 보존한다.
- 출력 계약 변경이 기존 사용자를 깨뜨리면 이전 스키마/Skill 버전으로 롤백한다.
- 데이터 품질이나 권한 상태가 악화되면 연구 결과에 관계없이 DATA_NOT_READY/BLOCKED로 후퇴한다.
- 배포/CI 결과가 확인되지 않으면 성공으로 보고하지 않는다.

## 11. Git 및 룰 변경 결정

- 평가 문서: **저장 필요 — YES**. 여러 세션에서 재사용할 아키텍처 판단과 실행 게이트를 포함한다.
- 실행 Skill 구현: **현재는 NO**. 소비 런타임이 확인되지 않았다.
- 전략 코드/임계값 변경: **NO**. 이번 작업에서는 변경하지 않는다.
- 기존 투자 규칙 변경: **NO**. M0–M3, 권한 상태, 기준선 및 M1 선행 게이트를 유지한다.
- 테스트 실행: **이번 변경은 문서 전용**이므로 코드 테스트를 실행했다고 주장하지 않는다. Issue #27 및 M1 필수 검증은 별도 선행 작업이다.
- 커밋: 이 문서를 별도 단일 문서 커밋으로 저장한다.

## 12. Lesson Learned

1. 이미 존재하는 코드 에이전트/오케스트레이터를 AI Skill로 재복제하지 말고 각 기술의 역할을 구분한다.
2. Skill 개수는 모듈화의 품질 지표가 아니다. 독립적인 책임·입출력 계약·테스트·호출 이점이 분리의 근거여야 한다.
3. Skill의 응답 품질, 데이터 파이프라인의 무결성, 전략의 경제적 성과를 서로 다른 검증 축으로 관리한다.
4. 실행 런타임을 확인하지 않은 SKILL.md 생성은 배포 완료를 뜻하지 않는다.
5. 선행 데이터 게이트가 막힌 상황에서 새로운 전략 또는 Skill을 승격하지 않는다.

## 13. 참고한 저장소 문서

- docs/governance/AUTO_COMMIT_POLICY_v0.1.md
- docs/governance/INVESTMENT_RESEARCH_LOOP.md
- docs/market/MARKET_CHECK_WORKFLOW_V1.md
- docs/investment/BUY_TRIGGER_ENGINE_V0.1.md
- docs/investment/MULTI_ASSET_SUBAGENT_ARCHITECTURE_V0.1.md
- docs/investment/HISTORICAL_INVESTMENT_DB_V1.md
- B0_BASELINE_FREEZE_2026-10-16.md
- STOCK_METHOD_TEST_CONTRACTS_V1_2026-10-16.md
- https://github.com/chayobi03-cyber/investment/issues/27
