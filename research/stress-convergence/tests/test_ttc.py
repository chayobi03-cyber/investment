import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ttc import classify_ttc, within_primary_window, within_long_term_window


def test_frozen_boundaries():
    expected = {
        None: "NO_CONFIRMATION",
        -1: "PRE_EW",
        0: "ULTRA_SHORT_1D",
        1: "ULTRA_SHORT_1D",
        2: "SHORT_7D",
        7: "SHORT_7D",
        8: "NEAR_MEDIUM_30D",
        30: "NEAR_MEDIUM_30D",
        31: "VALID_MEDIUM_90D",
        90: "VALID_MEDIUM_90D",
        91: "LONG_TERM_365D",
        365: "LONG_TERM_365D",
        366: "UNRELATED_GT365D",
    }
    for value, label in expected.items():
        assert classify_ttc(value) == label


def test_primary_window():
    assert not within_primary_window(-1)
    assert within_primary_window(0)
    assert within_primary_window(90)
    assert not within_primary_window(91)
    assert not within_primary_window(None)


def test_long_term_window():
    assert not within_long_term_window(90)
    assert within_long_term_window(91)
    assert within_long_term_window(365)
    assert not within_long_term_window(366)


def test_335_day_case_is_not_primary_by_duration():
    assert classify_ttc(335) == "LONG_TERM_365D"
    assert not within_primary_window(335)
