"""Minimal deterministic portfolio-risk calculations for research experiments.

This module intentionally contains calculation primitives only. It does not fetch
market data and it does not constitute trading advice.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class RiskMetrics:
    cagr: float
    volatility: float
    max_drawdown: float
    recovery_periods: int


def max_drawdown(equity_curve: Sequence[float]) -> float:
    values = np.asarray(equity_curve, dtype=float)
    if values.size == 0 or np.any(values <= 0):
        raise ValueError("equity_curve must contain positive values")
    running_max = np.maximum.accumulate(values)
    drawdowns = values / running_max - 1.0
    return float(drawdowns.min())


def cagr(start_value: float, end_value: float, periods_per_year: float, periods: int) -> float:
    if start_value <= 0 or end_value <= 0 or periods <= 0:
        raise ValueError("values must be positive and periods must be > 0")
    years = periods / periods_per_year
    return float((end_value / start_value) ** (1.0 / years) - 1.0)


def annualized_volatility(period_returns: Sequence[float], periods_per_year: float) -> float:
    returns = np.asarray(period_returns, dtype=float)
    if returns.size < 2:
        raise ValueError("at least two returns are required")
    return float(np.std(returns, ddof=1) * np.sqrt(periods_per_year))
