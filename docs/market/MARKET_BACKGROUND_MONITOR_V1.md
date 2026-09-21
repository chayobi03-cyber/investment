# Market Background Monitor V1

## Purpose

Run the market-condition check as a background automation so the main investment conversation only receives material state changes. The monitor is an observation/signal layer, not an autonomous trade executor.

## Core design

`raw data -> state -> delta -> trigger -> notification`

The monitor should prefer a compact state transition over repeating the full market report.

### State dimensions

- Trend
- Breadth / leadership
- Volatility / risk
- Rates / liquidity
- Cross-asset
- Geopolitical risk
- Market regime (R1-R6)

### Cross-asset inputs

- Korea / US major indices and volatility
- Leading stocks / semiconductors and breadth
- Oil
- US 2Y / 10Y and rate expectations
- USD/KRW and major FX
- Gold / USD
- Material geopolitical or war-related market shocks
- Credit / liquidity stress

## Notification policy

Normal condition:

`NO MATERIAL CHANGE`

Only send a detailed notification when one or more of these occurs:

- regime transition
- abnormal market move
- oil/rates/FX cross-asset shock
- leadership/breadth deterioration
- material geopolitical repricing
- predefined watch-entry condition is met
- important data conflict or missingness

## Output contract

Maximum 8 lines when a notification is required:

`STATE: current regime/risk state`
`DELTA: 1-3 material changes since prior run`
`DRIVERS: confirmed data / causes`
`LEADERS: leaders and breadth`
`MACRO: oil / rates / FX`
`GEO: material geopolitical change`
`TRIGGER: watch condition status`
`ACTION: observe / wait / verify`

Unknown or conflicting data must be reported as `DATA GAP`, not imputed.

## Context-saving rule

Do not repeat unchanged historical context. Preserve only the minimum state required to detect the next material delta.

## Safety / decision boundary

The monitor reports facts, signals, uncertainty, and watch conditions. It does not autonomously place orders or convert a signal into an execution instruction.

## Background automation

Created automation: `시장상황 감시`
Automation ID: `6ab08886d13081918f49ce8b04bde8f1`
Cadence: daily, flexible schedule
Timezone: `Asia/Seoul`

## Lessons learned

1. A recurring market report consumes conversation context unnecessarily.
2. The monitor should be delta-first and exception-driven.
3. Price alone is insufficient; leadership, breadth, oil, rates, FX and geopolitical regime shifts belong in the same state vector.
4. Data gaps must fail closed rather than silently becoming assumptions.

## Future extension

For intraday monitoring, the current task-automation cadence is insufficient because recurring automations support daily/weekly/monthly schedules rather than arbitrary hourly/custom schedules. An event-driven or external scheduler can be added later without changing the state/output contract.
