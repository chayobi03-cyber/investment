import json
from pathlib import Path


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
