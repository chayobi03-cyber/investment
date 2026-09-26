from datetime import datetime, timezone

import pytest

from src.investment_pipeline.asset_signal_contract import (
    AssetSignalSnapshot,
    require_pit_eligible,
)


def _now():
    return datetime(2026, 9, 26, 15, 0, tzinfo=timezone.utc)


def test_snapshot_is_immutable_and_timezone_aware():
    snapshot = AssetSignalSnapshot(
        asset="CRYPTO",
        signal_state="B3",
        as_of=_now(),
        rule_version="crypto-market-regime-entry-v0.2",
    )

    with pytest.raises(Exception):
        snapshot.signal_state = "B4"  # type: ignore[misc]


def test_naive_as_of_is_rejected():
    with pytest.raises(ValueError, match="as_of_must_be_timezone_aware"):
        AssetSignalSnapshot(
            asset="GOLD",
            signal_state="DATA_NOT_READY",
            as_of=datetime(2026, 9, 26, 15, 0),
            rule_version="pending",
        )


def test_signal_lookahead_is_blocked():
    snapshot = AssetSignalSnapshot(
        asset="EQUITY",
        signal_state="B3",
        as_of=datetime(2026, 9, 26, 15, 1, tzinfo=timezone.utc),
        rule_version="stock-score-v1",
    )

    with pytest.raises(ValueError, match="SIGNAL_LOOKAHEAD"):
        require_pit_eligible(snapshot, _now())


def test_signal_at_decision_time_is_eligible():
    snapshot = AssetSignalSnapshot(
        asset="GOLD",
        signal_state="B3",
        as_of=_now(),
        rule_version="gold-entry-pending-v0.1",
        evidence_refs=("GOLD-PRICE", "DXY"),
    )

    require_pit_eligible(snapshot, _now())
