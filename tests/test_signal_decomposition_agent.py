import pandas as pd
import pytest

from src.investment_pipeline.signal_decomposition_agent import SignalDecompositionAgent


def test_applies_regime_state_signal_type_and_zone_without_mutating_signal_state():
    frame = pd.DataFrame(
        {
            "confirmed_regime": ["R1", "R2", None],
            "entry_state": ["B2", "B3", "B4"],
            "breakout": [False, True, False],
            "zone": ["Z1", "BREAKOUT", "Z3"],
        }
    )

    out = SignalDecompositionAgent().apply(frame)

    assert out["entry_state"].tolist() == ["B2", "B3", "B4"]
    assert out["signal_type"].tolist() == ["PULLBACK", "BREAKOUT", "PULLBACK"]
    assert out["decomposition_regime"].tolist() == ["R1", "R2", "DATA_NOT_READY"]
    assert out["decomposition_key"].tolist() == [
        "R1|B2|PULLBACK|Z1",
        "R2|B3|BREAKOUT|BREAKOUT",
        "DATA_NOT_READY|B4|PULLBACK|Z3",
    ]


def test_candidate_only_keeps_only_b2_b3_b4():
    frame = pd.DataFrame({"entry_state": ["B0", "B1", "B2", "B3", "B4"]})
    out = SignalDecompositionAgent().candidate_only(frame)
    assert out["entry_state"].tolist() == ["B2", "B3", "B4"]


def test_summary_is_deterministic_and_multidimensional():
    frame = SignalDecompositionAgent().apply(
        pd.DataFrame(
            {
                "confirmed_regime": ["R1", "R1", "R2"],
                "entry_state": ["B2", "B3", "B3"],
                "breakout": [False, True, False],
                "zone": ["Z1", "BREAKOUT", "Z2"],
            }
        )
    )
    summary = SignalDecompositionAgent().summarize(frame)
    assert len(summary) == 3
    assert set(summary["events"]) == {1}


def test_missing_dimensions_fail_closed_for_contract():
    with pytest.raises(ValueError, match="DECOMPOSITION_MISSING_COLUMNS"):
        SignalDecompositionAgent().apply(
            pd.DataFrame(
                {
                    "entry_state": ["B2"],
                    "breakout": [True],
                }
            )
        )
