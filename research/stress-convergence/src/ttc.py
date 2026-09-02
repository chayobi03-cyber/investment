from __future__ import annotations


def classify_ttc(ttc_days: int | None) -> str:
    """Classify confirmation timing using the frozen v0.2.4 boundaries."""
    if ttc_days is None:
        return "NO_CONFIRMATION"
    if ttc_days < 0:
        return "PRE_EW"
    if ttc_days <= 1:
        return "ULTRA_SHORT_1D"
    if ttc_days <= 7:
        return "SHORT_7D"
    if ttc_days <= 30:
        return "NEAR_MEDIUM_30D"
    if ttc_days <= 90:
        return "VALID_MEDIUM_90D"
    if ttc_days <= 365:
        return "LONG_TERM_365D"
    return "UNRELATED_GT365D"


def within_primary_window(ttc_days: int | None) -> bool:
    return ttc_days is not None and 0 <= ttc_days <= 90


def within_long_term_window(ttc_days: int | None) -> bool:
    return ttc_days is not None and 91 <= ttc_days <= 365
