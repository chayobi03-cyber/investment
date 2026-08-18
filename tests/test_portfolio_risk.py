import numpy as np
import pytest

from src.risk_engine.portfolio import (
    portfolio_returns,
    portfolio_volatility,
    stress_loss,
    validate_weights,
)


def test_weights_must_sum_to_one():
    validate_weights({"SPY": 0.5, "IEF": 0.5})
    with pytest.raises(ValueError):
        validate_weights({"SPY": 0.7, "IEF": 0.2})


def test_portfolio_returns_are_weighted():
    result = portfolio_returns(
        {"A": [0.10, 0.00], "B": [0.00, 0.10]},
        {"A": 0.5, "B": 0.5},
    )
    np.testing.assert_allclose(result, [0.05, 0.05])


def test_stress_loss_reports_negative_krw_loss():
    loss = stress_loss(
        {"Equity": 0.50, "Bond": 0.25, "Gold": 0.10, "Cash": 0.15},
        {"Equity": -0.30, "Bond": -0.10, "Gold": -0.05, "Cash": 0.0},
        10_000_000,
    )
    assert loss == pytest.approx(-1_800_000)


def test_portfolio_volatility_is_positive():
    vol = portfolio_volatility(
        {"A": [0.02, -0.01, 0.01], "B": [0.01, 0.00, -0.01]},
        {"A": 0.5, "B": 0.5},
    )
    assert vol > 0
