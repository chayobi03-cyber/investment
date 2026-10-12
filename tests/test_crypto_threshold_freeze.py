import json
import math
from pathlib import Path

import pandas as pd

from src.investment_pipeline import crypto_entry as ce
from src.investment_pipeline import crypto_risk as cr


CONFIG = Path("config/crypto_market_regime_entry_v0.2.json")


def test_v02_threshold_contract_is_frozen():
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))

    assert cfg["version"] == "0.2"
    assert cfg["market_score"]["weights"] == {
        "trend": 0.2,
        "flow_institutional": 0.2,
        "macro_liquidity": 0.2,
        "breadth_relative_strength": 0.15,
        "derivatives": 0.1,
        "volatility_risk": 0.1,
        "regulation_market_structure": 0.05,
    }
    assert cfg["pullback_zones"]["reference_high_days"] == 60
    assert cfg["pullback_zones"]["exclude_current_bar"] is True
    assert cfg["stabilization"]["return_3d_gt"] == 0
    assert cfg["stabilization"]["green_closes_last_3_min"] == 2
    assert cfg["breakout"]["close_buffer"] == 0.005
    assert cfg["breakout"]["volume_ratio_20d_min"] == 1.2
    assert cfg["episode"]["cooldown_bars"] == 5
    assert cfg["permission_layer"]["threshold_mutation_allowed"] is False
    assert cfg["deployment"]["buy_allowed"] is False
    assert cfg["deployment"]["automatic_orders"] is False


# Code-vs-config: the constants the code actually runs on must equal the frozen
# v0.2 config. Regime upper bounds are left out on purpose (the config uses
# closed 74.999999-style bounds, crypto_risk.REGIMES uses half-open intervals).


def _cfg() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def test_crypto_entry_constants_match_config():
    cfg = _cfg()
    assert ce.V02_COOLDOWN_BARS == cfg["episode"]["cooldown_bars"]
    assert ce.V02_BREAKOUT_BUFFER == cfg["breakout"]["close_buffer"]
    assert ce.V02_BREAKOUT_VOLUME_RATIO == cfg["breakout"]["volume_ratio_20d_min"]
    assert ce.V02_STABILIZATION_GREEN_MIN == cfg["stabilization"]["green_closes_last_3_min"]

    zones = cfg["pullback_zones"]
    assert ce.V02_Z1_MAX_DD == zones["Z0"]["min_drawdown"] == zones["Z1"]["max_drawdown"]
    assert ce.V02_Z2_MAX_DD == zones["Z1"]["min_drawdown"] == zones["Z2"]["max_drawdown"]
    assert ce.V02_Z3_MAX_DD == zones["Z2"]["min_drawdown"] == zones["Z3"]["max_drawdown"]


def test_crypto_entry_zone_literals_are_frozen():
    # Exact literal values, including bit-identity of the derived multipliers.
    assert (ce.V02_Z1_MAX_DD, ce.V02_Z2_MAX_DD, ce.V02_Z3_MAX_DD) == (-0.05, -0.08, -0.12)
    assert ce.V02_NO_CHASE_DD == -0.02
    assert (ce.V02_Z1_UPPER_MULT, ce.V02_Z1_LOWER_MULT, ce.V02_Z2_LOWER_MULT) == (0.95, 0.92, 0.88)
    assert (ce.V02_Z1_UPPER_MULT).hex() == (0.95).hex()
    assert (ce.V02_Z1_LOWER_MULT).hex() == (0.92).hex()
    assert (ce.V02_Z2_LOWER_MULT).hex() == (0.88).hex()
    assert (1.0 + ce.V02_BREAKOUT_BUFFER).hex() == (1.005).hex()


def test_assign_zones_boundaries():
    dd = pd.Series([
        0.0, -0.02, math.nextafter(-0.05, 0.0), -0.05, math.nextafter(-0.08, 0.0),
        -0.08, math.nextafter(-0.12, 0.0), -0.12, -0.5, float("nan"),
    ])
    assert ce.assign_zones(dd).tolist() == [
        "Z0", "Z0", "Z0", "Z1", "Z1", "Z2", "Z2", "Z3", "Z3", "UNKNOWN",
    ]


def test_crypto_risk_constants_match_config():
    cfg = _cfg()
    assert cr.DEFAULT_WEIGHTS == cfg["market_score"]["weights"]
    assert list(cr.DEFAULT_WEIGHTS) == list(cfg["market_score"]["weights"])
    assert cr.EXPOSURE_MULTIPLIER == {
        state: spec["exposure_multiplier"] for state, spec in cfg["buy_states"].items()
    }

    gates = cfg["market_score"]["gates"]
    assert cr.MARKET_GATE_GREEN_MIN == gates["green_min"] == 70
    assert cr.MARKET_GATE_YELLOW_MIN == gates["yellow_min"] == gates["red_max_exclusive"] == 55
    # Behaviour at and just below each cut-off.
    assert cr.market_gate_from_score(gates["green_min"]) == "GREEN"
    assert cr.market_gate_from_score(gates["green_min"] - 1e-6) == "YELLOW"
    assert cr.market_gate_from_score(gates["yellow_min"]) == "YELLOW"
    assert cr.market_gate_from_score(gates["yellow_min"] - 1e-6) == "RED"
