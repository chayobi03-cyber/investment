from datetime import datetime, timezone

from src.investment_pipeline.multi_asset_subagents import (
    AssetClass,
    BUY_ALLOWED,
    EXECUTION_ALLOWED,
    MultiAssetOrchestrator,
    PITObservation,
    Status,
)


def test_global_execution_lock_is_hard_false():
    assert BUY_ALLOWED is False
    assert EXECUTION_ALLOWED is False


def test_pit_lookahead_fails_closed():
    now = datetime(2026, 9, 26, tzinfo=timezone.utc)
    obs = [
        PITObservation(
            series_id="DXY",
            observation_timestamp=now,
            available_at=datetime(2026, 9, 27, tzinfo=timezone.utc),
            source_id="TEST",
            value=100.0,
            provenance_hash="hash",
        )
    ]

    result = MultiAssetOrchestrator().run(
        asset=AssetClass.GOLD,
        decision_timestamp=now,
        observations=obs,
        required_series={"DXY"},
        axis_scores={"trend": 80, "breadth": 70},
        regime_weights={"trend": 0.5, "breadth": 0.5},
        signal_features={"signal_state": "B3"},
        evidence_claims=[],
        risk_inputs={
            "max_drawdown": -0.1,
            "mae": -0.05,
            "stress_loss": -0.15,
        },
        permission_inputs={},
    )
    assert result.buy_allowed is False
    assert result.execution_allowed is False
    assert "PIT_GATE_NOT_GREEN" in result.blocker_codes


def test_signal_is_separate_from_permission():
    now = datetime(2026, 9, 26, tzinfo=timezone.utc)
    obs = [
        PITObservation("DXY", now, now, "TEST", 100.0, "hash"),
        PITObservation("REAL_YIELD", now, now, "TEST", 2.0, "hash"),
    ]

    result = MultiAssetOrchestrator().run(
        asset=AssetClass.CRYPTO,
        decision_timestamp=now,
        observations=obs,
        required_series={"DXY", "REAL_YIELD"},
        axis_scores={"trend": 80, "breadth": 75},
        regime_weights={"trend": 0.5, "breadth": 0.5},
        signal_features={"signal_state": "B3"},
        evidence_claims=[{
            "claim_id": "C1",
            "source_id": "TEST",
            "timestamp": now.isoformat(),
            "calculation": "fixture",
        }],
        risk_inputs={
            "max_drawdown": -0.1,
            "mae": -0.05,
            "stress_loss": -0.15,
        },
        permission_inputs={"macro_block": True},
    )
    assert result.signal_state == "B3"
    assert result.buy_allowed is False
    assert result.execution_allowed is False
    assert result.permission_status == Status.BLOCKED
    assert "MACRO_BLOCK" in result.blocker_codes
