# 주식투자 방법론 벤치마크 v1 — 2026-10-16

- 작성일: 2026-10-16
- 상태: RESEARCH ONLY / 정책·매매규칙 미승격
- 저장소: investment
- 목적: 기존 자본보존 중심 투자 엔진에 추가할 방법론을 원전·학술 근거와 대조하고, 검증 우선순위 및 반증 실험을 등록한다.
- 안전 제어: 기존 M0–M3 게이트, PIT/Data QA, BUY_ALLOWED=false, EXECUTION_ALLOWED=false를 변경하지 않는다.

## 1. 결론

**전략을 많이 붙이는 것보다 서로 다른 정보가 실제로 추가 설명력을 주는지 검증하는 것이 우선이다.**

우선 연구할 조합은 다음과 같다.

1. **Cross-sectional momentum / relative strength**: 시장·섹터 대비 종목의 중기 강도와 지속성을 별도 신호로 측정한다.
2. **Quality / profitability + valuation discipline**: 수익성·현금흐름·재무건전성을 기업 기회 평가에 추가하고, 가치 함정과 과열 가격을 분리한다.
3. **Low-risk / volatility-aware sizing + factor look-through**: 수익률을 더 예측하기보다 동일한 위험예산에서 종목·섹터·테마 집중도를 통제한다.
4. **Time-series trend filter**: 200일선 또는 월간 10개월 이동평균을 후보 벤치마크로 쓰되, 유일한 매매 신호가 아니라 위험 노출 조절 후보로 검증한다.
5. **CAN SLIM / SEPA형 성장주 셋업**: 돌파·가격/거래량 구조는 진입 시점 보조 가설로만 시험한다. 고정 손절폭이나 저널/판매사의 주장 자체를 검증된 알파로 간주하지 않는다.
6. **Lump sum / fixed DCA / rule-based staging**: 종목 신호가 아닌 자금투입 정책의 대조군으로 비교한다.

이 후보들은 지금 바로 운용에 넣는 규칙이 아니다. 현재 저장소의 기존 프레임워크와 비교하는 사전등록 연구 후보들이다.

## 2. 저장소 기준선 및 적용 경계

저장소의 현재 연구 구조에는 이미 다음이 존재한다.

- 시장 상태: Trend / Breadth / Risk / Macro / Cross-Asset, R1–R6, stress override
- 종목 기회와 시장 허가의 분리: Stock/Opportunity와 Market/Risk/Permission을 분리한 뒤 행동을 결정
- 매수 단계: B0 No Buy, B1 Watch, B2 Scout, B3 Active Buy, B4 Aggressive Buy
- 종목 진입 점검: D/W/M 추세, 지지·저항, 최근 고점 대비 위치, 모멘텀, 상대강도
- PIT 데이터, 규칙 동결, Walk-forward OOS, 민감도·비용·반증 검사
- ETF look-through를 포함한 직접 종목·팩터·매크로 노출과 LOCKED 보유분의 위험 반영

따라서 신규 방법론은 기존 Market Regime Engine이나 Buy Trigger Engine을 대체하지 않는다. 각 방법론을 식별 가능한 독립 신호로 등록하고, 기존 엔진 대비 증분 효과를 테스트한다.

**선행 차단 사항:** GitHub Issue #27은 2026-10-16 확인 시 OPEN이다. 2026-10-12의 예시에서 5분 막대 변화율을 일간 변화율처럼 취급했고, 가장 최신인 USD/JPY 타임스탬프가 오래된 한국 지수 관측치를 가려 DATA_QUALITY=GREEN이 될 수 있었다. 이 결함과 회귀시험이 해결되기 전에는 시장 모니터의 Risk/Trend/Quality 필드를 매수 권한에 사용하지 않는다.

관련 내부 문서:
- [Market Regime Engine V1](../investment/MARKET_REGIME_ENGINE_V1.md)
- [Buy Trigger Engine V0.1](../investment/BUY_TRIGGER_ENGINE_V0.1_MARKET_VECTOR.md)
- [Market Decision Framework Research](MARKET_DECISION_FRAMEWORK_RESEARCH_2026-09-08.md)
- [Portfolio Factor Exposure Rule V1](../portfolio/PORTFOLIO_FACTOR_EXPOSURE_RULE_V1.md)
- [Issue #27 — Market monitor data integrity](https://github.com/chayobi03-cyber/investment/issues/27)

## 3. 방법론 비교표

| 방법론 | 무엇을 측정하는가 | 적합한 엔진 계층 | 기대 기여 | 대표 실패 모드 | 이번 판단 |
|---|---|---|---|---|---|
| Quality / profitability | 수익성, 현금흐름, 레버리지, 이익의 질, 투자 효율 | Stock Quality / Opportunity | 구조적 훼손·취약기업을 후보 단계에서 걸러냄 | 회계/공시 지연, 일회성 이익, 높은 가격에 대한 무감각, 가치 함정 | 우선 실험 |
| Value / valuation discipline | 이익·장부가·현금흐름 대비 가격, 밸류에이션 분포 | Opportunity의 가격 매력도 | 좋은 기업과 좋은 매수가격을 구분 | 경기민감 업종의 저PER 착시, 구조적 쇠퇴, 밸류 트랩 | Quality와 함께 실험 |
| Cross-sectional momentum / relative strength | 동일 기간 시장·섹터 및 유니버스 대비 성과, 순위 지속성 | Sector/Stock rank + D/W/M 진입 확인 | 리더십 지속과 종목 간 수익률 차이를 포착 | 급반전·혼잡·늦은 추격매수, 저유동성·수수료 | 최우선 실험 |
| Time-series momentum / trend | 해당 지수·종목 자체의 과거 수익률, 이동평균·기울기·낙폭 | Market Regime / Permission / risk scaling | 하락 추세 중 노출 확대를 억제할 수 있음 | 횡보장 whipsaw, 신호 지연, 급락 후 급반등 누락 | 위험 필터 후보 |
| Low-risk / volatility-aware sizing | 실현·하방 변동성, 상관·공분산, 스트레스 손실 | Portfolio Risk / Position Sizing | 같은 위험예산에서 위험 집중을 줄임 | 과거 변동성의 급변, 상관 붕괴, 저변동성의 밸류/섹터 편향 | 팩터 룩스루와 병행 |
| Multifactor | 가치·수익성·모멘텀·저위험 등 복수 신호의 독립 기여 | Stock rank + Portfolio construction | 단일 팩터 의존성 완화 가능 | 상관 신호 중복 가점, 불안정 가중치, 롱온리 분산 착시 | 팩터별 독립 시험 후 조합 |
| CAN SLIM / SEPA형 breakout | 성장/실적 + 상대강도 + 거래량/가격 베이스 + 시장 추세 | Entry Timing 보조 | 후보 선정과 실제 진입 시점을 구분 | 돌파 실패·갭 리스크·과최적화·고정 손절 룰의 부적합 | 보조 가설 |
| Lump sum / fixed DCA / staged deployment | 투자 가능 자금의 투입 시기와 속도 | Capital Deployment | 진입 시점 위험·후회 위험과 현금 기회비용의 절충 | DCA가 자동으로 초과수익을 주지 않음; 하락 중 무조건 매수 | 필수 대조군 |
| Macro / event transmission | 지정학→에너지→물가/Fed→금리→FX→신용/유동성 | Permission / Stress Override | 헤드라인보다 실제 시장 전이를 확인 | 원인 추정 과신, 동시상관을 인과로 오인, 출처 지연 | 기존 엔진 유지·품질 강화 |

## 4. 근거 수준과 해석

### 4.1 한국 주식시장 팩터 연구

Kim(2021)은 한국 주식시장에서 size, value, momentum, profitability, low-risk 팩터의 위험 프리미엄을 보고했다. 또한 원하지 않는 다른 팩터에 대한 음의 노출을 줄였을 때 결과가 개선됐다고 보고했다. 반면 롱온리 멀티팩터 포트폴리오가 큰 분산효과를 보장하지는 않았다고 설명한다.

**시스템 적용:** 종목 점수에 팩터 점수를 무조건 합산하지 않는다. 각 팩터를 별도 산출하고, 종목 및 ETF look-through 기준으로 원치 않는 노출과 공통 집중도를 측정한다. 논문 결과는 미래 수익 보장이나 현재 종목 매수 허가가 아니다.

### 4.2 Value / Profitability / Investment

Fama–French 5-factor 연구는 size, value, profitability, investment 패턴을 포함한 모델이 기존 3-factor 모델보다 평균 주식수익률 패턴을 더 잘 설명한다고 보고한다. 다만 이 결과는 개별 한국 종목의 매수 규칙이나 현재 가중치를 직접 정해주지 않는다.

**시스템 적용:** 공시의 발표 가능 시점(available_at)을 엄격히 반영하고, ROE 하나만으로 수익성을 대리하지 않는다. 현금흐름, 레버리지, 일회성 요인 및 자본투자 정책을 함께 검토한다. 가치와 품질은 진입 허가가 아닌 기업/가격의 기회 평가 계층에 둔다.

### 4.3 Cross-sectional momentum

Jegadeesh–Titman(1993)은 과거 3–12개월 성과가 좋았던 종목을 매수하고 약했던 종목을 매도하는 전략에서 유의한 수익 패턴을 보고했다. 이후 문헌도 모멘텀 효과를 폭넓게 조사했으나, 모멘텀의 존재가 모든 시장·기간·비용 조건에서 같은 결과를 보장하지는 않는다.

**시스템 적용:** 종목의 20/60/120거래일 성과, 시장 대비 RS, 섹터 대비 RS를 서로 같은 종료 시각과 기간으로 산출한다. 가능하면 6–12개월 모멘텀도 독립 후보로 시험한다. 최근 하루 반등이나 과매도 지표만으로 중기 모멘텀 회복을 선언하지 않는다.

### 4.4 Time-series momentum / trend following

Moskowitz–Ooi–Pedersen(2012)은 여러 자산군의 선물·선도 계약에서 자체 과거 1–12개월 수익률의 지속성을 보고했다. Hurst–Ooi–Pedersen(2017)은 장기 역사 자료를 이용한 추세추종 연구를 발표했다. 이는 추세 신호를 벤치마크할 근거지만, 다자산 선물 전략의 결과를 한국 개별주 롱온리 계좌에 그대로 외삽할 수는 없다.

**시스템 적용:** 200일 SMA 또는 월간 10개월 SMA를 단순 대조군으로 두고, 시장 레짐 및 현금비중 조절에 대한 증분 효과를 검증한다. 매매 필터 하나가 구조적 데이터 결함을 덮거나, 검증되지 않은 종목별 강제매도를 발생시키지 않도록 분리한다.

### 4.5 성장주·돌파형 진입법

IBD가 공개한 CAN SLIM/투자 방법론 소개는 펀더멘털, 기술적 분석, 시장 방향, 위험관리의 결합을 강조한다. 이 방식은 현재 시스템의 실적/품질 + 시장 허가 + D/W/M + 가격·거래량 진입 확인과 기능적으로 겹친다.

**시스템 적용:** 새로운 독립 스코어를 즉시 만들지 않고, 가격 베이스/돌파 및 거래량 확인이 기존 D/W/M 상대강도 대비 진입 실패율, 추격매수, MAE를 개선하는지 확인한다. 판매사 또는 실전 트레이더의 성과 주장을 독립적인 학술 검증으로 취급하지 않는다. 단일 7–8% 고정 손절폭을 시스템 기본 규칙으로 채택하지 않는다.

### 4.6 Lump sum vs DCA

Vanguard의 1976–2022 시장 분석은 여러 시장의 1년 롤링 기간에서 일시투자가 분할투자보다 대략 61.6–73.7% 더 높은 결과를 냈다고 보고했다. 이는 시장의 기대 위험 프리미엄에 더 오래 노출되는 현상과 일치한다. 그러나 DCA는 초기 시점의 손실과 후회 위험을 낮추려는 목적에 유용할 수 있으며, 위 결과는 특정 집중 종목의 일일 분할매수 규칙을 직접 검증한 결과가 아니다.

**시스템 적용:** DCA를 초과수익 전략으로 가정하지 않는다. 자금투입 규칙은 일시투자, 고정 DCA, 시장/위험 게이트를 반영한 단계적 투입을 별도 대조군으로 비교한다. 모든 분할 매수가 예정됐다는 이유로 데이터/시장 허가 게이트를 우회하지 않는다.

### 4.7 백테스트 선택편향

Bailey–López de Prado의 Deflated Sharpe Ratio 연구는 다중 실험·전략 선택과 비정규 수익률이 백테스트 성과를 부풀릴 수 있음을 다룬다.

**시스템 적용:** 실험한 모든 규칙·파라미터 조합을 기록하고, OOS 결과를 본 뒤 규칙을 바꾸면 해당 기간을 더 이상 독립 OOS로 부르지 않는다. DSR/PBO는 유용한 진단 도구이지만 한 개 숫자를 자동 합격/불합격 기준으로 삼지 않는다.

## 5. 권장 의사결정 구조

정보의 역할을 분리한다.

1. **Data eligibility:** PIT, 시세 기준시각, 가격 조정, 거래소 세션, 데이터 신선도, 출처 충돌을 검증한다. 불일치는 fail-closed.
2. **Company / Stock Opportunity:** Quality, profitability, valuation, earnings revisions, cash-flow and balance-sheet integrity를 평가한다.
3. **Sector / Cross-sectional strength:** 섹터 breadth, 시장/섹터 대비 상대강도, 모멘텀의 지속성을 측정한다.
4. **Market Permission:** R1–R6, 스트레스 클러스터, 금리/FX/에너지/신용 전이, 시장 추세와 breadth를 통해 허가 수준을 결정한다.
5. **Entry Setup:** D/W/M 구조, 지지·저항, 최근 고점과의 거리, 돌파/거래량, 진입 가격의 손익비를 별도 평가한다.
6. **Portfolio Risk / Sizing:** 직접 보유 + ETF look-through + 공통 팩터/테마 + 상관 + stress loss + 유동성 + LOCKED 제약을 반영한다.
7. **Capital Deployment:** 일시투자, 고정 DCA, 단계적 매수는 별도의 투입 정책으로 시험하되 B0/Data QA 실패 시 모두 중지한다.
8. **HOTL / outcome ledger:** 관측 당시 정보, 선택한 규칙, 허가/거절 이유, 실제 체결, 이후 수익/MAE/MFE, 반증 여부를 누적한다.

이 구조는 Quality/Trend/Entry 신호를 같은 점수에 중복 합산하지 않는다. 시장 허가 실패는 높은 종목점수로 상쇄할 수 없다. LOCKED 포지션은 위험 계산에는 포함하지만 자동 매도 대상에는 넣지 않는다.

## 6. 사전등록 벤치마크 실험

### 6.1 비교군

| ID | 전략/모델 | 목적 |
|---|---|---|
| B0 | 현재 규칙 기반 엔진(고정된 기존 버전) | 기준 성능 |
| B1 | KOSPI/KOSPI 200 buy-and-hold 및 현행 포트폴리오 | 시장·운용 기준선 |
| B2 | 정기 DCA | 단순 분할투입 대조군 |
| B3 | 200일 SMA 또는 월간 10개월 SMA trend filter | 추세 기반 위험 축소 효과 |
| C1 | B0 + Quality/Profitability | 기업 품질 신호의 증분 가치 |
| C2 | B0 + Value/valuation discipline | 가격 매력도 신호의 증분 가치 |
| C3 | B0 + Cross-sectional Momentum/RS | 모멘텀 신호의 증분 가치 |
| C4 | B0 + Low-risk / volatility-aware sizing | 위험 기반 사이징 효과 |
| C5 | Quality + Value + Momentum + Low-risk 조합 | 팩터 상호작용·중복 위험 |
| C6 | B0 + breakout/volume setup | 진입 셋업의 증분 효과 |
| C7 | risk-gated staged deployment | 자금투입 정책의 위험/기회비용 비교 |

단일 신호 실험을 먼저 수행하고, 통과한 신호만 조합한다. 다중 신호를 한 번에 추가해 성과가 바뀌면 무엇이 원인인지 특정할 수 없기 때문이다. B0는 코드·설정 버전과 데이터 컷오프를 고정한다.

### 6.2 데이터·검증 조건

- 유니버스: 현행 고정 KRX 종목군과 별도 유동성 기준 유니버스를 분리한다. 생존편향 방지를 위해 상장폐지·거래정지·유니버스 변경 자료를 확보한다.
- PIT: 모든 펀더멘털/공시 신호는 실제 공개 가능 시각 기준으로 lag를 적용한다. 사후 수정값을 과거 의사결정에 넣지 않는다.
- 가격: 분할·배당 등 기업행동을 일관되게 반영하고, 체결 가능한 거래일/가격으로 실행을 모의한다.
- 실행비용: 수수료, 세금, 스프레드/슬리피지, 유동성 및 거래 빈도를 반영한다.
- 계좌: 다계좌 합산과 ETF look-through를 사용하되 계좌 요약액을 실물 보유분에 중복 합산하지 않는다. LOCKED 자산은 별도 제약으로 보존한다.
- 검증: 개발 구간 → freeze → walk-forward OOS. 라벨 기간 중첩 시 purge/embargo를 고려한다. 시장 국면별·연도별·유니버스별 결과를 따로 낸다.
- 파라미터: 가중치와 임계값을 OOS 결과에 맞춰 사후 최적화하지 않는다. 다중 실험 수를 기록하고, 필요 시 PBO/DSR 및 다중검정 진단을 사용한다.
- 진입 시점: 종목 기준 D/W/M은 시장/섹터 상대강도와 동일 시점 데이터에 대해 계산한다. 최근 하루의 저점/반등 또는 RSI만으로 reversal을 확정하지 않는다.

### 6.3 필수 평가 지표

| 영역 | 지표 |
|---|---|
| 자본보존 | MDD, 95% CVaR/Expected Shortfall, 최악의 forward return, 스트레스 손실, 생존 제약 위반 |
| 회복 | 고점 회복기간, 최대 회복기간, 손실 지속시간 |
| 신호 품질 | horizon별 평균/중앙값 forward return, Rank IC/monotonicity, false positive/negative, lead time |
| 거래 효율 | turnover, 거래횟수, 수수료/세금/슬리피지 후 성과, 유동성 용량 |
| 진입 품질 | MAE/MFE, 목표 기간 내 손실 빈도, 돌파 실패율, 추격매수 빈도 |
| 안정성 | 연도/레짐/섹터별 성과, 파라미터 민감도, 유니버스·시장 간 재현성 |
| 자금투입 | 투입 속도, 현금 기회비용, 초기 손실 확률/깊이/지속기간 |

CAGR은 보고하지만 일차적인 최적화 목표로 사용하지 않는다. 첫 번째 탈락 조건은 생존 제약 악화 또는 데이터 무결성 실패다.

## 7. 승격 게이트

- **G0 — Evidence-ready:** 데이터 계약, PIT, corporate action, 출처/시간대, 비용·체결 가정이 확인됨.
- **G1 — Baseline parity:** 기존 B0 및 단순 벤치마크의 결과가 재현됨.
- **G2 — Incremental value:** 신호 추가가 사전 정의된 지표에서 B0보다 증분 효과를 보이며, tail risk나 MDD를 부당하게 악화시키지 않음.
- **G3 — Robustness:** Walk-forward OOS, 국면별, 비용·파라미터 민감도 및 반증 검사를 통과.
- **G4 — Paper / shadow:** 실시간 관측에서 데이터·신호·행동 기록의 정확성을 확인.
- **G5 — Promotion review:** 독립 검토 후 별도 승인. 현재 문서는 G5를 승인하지 않는다.

수치 합격 기준은 실험 전에 별도의 test contract에 등록한다. 결과를 본 뒤 기준을 고치는 것을 금지한다. 어떤 신규 방법론도 Issue #27 및 M1 Data Integrity의 선행 차단을 무시할 수 없다.

## 8. 이번 회차 Lesson Learned

1. 투자 방법론 추가의 단위는 “새로운 인기 전략”이 아니라 기존 시스템에 대한 **검증 가능한 증분 가설**이어야 한다.
2. 기업 품질, 팩터 모멘텀, 시장 추세, 진입 셋업, 사이징, 투입 속도는 서로 다른 역할이다. 역할을 분리하지 않으면 동일한 정보를 여러 번 가점하거나 현금/리스크 제한을 숨길 수 있다.
3. 한국 주식 팩터 결과는 local validation을 설계하는 근거이지, 향후 프리미엄을 보장하거나 현재 시장에서 BUY를 허용하는 근거가 아니다.
4. DCA는 진입 타이밍 위험 및 행동적 부담을 낮추는 투입 정책으로 평가해야 하며, 자동 초과수익 규칙으로 간주하지 않는다.
5. 데이터 정확성의 실패는 어떤 투자 전략보다 먼저 처리해야 할 차단 조건이다.

### 규칙 변경 여부

- 이번 회차에서 LIVE 룰 및 수치 임계값은 변경하지 않는다.
- 신규 실험 후보만 연구 레지스트리에 추가한다.
- Issue #27 해결, M1 GREEN, PIT 데이터와 실행비용 검증이 충족된 후에만 추가 신호의 승격을 검토한다.

## 9. 참고문헌 및 원전

1. Saejoon Kim (2021), “Enhanced factor investing in the Korean stock market,” Pacific-Basin Finance Journal 67, 101558. https://doi.org/10.1016/j.pacfin.2021.101558
2. Eugene F. Fama and Kenneth R. French (2015), “A five-factor asset pricing model,” Journal of Financial Economics 116(1), 1–22. https://doi.org/10.1016/j.jfineco.2014.10.010
3. Narasimhan Jegadeesh and Sheridan Titman (1993), “Returns to Buying Winners and Selling Losers: Implications for Stock Market Efficiency,” Journal of Finance. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x
4. Tobias J. Moskowitz, Yao Hua Ooi and Lasse H. Pedersen (2012), “Time series momentum,” Journal of Financial Economics 104(2), 228–250. https://doi.org/10.1016/j.jfineco.2011.11.003
5. Brian Hurst, Yao Hua Ooi and Lasse H. Pedersen (2017), “A Century of Evidence on Trend-Following Investing.” https://www.aqr.com/Insights/Research/Journal-Article/A-Century-of-Evidence-on-Trend-Following-Investing
6. Investor’s Business Daily, “Introducing The Four Pillars Of The IBD Methodology For Stock Market Success.” https://www.investors.com/how-to-invest/investors-corner/stock-market-investing-ibd-methodology/
7. Vanguard Research, “Cost averaging: Invest now or temporarily hold your cash?” https://corporate.vanguard.com/content/dam/corp/research/pdf/cost_averaging_invest_now_or_temporarily_hold_your_cash.pdf
8. David H. Bailey and Marcos López de Prado (2014), “The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting, and Non-Normality,” Journal of Portfolio Management 40(5), 94–107. https://doi.org/10.3905/jpm.2014.40.5.094

---

**Final status:** benchmark framework recorded; research-only; no new BUY signal, no execution permission, no rule promotion.
