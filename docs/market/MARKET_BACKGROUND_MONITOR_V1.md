# Market Background Monitor V1.1

## 목적

시장상황 확인을 대화형 요약이 아니라 **백그라운드 Event/Regime Detector**로 운용한다.

핵심 성공 기준:
1. 중요한 레짐/스트레스 변화를 놓치지 않는다.
2. 노이즈와 중복 알림을 줄인다.
3. 가격 외 Trend, Breadth, Rates, FX, Oil, Geopolitics, Cross-Asset를 함께 본다.
4. 사용자 컨텍스트 사용량을 최소화한다.
5. 데이터가 불충분하면 fail-closed 한다.

## 감시 축

- Market Trend: KOSPI, KOSDAQ, S&P 500, Nasdaq, SOX
- Breadth / Leadership: 상승종목 확산, 선도주 상대강도, 주도섹터 리더십
- Vol / Risk: VIX 등 변동성, 급락/갭, 상관관계 급등, 신용·유동성 스트레스
- Rates / Liquidity: 미국 2Y/10Y, 금리 변화와 기대
- FX: USD/KRW, DXY, USD/JPY 등 위험회피성 이동
- Commodities: WTI/Brent, Gold, 필요시 Copper
- Geopolitics: 전쟁·제재·해협·에너지 공급 차질 중 시장가격에 확인된 영향
- Cross-Asset: 주식·채권·달러·금·유가의 동조/비동조
- Leadership watchlist: 삼성전자, SK hynix, SK Square, Samsung SDI, KB Financial, Hyundai Motor, Samsung Fire, SK Innovation, Doosan Enerbility, NAVER, Samsung Biologics, TSM, AVGO 등

종목 자체의 단순 가격 변동보다 **시장 대비 상대강도와 breadth 기여도**를 우선한다.

## 세션 인식

매 실행 시 점검 시점이 한국장/한국장 전후/미국장 전후 중 어디에 해당하는지 인식한다.
- 한국장: KOSPI/KOSDAQ breadth와 국내 선도주를 우선
- 미국장: S&P/Nasdaq/SOX, 미국 선도주와 VIX를 우선
- 글로벌 전환구간: 금리/FX/유가 및 선물/주요 해외시장 변화를 우선

자동화 시간은 플랫폼의 반복 스케줄 제약을 따르며, 특정 시각의 체결/주문 감시를 보장하는 것으로 표현하지 않는다.

## Regime

기존 Market Regime Engine V1의 R1-R6 체계를 그대로 사용한다.
- MarketScore, SectorScore, StockScore, BuyStrength를 분리한다.
- 단일 지표 하나로 레짐을 확정하지 않는다.
- 복수 축의 일치 여부를 확인한다.
- 데이터 충돌/부족 시 레짐 변경을 확정하지 않는다.

## Alert Severity

### P0 — 즉시
시장 전체에 직접적인 충격을 주는 사건, 급격한 레짐 전환, 유가·금리·FX·지정학의 비정상적 충격.

### P1 — 중요
Breadth 붕괴/회복, 변동성 regime 변화, 지속적인 금리·FX·유가 방향 전환, 선도주 리더십 전환, 사전 정의한 관심조건의 접근/충족.

### P2 — 관찰
의미 있는 변화지만 아직 행동 트리거가 아닌 상태. 누적 변화가 충분할 때만 압축 보고한다.

일반적인 일중 등락과 기존 정보의 반복은 보고하지 않는다.

## Signal Gate

기본 확정 조건:
- 서로 독립적인 최소 2개 감시 축이 같은 방향으로 변화
- 또는 시장 전체에 직접 충격을 주는 명백한 단일 이벤트(P0)

뉴스/루머만으로 P1을 확정하지 않는다. 가능하면 가격·금리·FX·변동성 등 시장 데이터로 교차검증한다.

원인은 확인된 사실, 시장 데이터에서 확인된 현상, 아직 검증되지 않은 가설로 분리한다.

### False-alert suppression
- 동일한 데이터 변화가 반복되면 신규 알림으로 취급하지 않는다.
- 직전 알림에서 이미 보고된 trigger는 상태가 강화/약화되거나 무효화될 때만 재알림한다.
- 한 축의 작은 변화만으로 P1을 만들지 않는다.

## Compact State

매 실행에서 다음 상태를 유지한다.

REGIME | RISK | TREND | BREADTH | LEADERS | RATES | FX | OIL | GOLD | GEO | BUY_TRIGGER | DATA_QUALITY

각 항목은 가능한 한 GREEN / AMBER / RED / N/A로 저장한다. 숫자는 핵심 수치 1~2개만 남긴다.
다음 실행에서는 직전 state와 비교해 delta를 만든다.

## Buy-Timing Watch

자동 주문을 수행하지 않는다.

감시 대상은 다음 조건의 충족 / 근접 / 유지 / 무효화 여부다.

관심 신호 예:
- 급락 중 breadth/선도주 상대강도가 유지
- 변동성 급등 후 정상화
- 금리/FX/유가 충격 완화
- Trend가 유지된 채 가격 조정
- 주도주 리더십 유지 + risk/reward 개선

대기 신호 예:
- 지수 반등인데 breadth 악화
- 일부 주도주만 상승
- 유가 상승 + 금리 상승 + 달러 강세 재강화
- 변동성/신용 스트레스 지속 확대

## User Delivery

P0/P1만 기본적으로 사용자 대화에 전달한다.

ALERT: P0/P1
STATE: 레짐 / 리스크
DELTA: 핵심 변화 1~3개
EVIDENCE: 확인된 시장 데이터 + timestamp
LEADERS: 주도주 / breadth
MACRO: 금리 / FX / 유가 / 금
GEO: 확인된 지정학 영향
TRIGGER: 충족 / 근접 / 무효화
ACTION: 관찰 / 대기 / 추가검증

P2는 누적 변화가 의미 있을 때만 압축 전달한다.
변화가 없으면 사용자 메시지를 생성하지 않는다.

## Fail-Closed

- 데이터 누락/지연/충돌 → DATA GAP
- stale data를 현재값으로 표현하지 않는다.
- 임의 보간/수기 추정 금지
- 원인 불명 상태에서 인과관계를 단정하지 않는다.
- 정확성이 알림량보다 우선한다.
- 데이터 품질이 최소 기준에 미달하면 BUY_TRIGGER를 확정하지 않는다.

## Validation

운영 후 다음 성능지표를 누적한다.
- Alert precision / false alert rate
- missed event rate
- 중복 알림률
- 레짐 전환 선행시간
- 매수 관심조건 감지 lead time
- DATA GAP 발생률
- 평균 알림 길이 / 컨텍스트 절감량

백테스트와 실제 운용 평가는 동일한 trigger definition을 사용하고 사후적으로 기준을 바꾸지 않는다.

## Background automation

현재 활성화된 `시장상황 감시`는 daily flexible schedule, Asia/Seoul을 사용한다.
이 스케줄은 특정 분 단위의 intraday 감시를 보장하지 않는다.

차기 V2는 다음 구조를 목표로 한다:
Data Feed -> Event Detector -> State Store -> Alert Gate -> Chat Notification

외부 event-driven worker를 추가하더라도 V1의 state/output contract는 유지한다.

## Lessons learned

1. 반복적인 전체 시황 보고는 컨텍스트를 불필요하게 소비한다.
2. 시장 monitor는 report generator가 아니라 delta-first detector여야 한다.
3. 가격만으로는 부족하며 leadership, breadth, oil, rates, FX, geopolitics를 하나의 state vector에서 같이 봐야 한다.
4. P0/P1의 기준과 중복 억제 규칙이 없으면 자동화가 곧 noise generator가 된다.
5. 데이터 gap을 조용히 메우지 않는 fail-closed가 자본보존 관점에서 중요하다.
6. daily automation과 intraday event-driven monitoring은 별개 능력으로 취급해야 한다.

## Git

이 문서는 백그라운드 시장감시 Agent의 운영 계약(Operating Contract)으로 취급한다.
모델/자동화 규칙의 중요한 변경은 이 문서와 함께 Git에 기록한다.
