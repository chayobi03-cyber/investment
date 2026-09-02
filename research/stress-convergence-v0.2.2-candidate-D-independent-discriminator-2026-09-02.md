# Stress Convergence v0.2.2 Candidate D — R+I Persistence + Independent Discriminator

Date: 2026-09-02
Status: Candidate design — BACKTEST REQUIRED

## 1. 왜 Candidate D가 필요한가

앞선 실험에서 세 가지 문제가 확인됐다.

- Candidate A: 주식 하락(E)을 확인 조건으로 넣으면 2022년처럼 천천히 진행되는 금리 충격을 너무 늦게 잡는다.
- Candidate B: R+I를 2주 지속시키면 2022년을 약 8개월 앞서 잡을 수 있지만, 2013년과 2016년에 잘못된 경보(FP)가 발생한다.
- Candidate C: B의 경보 지속시간을 8주로 제한했지만 FP는 그대로이고, 2022년 조기경보를 놓쳤다.

따라서 다음 실험에서는 persistence의 길이를 다시 조절하지 않는다.

**핵심 문제는 '얼마나 오래 지속됐는가'가 아니라 '실제로 긴축 충격이 진행되고 있는가'를 구분하는 것이다.**

## 2. Candidate D의 아이디어

Candidate D는 다음 두 가지를 동시에 요구한다.

1. 금리와 물가가 동시에 나빠지고 있어야 한다. → `R + I persistence`
2. 장기금리뿐 아니라 정책금리에 가까운 단기금리도 의미 있게 재가격화되어야 한다. → `D2`

즉:

`R + I sustained for 2 consecutive weekly observations AND D2`

여기서 D2는 2년물 국채금리(2Y)의 독립적인 확인 신호다.

## 3. Frozen signal definitions

기존 신호는 그대로 유지한다.

- `R`: 10Y Treasury yield가 trailing 12-month low보다 +40bp 이상 높음.
- `I`: US CPI y/y가 3개월 전보다 +0.4 percentage point 이상 높음.
- `L`: unemployment rate가 trailing 12-month low보다 +0.3pp 이상 높음.
- `C`: HY OAS가 trailing 6-month low보다 +75bp 이상 높음.
- `V`: VIX >= 25가 5거래일 이상 지속.
- `E`: S&P 500이 trailing 60-trading-day high보다 10% 이상 하락.

기존 regime path도 변경하지 않는다.

- Credit/Liquidity: `C + V + (L OR E)`
- Growth/Exogenous: `L + (E OR V) + (C OR R)`

## 4. Candidate D의 신규 조건

### D2 — 2Y Treasury independent discriminator

`2Y Treasury yield >= trailing 12-month low + 60bp`

그리고 R+I persistence와 함께 평가한다.

### 최종 조건

`R + I sustained for 2 consecutive weekly observations + D2`

여기서 중요한 점은 **D2가 R의 복사본이 아니라 독립적인 단기금리 축이라는 것**이다.

10Y 금리 상승만으로는 taper/tightening과 crisis-producing tightening을 구분하기 어렵다. 2Y까지 크게 재가격화되면 시장이 장기 인플레이션뿐 아니라 정책금리 경로 자체를 강하게 재평가하고 있는지를 추가로 확인할 수 있다.

## 5. 왜 2Y인가

2Y Treasury yield는 연준 정책금리 기대에 상대적으로 민감하다.

따라서 다음과 같은 구분을 시험한다.

- 10Y만 상승 → 장기금리 상승일 수 있음
- 10Y + CPI 상승 → 인플레이션/기간 프리미엄 상승일 수 있음
- 10Y + CPI + 2Y의 의미 있는 상승 → 정책금리 경로까지 강하게 재가격화되는지 확인

Candidate D의 목적은 세 번째 상황을 추가로 확인하는 것이다.

## 6. Threshold를 왜 +60bp로 고정하는가

이번 실험에서는 결과를 보고 threshold를 바꾸지 않는다.

`+60bp / trailing 12-month low`를 사전에 고정하고 동일한 7개 benchmark에 적용한다.

이렇게 해야 Candidate D의 성능이 실제 discriminator 효과인지, benchmark에 맞춘 사후 tuning인지 구분할 수 있다.

## 7. 반드시 동일하게 비교할 benchmark

기존 benchmark와 완전히 동일하게 유지한다.

### Crisis

- 2000 dot-com
- 2008 GFC
- 2020 COVID
- 2022 rate shock

### False-positive

- 2013 taper tantrum
- 2016 China/energy stress
- Q4 2018 tightening selloff

평가 지표:

- FP
- FN
- Lead Time
- Trigger Frequency

이번 역시 event-window replay이므로 전체 일별 시계열에서의 population-level FP rate라고 해석하지 않는다.

## 8. Candidate D에서 확인할 핵심 질문

### 질문 1 — 2022년을 계속 잡는가?

Candidate B의 가장 큰 장점은 2022년을 놓치지 않았다는 것이다.

D2를 추가해도 2022 pre-peak detection이 유지되어야 한다.

### 질문 2 — 2013년 FP가 사라지는가?

B에서 발생한 FP를 D2가 제거한다면 독립 discriminator가 의미가 있다는 첫 번째 증거가 된다.

### 질문 3 — 2016년 FP가 사라지는가?

동일하게 2016년 FP 제거 여부를 확인한다.

### 질문 4 — 2018년의 정상 판정을 유지하는가?

새로운 조건이 과도하게 민감해져 기존의 정상 판정을 FP로 바꾸지 않는지 확인한다.

### 질문 5 — Lead Time을 지나치게 희생하지 않는가?

독립 confirmation을 추가하면서 신호가 너무 늦어지면 Candidate A의 문제가 다시 발생한다.

## 9. 성공 조건

Candidate D를 최종 v0.2.2 후보로 승격하려면 최소한 다음을 만족해야 한다.

1. **FN:** 4개 crisis benchmark에서 0/4 유지
2. **FP:** 기존 B의 2/3보다 명확하게 개선
3. **2022:** pre-peak lead 유지
4. **Trigger Frequency:** 장기 regime-state처럼 과도하게 지속되지 않을 것
5. 개선 효과가 D2 때문에 발생했다는 설명이 가능할 것

특히 `FN=0`만 보고 채택하지 않는다. FP가 그대로라면 D2는 discriminator로서 실패한 것이다.

## 10. Falsification 조건

다음 중 하나라도 발생하면 Candidate D를 기각한다.

- 2022년 FN 재발
- 2013/2016 FP가 그대로 유지
- 2Y 조건 때문에 신호가 지나치게 늦어짐
- D2가 사실상 R과 동일한 정보만 제공함
- benchmark 결과에 맞추기 위해 사후 threshold 조정이 필요함

## 11. 현재 판정

**Candidate D는 아직 PASS가 아니다.**

현재는 다음 단계의 검증 가능한 가설이다.

> `R+I persistence`의 민감도를 유지하면서 `2Y independent discriminator`를 추가하면, 2022년의 긴 선행시간을 유지하면서 2013/2016년의 false positive를 줄일 수 있는가?

이 질문을 동일한 7개 benchmark에서 직접 검증한다.

## 12. 현재 후보 비교

| Rule | FN | FP | 2022 Lead | 판단 |
|---|---:|---:|---:|---|
| A | 1/4 | 0/3 | 없음 | REJECT — 너무 늦음 |
| B | 0/4 | 2/3 | 약 8개월 | REJECT — 너무 permissive |
| C | 1/4 | 2/3 | 없음 | REJECT — duration 제한만으로 해결 안 됨 |
| D | 미검증 | 미검증 | 미검증 | **BACKTEST REQUIRED** |

## 13. Lesson Learned

Candidate C까지의 결과로 확인된 것은 명확하다.

**Persistence duration은 specificity 문제를 해결하지 못한다.**

따라서 다음 실험에서는 시간축을 계속 조정하지 않고, 서로 다른 시장정보를 제공하는 독립 discriminator를 추가한다.

이번 D 실험의 목적은 바로 그 가설을 검증하는 것이다.

## 14. 다음 작업

1. Candidate D의 모든 threshold를 freeze
2. 동일 7개 benchmark 재실행
3. FP / FN / Lead Time / Trigger Frequency 계산
4. B / C / D 직접 비교
5. Falsification
6. Lesson Learned
7. v0.2.2 채택 여부 결정
