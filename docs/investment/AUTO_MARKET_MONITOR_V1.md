# Auto Market Monitor V1

This layer operationalizes the frozen BUY Trigger Engine market-vector contract without changing the research rules.

## Automated checkpoints (Asia/Seoul)

- 08:30 pre-open
- 09:30 initial flow/trend check
- 10:30 active-buy permission check
- 14:30 close-risk recheck

GitHub Actions cron is UTC; the workflow uses 23:30, 00:30, 01:30 and 05:30 UTC respectively.

## Data posture

The monitor is a **permission/alert system only**. It never places orders. Missing critical data produces `DATA_BLOCKED` rather than an inferred value.

The first implementation uses `yfinance` as a transport for market observations (KOSPI, KOSPI leaders, S&P 500, Nasdaq, VIX, US 10Y proxy, Brent, DXY and USD/KRW). This is an acquisition adapter, not the canonical historical/PIT source for research. Replace it with the approved source adapters before using the generated observations for validated backtests.

## Outputs

`artifacts/auto_market_monitor/latest.json` contains:

- observation timestamp and checkpoint;
- raw observations and source timestamps;
- cluster states;
- B0/B1/B2/B3/B4 permission state;
- data-quality gate;
- human-readable action note;
- rule version.

The workflow uploads the JSON as a GitHub Actions artifact. No live trading credentials are required.

## Safety rules

1. A missing critical market variable blocks escalation.
2. Price alone can never generate B3/B4.
3. Geopolitical headlines are not scored directly; only observed market transmission is used.
4. This monitor does not claim accuracy or expected return until the PIT/OOS backtest contract is completed.
