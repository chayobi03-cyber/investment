"""Deterministic stress matrix for the initial capital-preservation research.

Stress results are mechanical KRW loss calculations against defined shocks;
no market prediction or strategy performance claim is made here.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.risk_engine.portfolio import stress_loss

ROOT = Path(__file__).resolve().parents[1]
CAPITAL_TIERS = {"T1": 10_000_000, "T2": 50_000_000, "T3": 100_000_000}
PORTFOLIOS = {
    "P0": {"Equity": 1.00},
    "P1": {"Equity": 0.50, "Bond": 0.25, "Gold": 0.10, "Cash": 0.15},
    "P2": {"Equity": 0.60, "Bond": 0.20, "Gold": 0.10, "Cash": 0.10},
    "P3": {"Equity": 0.40, "Bond": 0.30, "Gold": 0.15, "Cash": 0.15},
}
SCENARIOS = {
    "equity_down_10": {"Equity": -0.10, "Bond": 0.00, "Gold": 0.00, "Cash": 0.00},
    "equity_down_20": {"Equity": -0.20, "Bond": 0.00, "Gold": 0.00, "Cash": 0.00},
    "equity_down_30": {"Equity": -0.30, "Bond": 0.00, "Gold": 0.00, "Cash": 0.00},
    "equity_down_50": {"Equity": -0.50, "Bond": 0.00, "Gold": 0.00, "Cash": 0.00},
    "broad_risk_off": {"Equity": -0.30, "Bond": -0.10, "Gold": 0.05, "Cash": 0.00},
}


def main() -> None:
    rows = []
    for portfolio_id, weights in PORTFOLIOS.items():
        for tier_id, capital in CAPITAL_TIERS.items():
            for scenario_id, shocks in SCENARIOS.items():
                applicable = {asset: shocks.get(asset, 0.0) for asset in weights}
                loss = stress_loss(weights, applicable, capital)
                rows.append({
                    "case_id": f"{portfolio_id}-{tier_id}",
                    "portfolio": portfolio_id,
                    "capital_tier": tier_id,
                    "scenario": scenario_id,
                    "capital_krw": capital,
                    "loss_krw": loss,
                    "loss_pct": loss / capital,
                })
    output = {
        "type": "stress_matrix",
        "scenario_count": len(SCENARIOS),
        "case_count": len(CAPITAL_TIERS) * len(PORTFOLIOS),
        "result_count": len(rows),
        "results": rows,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
