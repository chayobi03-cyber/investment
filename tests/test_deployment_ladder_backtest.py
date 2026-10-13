import numpy as np
import pandas as pd

from research.scripts.deployment_ladder_backtest import HORIZON, simulate, target_path

FLAT_DD = np.zeros(12)
ALL_UP = np.ones(12, dtype=bool)


def test_drawdown_only_ladder_stalls_at_stage0_without_a_drawdown():
    assert target_path("LADDER", FLAT_DD, ALL_UP).max() == 0.20


def test_hybrid_time_floor_reaches_full_deployment_on_schedule():
    tgt = target_path("HYBRID6_STAB", FLAT_DD, ALL_UP)
    assert tgt[0] == 0.20
    assert tgt[4] < 1.0
    assert tgt[5] == 1.0


def test_hybrid_accelerates_when_drawdown_levels_are_touched():
    dd = np.array([0.0, -0.12, -0.16, -0.16, -0.16, -0.16])
    tgt = target_path("HYBRID12", dd, np.ones(6, dtype=bool))
    assert tgt[1] == 0.40
    assert tgt[2] == 0.60


def test_stabilized_stage_waits_for_an_up_month():
    dd = np.array([0.0, -0.21, -0.25, -0.22])
    up = np.array([True, False, False, True])
    tgt = target_path("LADDER_STAB", dd, up)
    assert list(tgt) == [0.20, 0.20, 0.20, 0.80]


def test_scale_suffix_does_not_swallow_the_stab_suffix():
    dd = np.array([0.0, -0.08])
    up = np.array([True, False])
    # @0.75 moves the first accelerator to -7.5%, but STAB still waits for an up month.
    assert target_path("HYBRID24_STAB@0.75", dd, up)[1] == 0.20
    assert target_path("HYBRID24@0.75", dd, up)[1] == 0.40


def test_buy_executes_at_next_month_return():
    n = HORIZON + 1
    df = pd.DataFrame(
        {
            "ret": [0.0, 0.10] + [0.0] * (n - 2),
            "cash_zero": 0.0,
            "dd": 0.0,
            "up": True,
        }
    )
    lump = simulate(df, 0, "LUMP", "cash_zero")
    assert abs(lump["terminal"] - 1.10) < 1e-12
    assert lump["undeployed"] == 0.0
