"""Deterministic 4-portfolio x 3-capital-tier risk-engine harness.

This is an engine-validation harness using synthetic returns. It is not a
backtest and must not be interpreted as an investment performance result.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.risk_engine.core import annualized_volatility, cagr, max_drawdown
from src.risk_engine.portfolio import portfolio_returns

ROOT = Path(__file__).resolve().parents[1]

CAPITAL_TIERS = {"T1": 10_000_000, "T2": 50_000_000, "T3": 100_000_000}
PORTFOLIOS = {
    "P0": {"Equity": 1.00},
    "P1": {"Equity": 0.50, "Bond": 0.25, "Gold": 0.10, "Cash": 0.15},
    "P2": {"Equity": 0.60, "Bond": 0.20, "Gold": 0.10, "Cash": 0.10},
    "P3": {"Equity": 0.40, "Bond": 0.30, "Gold": 0.15, "Cash": 0.15},
}


def main() -> None:
    fixture = json.loads((ROOT / "fixtures/risk_engine_returns.json").read_text())
    returns = fixture["returns"]
    periods_per_year = float(fixture["periods_per_year"])
    rows = []

    for portfolio_id, weights in PORTFOLIOS.items():
        asset_returns = {name: returns[name] for name in weights}
        p_returns = portfolio_returns(asset_returns, weights)
        equity_curve = [1.0]
        for ret in p_returns:
            equity_curve.append(equity_curve[-1] * (1.0 + float(ret)))
        rows_for_portfolio = {
            "portfolio": portfolio_id,
            "cagr": cagr(equity_curve[0], equity_curve[-1], periods_per_year, len(p_returns)),
            "volatility": annualized_volatility(p_returns, periods_per_year),
            "max_drawdown": max_drawdown(equity_curve),
            "periods": len(p_returns),
        }
        for tier_id, capital in CAPITAL_TIERS.items():
            rows.append({
                "case_id": f"{portfolio_id}-{tier_id}",
                "capital_tier": tier_id,
                "capital_krw": capital,
                **rows_for_portfolio,
            })

    output = {"type": "risk_engine_fixture_harness", "cases": rows, "case_count": len(rows)}
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
