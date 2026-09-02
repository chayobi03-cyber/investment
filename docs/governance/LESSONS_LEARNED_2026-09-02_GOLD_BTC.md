# Lessons Learned — 2026-09-02 Gold / Bitcoin Integration

## Lesson

Gold와 Bitcoin을 Stress Convergence에 추가할 때 **자산의 통상적인 서사(safe haven, inflation hedge)를 그대로 신호 정의에 사용하면 안 된다.** 같은 가격 방향이라도 금리·달러·유동성 조건에 따라 의미가 달라진다.

### Operational rule added

> 어떤 자산도 `safe haven` 또는 `risk-off`로 선분류하지 않는다. 먼저 macro regime을 구분하고, 해당 자산 신호가 기존 rates/credit/Korea stress 신호에 추가적인 설명력과 lead time을 제공하는지 백테스트로 검증한다.

## Model consequence

- Gold: macro/geopolitical/fiscal confirmation variable
- Bitcoin: liquidity/risk-appetite/financial-conditions confirmation variable
- Gold/BTC weight increase: backtest 이후에만 허용
- Gold/BTC 단독 신호로 crisis escalation 금지
- `Gold ↓ + BTC ↓ + USD ↑ + yields ↑ + credit spreads ↑`는 safe-haven failure가 아니라 forced-liquidity 가능성을 우선 검토

## Validation requirement

기존 Korea stress benchmark에서 다음 네 모델을 비교한다.

- Baseline
- + Gold
- + Bitcoin
- + Gold + Bitcoin

평가: FP/FN, precision/recall, lead time, warning persistence, redundancy, incremental explanatory power.

## Git decision

이번 변경은 모델 구조에 영향을 주는 영속적 연구 artifact이므로 Git에 보존한다.
