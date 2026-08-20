"""Portfolio-level risk calculations."""

from __future__ import annotations

from typing import Mapping, Sequence

import numpy as np


def validate_weights(weights: Mapping[str, float], tolerance: float = 1e-9) -> None:
    if not weights:
        raise ValueError("weights must not be empty")
    if any(weight < 0 for weight in weights.values()):
        raise ValueError("weights must be non-negative")
    total = float(sum(weights.values()))
    if abs(total - 1.0) > tolerance:
        raise ValueError(f"weights must sum to 1.0; got {total}")


def portfolio_returns(asset_returns: Mapping[str, Sequence[float]], weights: Mapping[str, float]) -> np.ndarray:
    validate_weights(weights)
    missing = set(weights) - set(asset_returns)
    if missing:
        raise KeyError(f"missing returns for: {sorted(missing)}")
    lengths = {len(asset_returns[symbol]) for symbol in weights}
    if len(lengths) != 1:
        raise ValueError("all return series must have equal length")
    matrix = np.column_stack([np.asarray(asset_returns[symbol], dtype=float) for symbol in weights])
    weight_vector = np.asarray([weights[symbol] for symbol in weights], dtype=float)
    return matrix @ weight_vector


def portfolio_volatility(asset_returns: Mapping[str, Sequence[float]], weights: Mapping[str, float], periods_per_year: float = 12.0) -> float:
    validate_weights(weights)
    matrix = np.column_stack([np.asarray(asset_returns[symbol], dtype=float) for symbol in weights])
    covariance = np.cov(matrix, rowvar=False, ddof=1)
    weight_vector = np.asarray([weights[symbol] for symbol in weights], dtype=float)
    variance = float(weight_vector.T @ covariance @ weight_vector)
    return float(np.sqrt(max(variance, 0.0)) * np.sqrt(periods_per_year))


def stress_loss(weights: Mapping[str, float], asset_shocks: Mapping[str, float], capital: float) -> float:
    validate_weights(weights)
    missing = set(weights) - set(asset_shocks)
    if missing:
        raise KeyError(f"missing shocks for: {sorted(missing)}")
    portfolio_return = sum(weights[symbol] * asset_shocks[symbol] for symbol in weights)
    return float(capital * portfolio_return)
