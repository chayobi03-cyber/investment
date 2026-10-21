# META PROMPT — PR #30 Current-Main Audit, Market-Monitor Repair & CI Evidence v1.0

- 작성일: 2026-10-22 (KST)
- 대상 저장소: https://github.com/chayobi03-cyber/investment
- 대상 PR: https://github.com/chayobi03-cyber/investment/pull/30
- 관련 이슈: https://github.com/chayobi03-cyber/investment/issues/27, https://github.com/chayobi03-cyber/investment/issues/31
- 목적: 최신 main 대비 PR 검토, 검증된 결함 수정, 회귀 테스트와 현재 커밋의 CI 증거 확보
- 운영 모드: CODE_CHANGE_ALLOWED_ON_BRANCH / PRODUCTION_PROMOTION_DISABLED

---

## 1. 역할

너는 시니어 Python 엔지니어, 거래소 시계열 데이터 품질 엔지니어, 퀀트 백테스트 검증자, CI/release 엔지니어다. 일반적인 코드 설명이나 계획만 내놓지 말고, 저장소와 실행 환경에 실제 접근 가능한 범위에서 조사·수정·테스트·증거 수집을 완료한다.

반드시 다음을 분리한다.

1. 관찰한 사실과 재현 가능한 증거
2. 코드로 확인한 결함
3. 아직 검증되지 않은 가설
4. 제안하는 설계 또는 규칙 변경
5. 현재 구현에서 안전하게 실행 가능한 범위
6. CI 또는 데이터/권한 부재로 실행할 수 없는 범위

알 수 없는 환경·도구·API·시크릿을 가정하지 않는다. 명령, 테스트, CI 실행을 실제 수행하지 않았으면 수행했다고 보고하지 않는다.

## 2. 목적 및 완료 정의

PR #30이 해결하려는 Issue #27의 근본 문제를 최신 main과 비교해 독립적으로 감사한다.

- 5분 수익률, 검증된 15분 수익률, 현재 세션 수익률, 직전 완료 세션의 종가 대비 수익률을 섞지 않는다.
- 각 필수 시리즈·필드·거래 세션별 freshness를 검증한다. 한 종목의 최신 타임스탬프가 오래된 한국 지수/리더 데이터를 정상으로 만들면 안 된다.
- 누락·오래됨·충돌·시간축 불일치·유효하지 않은 세션 종가가 존재하면 안전하게 fail-closed한다.
- PR 수정사항을 최신 main 위에서 검증하고, 정확한 신규 커밋 SHA에서 CI 결과를 확보한다.
- 실제 코드 테스트와 end-to-end DB/HOTL 검증을 별도 게이트로 판정한다.
- 완료 시 Issue #27 / #31의 상태, PR 상태, 남은 위험 및 다음 액션을 증거와 함께 보고한다.

목표는 높은 백테스트 수익률이 아니라 잘못된 시장 상태 판단을 방지하는 것이다. 이번 변경으로 매수 임계값을 조정하거나 매수/실행 권한을 활성화하지 않는다.

## 3. 고정된 운영 안전 조건

- BUY_ALLOWED=false 유지
- EXECUTION_ALLOWED=false 유지
- PROMOTION=DISABLED 유지
- B0 기준선 및 기존 threshold 동결
- 실제 주문, paper/live execution, production deployment 금지
- main 직접 수정 금지
- 현재 PR의 과거 CI를 최신 main 또는 신규 커밋의 CI 증거로 재사용 금지
- 관련 없는 리팩터링, 전략 개선, 스키마 전면 변경을 이번 수정에 섞지 말 것
- 규칙/임계값 변경이 필요해 보이면 별도 버전의 변경 제안서와 근거를 제출할 것

이 프롬프트는 기능 브랜치에서의 코드 변경과 CI 실행을 허용하지만 PR 병합, production 승격, 거래 허가는 허용하지 않는다.

## 4. 기준선 확인 — 매번 최신 원격 상태부터 재조회

아래는 2026-10-22 조사 시점의 참조 스냅샷이다. 작업 실행 시점의 진실로 하드코딩하지 말고 GitHub에서 다시 확인한다.

- main SHA 참조: c30f3f0b7e2ed84f4b668b4778d57e51fc1b5312
- PR #30 head 참조: 6c9ba73cae60c32eded9f25a0024a9d17fd58037
- 비교 기준의 merge base 참조: 2e7e59eb96440eda0be9177e3ffc4d5df4651517
- 당시 main 대 PR head 비교: PR 방향으로 ahead_by=19, behind_by=20
- PR #30 상태: OPEN / DRAFT / 미병합
- Issue #27, #31: OPEN
- PR head에서 확인된 기존 collectors-ci 실행: run 38839367370, 성공, 36 tests / 1.22s로 기록됨. 이는 당시 PR head에 대한 과거 증거이며 현재 main 또는 새 수정 커밋의 성공을 뜻하지 않는다.
- 현재 main의 scripts/market_monitor/poll.py에서는 Yahoo chart 5분봉 중 마지막 두 가격으로 change_pct를 계산한다. 이는 구성상 5분봉 간 변동이며, 일간 또는 검증된 15분 변동으로 표시하면 안 된다.
- 현재 main의 freshness 계산은 모든 시리즈 중 가장 늦은 관측 시각을 이용한다. FX 등 한 시리즈가 신선하더라도 한국 지수/리더가 오래됐을 때 전체 데이터 품질이 GREEN이 될 수 있다.
- 현재 main의 tests/test_market_monitor.py에는 위 두 실패 모드를 모두 막는 충분한 회귀 테스트가 확인되지 않았다.

PR 브랜치는 최신 main과 크게 갈라져 있다. 따라서 단순 merge, 무검토 rebase, 무검토 force-push 중 어느 것도 자동으로 선택하지 않는다.

### 필수 시작 명령/조사

    git fetch origin --prune
    git status --short --branch
    git rev-parse origin/main
    git rev-parse origin/fix/market-monitor-horizons-issue-27
    git merge-base origin/main origin/fix/market-monitor-horizons-issue-27
    git log --oneline --decorate --graph --left-right origin/main...origin/fix/market-monitor-horizons-issue-27
    git diff --stat origin/main...origin/fix/market-monitor-horizons-issue-27
    git diff --find-renames origin/main...origin/fix/market-monitor-horizons-issue-27

명령에 필요한 원격 ref/접근권한이 없으면 사용 가능한 GitHub MCP/API 대안을 활용하고 결과를 명시한다. 현재 main SHA와 PR head SHA를 감사 보고서에 기록한다.

## 5. 변경사항 감사 — 구현보다 먼저 수행

다음 파일을 최소 범위로 검토한다.

- config/market_monitor.json
- scripts/market_monitor/poll.py
- tests/test_market_monitor.py
- .github/workflows/collectors-ci.yml
- .github/workflows/market-monitor.yml
- .github/workflows/historical-db-v1-ci.yml
- docs/market/MARKET_CHECK_WORKFLOW_V1.md
- docs/strategy/Handoff.md 및 관련 Issue/PR 기록

추가 종속성 파일/소비자가 발견되면 함께 확인한다.

각 변경 파일마다 다음을 기록한다.

- 최신 main 버전의 동작
- PR 버전의 동작
- 변경 의도와 실제 구현의 일치 여부
- 새로 생긴 회귀 가능성 및 외부 소비자/스키마 호환성
- 재현 테스트의 존재 여부
- 유지 / 수정 / 제거 판단과 근거

PR은 당시 기준으로 3개 파일을 변경했고, 추가 756 / 삭제 101 수준이었다. 현재 diff는 다시 산출한다. 숫자가 달라졌다면 그 이유를 추적한다.

### 브랜치 통합 정책

1. 원본 PR branch와 main을 보존하고 작업 트리 상태를 확인한다.
2. 최신 main에서 별도 통합/검증 worktree 또는 기능 브랜치를 만든다.
3. PR의 19개 ahead commit을 통째로 가져오기 전에 각 commit의 목적과 관련성을 조사한다.
4. 가능하면 PR의 최종 코드 diff에서 필요한 최소 수정만 최신 main에 재적용해 범위를 줄인다. 여러 커밋을 재생산하거나 rebase해야 한다면 commit range-diff와 최종 트리 diff로 의미가 바뀌지 않았음을 입증한다.
5. 충돌 해결은 추측하지 않는다. 각 충돌에 대해 main과 PR의 의도를 확인하고 테스트로 동작을 고정한다.
6. 기존 PR을 안전하게 갱신할 수 있으면 해당 PR을 유지한다. 새 PR이 불가피하면 기존 PR을 먼저 닫지 말고 대체 PR에 교차 링크와 이유를 남긴 뒤 중복/상태를 정리한다.
7. 작업은 별도 브랜치에서만 커밋한다. main 직접 push 및 PR 자동 병합은 금지한다.

## 6. 핵심 결함·회귀 검증 체크리스트

### A. 반환 기간(horizon) 정확성

데이터 스키마에 서로 명확한 필드를 둔다.

- 5-minute return
- validated 15-minute return
- current-session return against a verified prior-session close
- last-completed-session close-to-close return

각 결과에는 최소 관측 시각, 기준 관측 시각, 실제 경과 초/분, 시장 시간대, 계산 버전, 사용한 가격 필드 및 validation 상태를 추적할 수 있어야 한다. 소비자가 관측 기간을 검증할 수 없다면 해당 반환값을 확정값으로 노출하지 않는다.

현재 PR 후보의 _period_return()은 요청 기간의 60%~140% 범위 안에 있는 과거 봉을 선택한다. 명목 15분 반환에서 10분 간격의 관측값이 선택될 수 있으므로 실제 15분 반환과 혼동할 수 있다. 이 구간은 특히 검증한다.

필수 테스트:

- 정확히 5분/15분 간격의 정상 fixture
- 10분 이동값이 15분 값으로 오인되지 않는 경우
- 20분 이동값이 15분 값으로 오인되지 않는 경우
- timestamp endpoint/봉 간격 누락, 중복 시각, 정렬되지 않은 입력
- 다른 거래일의 봉을 같은 세션의 기준값으로 사용하는 경우
- 종가가 결측/NaN/무한대/0/음수이거나 타임스탬프가 미래 또는 timezone 미포함인 경우
- 간격 검증 실패 때 None/UNKNOWN/DATA GAP으로 fail-closed하는 경우
- provider timestamp가 봉 시작 또는 종료 시각 중 무엇인지 원문/fixture 근거로 확인한 경우

수익률 허용 오차는 명확한 데이터 공급자 의미와 테스트 근거로 설정한다. 값이 없거나 시간 간격이 맞지 않으면 가장 가까운 봉을 무조건 골라 수익률을 만들어내지 않는다.

### B. 세션 종가/일간 반환 정확성

- 일별 마지막 관측봉을 완료된 세션 종가로 간주하지 말고, 해당 거래소의 정상 세션 종가와 허용 오차로 검증한다.
- 최종 정규 세션 봉이 누락됐거나 너무 이른 경우, 종가 대비 수익률을 만들지 않는다.
- 직전 완료 세션 종가, 직전 세션 종가의 검증 상태, 최신 데이터의 거래 세션을 각각 보존한다.
- 현재 세션 반환값은 검증된 직전 세션 종가가 존재하고, 데이터 timestamp/세션이 올바를 때만 제공한다.
- 같은 세션의 미완성 봉을 완료된 세션 종가로 사용하지 않는다.
- 프리마켓/정규장/장후/주말/휴장일/조기폐장/서머타임 전환 fixture를 포함한다.
- 휴장일 및 조기폐장을 모르면 평일 일정만으로 정상 세션이라고 추정하지 않는다. 지원 가능한 거래소 캘린더를 확인하거나 해당 경우를 UNKNOWN/DATA GAP으로 처리한다.

별도 검토해야 할 설계 위험: KOSPI/KOSDAQ/미국 주가지수의 정규장 시간과 FX·미국 금리·금/원유 선물의 데이터 세션이 모두 같다고 가정하면 안 된다. 각 심볼의 거래소/상품 특성 및 provider timestamp 의미를 검증한다. 세션 정의가 확실하지 않은 시리즈에 임의의 주식시장 세션을 적용하지 않는다.

### C. 종목별 신선도(freshness) 및 데이터 품질

- freshness는 필수 instrument/field/session별 관측 시각으로 판단한다.
- 전체에서 가장 최신인 시리즈의 시각을 전체 freshness로 사용하지 않는다.
- 필수 시리즈 하나라도 stale/missing/invalid/conflicting이면 해당 종목과 그룹의 상태가 이를 반영해야 한다.
- 신선한 USD/JPY가 stale KOSPI, KOSDAQ 또는 한국 리더의 결함을 가리지 않는 회귀 fixture를 둔다.
- 미래 시각, 파싱 실패, 관측 시각 누락, API 오류, 불완전한 payload, 중복된/역순 timestamp에 대한 결과를 명시한다.
- 데이터 상태가 AMBER/RED/UNKNOWN이면 BUY_TRIGGER와 매수/실행 권한을 정상 상태로 승격시키지 않는다.
- 상태 계산, freshness, threshold horizon의 조합이 의미상 일치하는지 검토한다.
- 실패한 quote에 남아 있는 예전 수치가 계산에 이용되지 않는지 확인한다.

특히 현재 설정의 max_stale_minutes=30과 15분 반환값 사용의 관계를 검토한다. 30분 허용이 적절하다고 가정하지 말고, provider 지연/바 주기/계산 목적을 증거로 평가하고 경계 테스트를 한다. 기존 threshold는 이번 작업에서 조용히 변경하지 않는다. 허용 오차 변경이 필요하면 별도 versioned proposal로 분리하고 변경 전/후 영향, 검증 설계, 승인 필요성을 기록한다.

### D. 상태 집계와 호환성

- active session과 closed session이 서로 다른 반환 기간을 사용하는 것이 명시적이어야 한다.
- 임계값은 해당 기간에 맞는 필드에만 적용한다.
- 일부 입력이 없는 경우 평균이나 breadth 계산에서 제외된 수와 분모/coverage를 보고한다.
- 표본 수가 불충분하면 GREEN 또는 확정 추세가 되지 않도록 fail-closed한다.
- metrics의 legacy alias가 어느 horizon을 뜻하는지 계약서/테스트에 고정한다. 불명확하거나 시간축이 다른 alias는 deprecate/명확화한다.
- schema version 변경, 기존 workflow/모바일/monitor 소비자 호환성 및 null 처리에 대한 회귀 테스트를 한다.
- as-of 시간을 인자로 주입해 동일한 fixture/config의 출력이 결정론적으로 같게 만든다. live network/현재 시각을 사용하는 테스트를 결정론적 회귀 테스트와 분리한다.

### E. 2026-10-12 급락 재현

Issue #27에 기록된 관측을 fixture로 유지한다.

- KOSPI 공식 종가 변동 예시: -3.65%
- KOSDAQ 공식 종가 변동 예시: -4.83%
- 삼성전자 / SK하이닉스 및 인덱스 데이터가 종가 기준과 일치하는지 검증
- 마지막 두 5분봉 변화율이 daily close-to-close 변동으로 사용되지 않는지 검증
- USD/JPY 등 최신 시리즈가 국내 시장 관측보다 최신이어도 데이터 품질이 GREEN이 되지 않는지 검증

날짜가 고정된 회귀 fixture는 출처와 timestamp를 함께 보존한다. 해당 숫자를 현재 시장 상황으로 표시하지 않는다.

## 7. GitHub/Hugging Face 주식 관련 벤치마크

벤치마크는 현재 PR의 데이터 정합성·재현성·검증 계약을 개선하기 위한 참고자료다. 다른 프로젝트의 전략 성과나 홍보 문구를 수익 보장의 증거로 사용하지 않는다. 조사 실행일에 저장소/데이터 카드의 최신 상태, 라이선스, 버전, 출처를 다시 확인한다.

### 7.1 Microsoft Qlib — 연구 평가 및 재현성

- 저장소: https://github.com/microsoft/qlib
- 공식 benchmark 표: https://github.com/microsoft/qlib/blob/main/examples/benchmarks/README.md
- 관찰할 패턴: 예측-수익 상관(IC/Rank IC, ICIR)과 포트폴리오 수익률, Information Ratio, Max Drawdown을 별도로 평가한다. 문서에 20개 random seed의 평균/표준편차를 사용하는 비교가 있다.
- 이번 프로젝트에 적용: 회귀 테스트·리스크 지표·벤치마크·불확실성을 한 숫자로 뭉치지 않는다. 결과에 코드/데이터/config 버전을 기록하고 재현 가능한 fixture 기반 검증을 분리한다.
- 적용하지 말 것: Qlib의 alpha-prediction benchmark를 intraday quote freshness의 직접 검증 수단으로 사용하거나 기존 threshold를 자동 변경하지 않는다.
- 주의: 데이터셋/워크플로 버전이 달라지면 결과도 달라질 수 있으므로 발표된 숫자를 현재 프로젝트 성과와 직접 비교하지 않는다.

### 7.2 FinRL / FinRL-X — 비교 기준선과 계층 분리

- 원형 연구 프레임워크: https://github.com/AI4Finance-Foundation/FinRL
- 원형 benchmark 문서: https://github.com/AI4Finance-Foundation/FinRL/blob/master/docs/source/finrl_meta/Benchmark.rst
- 최신 모듈형 프로젝트: https://github.com/AI4Finance-Foundation/FinRL-Trading
- 관찰할 패턴: passive/buy-and-hold, mean-variance, min-variance, equal-weight 기준선을 두고 누적/연환산 수익률, 변동성, Sharpe, Max Drawdown을 함께 보고한다. FinRL-X README는 data, strategy, backtest, execution과 사전 위험 확인을 분리하는 구조를 제시한다.
- 이번 프로젝트에 적용: 전략 성능 평가 전 데이터 정확성과 거래 가능성을 검증한다. buy-and-hold/현금/간단한 기준선과 위험 지표를 같이 보고한다. 데이터·신호·리스크·권한·실행은 계약으로 분리한다.
- 적용하지 말 것: 강화학습 또는 라이브 거래 코드를 현재 모니터 수정에 넣거나 FinRL 프로젝트의 자체 보고 수익률을 독립적으로 검증된 투자 성과처럼 인용하지 않는다.

### 7.3 backtesting.py — 거래/비용 경계조건과 산출물 정확성

- 프로젝트: https://github.com/kernc/backtesting.py
- 변경 이력: https://github.com/kernc/backtesting.py/blob/master/CHANGELOG.md
- 관찰할 패턴: 수수료 양쪽 체결 처리, stop-loss 가격이 갭으로 넘어가는 경우, 같은 봉에서 손절/익절이 동시에 맞는 경우, 연환산 수익률 산출의 오류 수정이 독립적인 버그 항목으로 관리된다.
- 이번 프로젝트에 적용: 시간축 및 수치 계산을 작은 단위 함수로 분리하고 경계조건 fixture를 만든다. 보고되는 반환기간/위험상태가 입력 데이터와 정확히 일치하는지 증명한다.
- 적용하지 말 것: 백테스트 엔진의 동작을 실제 시장 데이터의 정확성 증명으로 간주하지 않는다. 이번 PR에서 불필요한 매매 체결 모듈을 추가하지 않는다.

### 7.4 Hugging Face — 한국 주식 EOD 데이터의 fixture 후보

- 후보: https://huggingface.co/datasets/aikstockdata/korea-equity-daily
- 조사 페이지에 제시된 범위: KOSPI/KOSDAQ/KONEX 2,787개 종목, 321 거래일, 2025-05-28~2026-09-17의 일별 종가와 DART 공시 영향 관련 테이블.
- 적용 가능성: 한국 주식 EOD 스키마/누락·중복 검증 fixture, 가격-종목 마스터-공시 관계를 점검하는 오프라인 연구 자료 후보.
- 한계: 5분/15분 모니터 검증을 대체하지 않는다. 데이터의 생성·갱신 시점, 원천, 라이선스, corporate action/종목 상장폐지 처리와 point-in-time 유효성을 확인하기 전에는 권위 있는 실시간/과거 원천으로 승격하지 않는다.

### 7.5 Hugging Face — 광범위한 일봉 히스토리 후보

- 후보: https://huggingface.co/datasets/paperswithbacktest/Stocks-Daily-Price
- 조사 페이지는 약 2,580만 행의 일별 가격과 1962년 이후 데이터를 표시한다. 검색 스니펫과 dataset viewer의 마지막 날짜 표현이 일치하지 않았으므로 실제 최신 범위는 이번 실행 시 revision/card를 확인해야 한다.
- 적용 가능성: 장기 EOD backtest의 오프라인 비교 데이터 후보.
- 한계: 라이선스는 “other”로 표기되어 있으며, 실제 다운로드/사용 전 약관·출처·기업행동 조정·생존편향·ticker mapping·결측·수정 이력을 검증해야 한다. 5분/15분 quote 정확성이나 현재 시세의 원천으로 사용하면 안 된다.
- 필수 행동: dataset revision/hash, card snapshot, 열 정의, 행 수, 날짜 범위, 원천/라이선스를 보고서에 고정한다. 검증하지 못하면 “후보/미검증”으로 남긴다.

### 7.6 벤치마크 판단 원칙

- 벤치마크는 체크리스트와 설계 패턴을 가져오는 용도이며, 소스 코드를 통째로 복사하거나 복잡한 ML/DRL을 PR에 추가하지 않는다.
- 외부 프로젝트의 모델 성능 순위보다 기간 정합성, source provenance, 누락의 fail-closed, 결정론적 테스트, 비용/체결 경계조건을 우선한다.
- 데이터 카드/저장소가 라이선스와 출처를 명확하게 설명하지 못하면 production 근거로 사용하지 않는다.
- 벤치마크 결과마다 URL, 접근일, revision/commit, 확인한 주장과 미확인 사항을 기록한다.

## 8. 테스트 계획

우선 현재 프로젝트의 실제 테스트 런너·dependencies·CI 명령을 확인한다. 아래는 의도한 테스트 종류이며 프로젝트 파일을 읽지 않고 무조건 복사 실행하지 않는다.

1. 변경 대상 단위 테스트: 반환 기간, 세션 종가, freshness, state aggregation
2. 회귀 테스트: Issue #27의 -3.65% / -4.83% 불일치 및 FX 신선도 착시
3. 실패/경계 테스트: stale/missing/conflicting/future timestamps, 잘못된 timezone, 거래 휴일/조기폐장, bar gap
4. 스키마 및 호환성 테스트: schema version, legacy alias, consumer, null/missing semantics
5. 저장소 전체 테스트: 발견된 표준 테스트 명령으로 실행
6. CI: collectors-ci 및 변경 영향이 있는 market-monitor, historical-db-v1 CI
7. 저장/영속화 확인: Issue #31 요구가 수정 범위에 들어간 경우 실제 Historical DB adapter/schema/runtime로 영수증을 반환하는지 증명. 어댑터가 없거나 테스트되지 않으면 BLOCKED/NOT VERIFIED로 보고.

네트워크에서 실시간 시세를 끌어오는 테스트와 frozen fixture 테스트를 분리한다. unit test가 provider를 호출하거나 시간/거래소 캘린더에 의존하면 테스트용 clock/provider를 주입한다.

## 9. CI 증거 기준

성공했다고 보고하려면 다음을 모두 확보한다.

- 테스트/CI가 실행된 정확한 commit SHA
- 실행된 workflow 이름과 run ID/URL
- run status=completed, conclusion=success
- 필수 job이 모두 성공했는지와 재시도/skip 여부
- 실제 테스트 명령, 테스트 수, 실패/skip 수와 실행 시간
- artifacts/logs가 제공되면 URL과 manifest
- main 기준선 SHA, PR head SHA, 최종 수정 SHA
- PR files changed와 최종 diff 검토 결과

빈 status 응답, pending status, 오래된 run, 다른 commit에서 성공한 결과를 CI 성공으로 간주하지 않는다. API가 run 세부정보를 반환하지 않으면 “확인 불가”로 남긴다. 새 변경 커밋을 push한 후에는 해당 SHA의 CI run이 새로 시작/완료된 사실을 확인한다.

최소 요구: 변경 관련 collectors-ci 통과 및 영향받는 workflow의 통과. Historical DB/HOTL의 end-to-end 증거가 없으면 Issue #31 해결로 선언하지 않는다.

## 10. 완료 게이트

### Gate A — 기준선 감사

- 최신 main, PR head, merge base 및 diff 기록
- 기존 PR 변경사항의 의미/범위 설명
- 결함과 가설을 분리한 finding 목록 작성

Gate A 미통과 시 구현보다 먼저 상태를 정리한다.

### Gate B — 수정 및 회귀 검증

- 구현상 결함마다 실패 테스트를 먼저 재현하거나 회귀 테스트를 추가
- 최소 범위 수정 적용
- 새 테스트 통과
- 관련 전체 테스트 통과

### Gate C — 새 커밋 CI 증거

- 정확한 신규 SHA에 대한 필수 CI 결과 확보
- 유효한 테스트/로그/아티팩트 링크 기록
- status가 pending/empty/old이면 Gate C 불통과

### Gate D — PR 판단

- diff가 최신 main 대비 최소 범위인지 검토
- 코드/테스트/CI/문서 일치 확인
- Issue #27과 #31의 수용 기준을 각각 판정
- PR은 통과 증거가 충분해도 기본적으로 READY_FOR_REVIEW 후보까지만 진행한다. 병합은 사용자/저장소 정책이 허용할 때 별도 승인 후 수행한다.
- 매수 권한, 실행 권한 및 PROMOTION은 계속 비활성화한다.

## 11. 필수 산출물

최소 산출물을 다음과 같이 남긴다.

1. docs/research/audits/PR30_BASELINE_AUDIT_2026-10-22.md 또는 실행일을 사용한 같은 형식의 보고서
   - 기준선 SHA, merge base, diff files/stats
   - Findings: severity, evidence, reproduction, affected component, remediation
   - open uncertainties/risks
   - 벤치마크 표와 채택/비채택 판단
2. 코드 및 회귀 테스트가 변경된 브랜치
3. 해당 커밋 SHA의 CI 증거
4. Handoff 업데이트 제안 또는 실제 업데이트
5. Lesson Learned: 원인, 탐지 방법, 수정, 회귀 방지, 임계값 변경 여부, Git 저장 여부

감사 문서는 실증한 내용과 앞으로 해야 하는 일을 구분한다. 테스트나 DB 저장을 실행하지 않았다면 완료형 문장을 쓰지 않는다.

## 12. 최종 보고 형식

### A. 판정
PASS / PARTIAL / BLOCKED / FAIL 중 하나. 각 Gate의 근거를 함께 쓴다.

### B. 기준선 비교
main SHA, PR head SHA, merge base, ahead/behind, diff 파일, 가장 중요한 변경 차이.

### C. 결함 및 수정
각 finding에 대해 severity, 재현 fixture/test, 수정 파일/행, 결과.

### D. 테스트/CI 증거
명령, 통과·실패·skip 개수, 정확한 SHA, run URL, job 결과, artifacts/logs.

### E. 외부 벤치마크
Qlib, FinRL/FinRL-X, backtesting.py, 선택한 Hugging Face 데이터의 사용 가능한 패턴, 비적용 사유, 라이선스/버전/출처 검증 상태.

### F. 남은 문제
문제, 영향, 임시 안전조치, 다음 액션, Issue #27/#31에 미친 영향.

### G. 운영 권한과 Git
BUY_ALLOWED=false, EXECUTION_ALLOWED=false, PROMOTION=DISABLED, B0 상태 확인. 수정 커밋/브랜치/PR 링크. merge 여부는 별도 표기.

### H. Lesson learned
새로 확인한 실패 패턴, 이를 막는 테스트/계약, 규칙 변경 필요성(NO/PROPOSAL), Handoff/Git 보존 필요성.

## 13. 시작 명령

이 메타프롬프트를 실행할 때 최신 원격 refs 및 CI 상태를 먼저 다시 조회하고, Gate A의 감사 결과를 기록한다. 이후 수정 가능한 결함을 실제 코드에서 고치고, 회귀 테스트 및 새 SHA의 CI 증거를 확보한다. 접근 권한/실행 환경/외부 의존성이 없으면 정확한 차단 사유와 대체 가능한 검증 범위를 보고한다.

문서 작성만으로 이슈 해결 또는 CI PASS라고 선언하지 않는다.
