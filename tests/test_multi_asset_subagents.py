from datetime import datetime, timezone

from src.investment_pipeline.multi_asset_subagents import (
    AssetClass,
    BUY_ALLOWED,
    EXECUTION_ALLOWED,
    MultiAssetOrchestrator,
    PITObservation,
    Status,
)
from src.investment_pipeline.source_retrieval_agent import SourceRecord


def test_global_execution_lock_is_hard_false():
    assert BUY_ALLOWED is False
    assert EXECUTION_ALLOWED is False



def _source_record():
    now = datetime(2026, 9, 26, tzinfo=timezone.utc)
    return SourceRecord(
        source_id="TEST",
        title="Test source",
        source_url="https://example.test/source",
        source_type="REPUTABLE_SECONDARY",
        available_at=now,
        retrieved_at=now,
        content_hash="hash",
    )


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
    assert result.market_score is None
    assert result.raw_regime is None
    assert result.confirmed_regime is None


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
            "claim_type": "FACT",
            "statement": "DXY observation exists",
            "scope": "2026-09-26",
            "source_id": "TEST",
            "source_timestamp": now,
            "available_at": now,
        }],
        source_records=[_source_record()],
        risk_inputs={
            "max_drawdown": -0.1,
            "mae": -0.05,
            "stress_loss": -0.15,
        },
        permission_inputs={"macro_block": True},
    )
    assert result.signal_state == "B3"
    assert result.buy_allowed is False
    assert result.market_score == 77.5
    assert result.raw_regime == "R1"
    assert result.confirmed_regime == "R1"
    assert result.execution_allowed is False
    assert result.permission_status == Status.BLOCKED
    assert "MACRO_BLOCK" in result.blocker_codes


def test_hallucination_guard_blocks_unsupported_claim():
    now = datetime(2026, 9, 26, tzinfo=timezone.utc)
    obs = [PITObservation("DXY", now, now, "TEST", 100.0, "hash")]

    result = MultiAssetOrchestrator().run(
        asset=AssetClass.EQUITY,
        decision_timestamp=now,
        observations=obs,
        required_series={"DXY"},
        axis_scores={"trend": 80, "breadth": 75},
        regime_weights={"trend": 0.5, "breadth": 0.5},
        signal_features={"signal_state": "B3"},
        evidence_claims=[{
            "claim_id": "BAD1",
            "claim_type": "FACT",
            "statement": "Unsupported fact",
            "scope": "2026-09-26",
        }],
        source_records=[],
        risk_inputs={
            "max_drawdown": -0.1,
            "mae": -0.05,
            "stress_loss": -0.15,
        },
        permission_inputs={},
    )

    assert result.buy_allowed is False
    assert result.execution_allowed is False
    assert "HALLUCINATION_GUARD_BLOCK" in result.blocker_codes


def test_verified_evidence_passes_hallucination_guard_but_buy_remains_locked():
    now = datetime(2026, 9, 26, tzinfo=timezone.utc)
    obs = [PITObservation("DXY", now, now, "TEST", 100.0, "hash")]

    result = MultiAssetOrchestrator().run(
        asset=AssetClass.GOLD,
        decision_timestamp=now,
        observations=obs,
        required_series={"DXY"},
        axis_scores={"trend": 80, "breadth": 75},
        regime_weights={"trend": 0.5, "breadth": 0.5},
        signal_features={"signal_state": "B3"},
        evidence_claims=[{
            "claim_id": "FACT1",
            "claim_type": "FACT",
            "statement": "DXY observation exists",
            "scope": "decision date",
            "source_id": "TEST",
            "source_timestamp": now,
            "available_at": now,
        }],
        source_records=[_source_record()],
        risk_inputs={
            "max_drawdown": -0.1,
            "mae": -0.05,
            "stress_loss": -0.15,
        },
        permission_inputs={},
    )

    assert result.hallucination_status.value == "PASS"
    assert result.buy_allowed is False
    assert result.execution_allowed is False


def test_source_quality_failure_is_a_decision_block():
    now = datetime(2026, 9, 26, tzinfo=timezone.utc)
    obs = [PITObservation("DXY", now, now, "TEST", 100.0, "hash")]
    weak_source = SourceRecord(
        source_id="TEST",
        title="Unknown source",
        source_url="https://example.test/source",
        source_type="UNKNOWN",
        available_at=now,
        retrieved_at=now,
        content_hash="hash",
    )

    result = MultiAssetOrchestrator().run(
        asset=AssetClass.EQUITY,
        decision_timestamp=now,
        observations=obs,
        required_series={"DXY"},
        axis_scores={"trend": 80, "breadth": 75},
        regime_weights={"trend": 0.5, "breadth": 0.5},
        signal_features={"signal_state": "B3"},
        evidence_claims=[{
            "claim_id": "C1",
            "claim_type": "FACT",
            "statement": "DXY observation exists",
            "scope": "decision date",
            "source_id": "TEST",
            "source_timestamp": now,
            "available_at": now,
        }],
        source_records=[weak_source],
        risk_inputs={
            "max_drawdown": -0.1,
            "mae": -0.05,
            "stress_loss": -0.15,
        },
        permission_inputs={},
    )

    assert result.source_quality_status == Status.BLOCKED
    assert "SOURCE_QUALITY_BLOCK" in result.blocker_codes
    assert result.buy_allowed is False


def test_conflict_detection_failure_is_a_decision_block():
    now = datetime(2026, 9, 26, tzinfo=timezone.utc)
    obs = [PITObservation("DXY", now, now, "TEST", 100.0, "hash")]
    source = _source_record()

    result = MultiAssetOrchestrator().run(
        asset=AssetClass.GOLD,
        decision_timestamp=now,
        observations=obs,
        required_series={"DXY"},
        axis_scores={"trend": 80, "breadth": 75},
        regime_weights={"trend": 0.5, "breadth": 0.5},
        signal_features={"signal_state": "B3"},
        evidence_claims=[
            {
                "claim_id": "A",
                "claim_type": "FACT",
                "statement": "Claim A",
                "scope": "gold decision",
                "source_id": "TEST",
                "source_timestamp": now,
                "available_at": now,
                "conflict_group": "GROUP1",
                "stance": "FOR",
            },
            {
                "claim_id": "B",
                "claim_type": "FACT",
                "statement": "Claim B",
                "scope": "gold decision",
                "source_id": "TEST",
                "source_timestamp": now,
                "available_at": now,
                "conflict_group": "GROUP1",
                "stance": "AGAINST",
            },
        ],
        source_records=[source],
        risk_inputs={
            "max_drawdown": -0.1,
            "mae": -0.05,
            "stress_loss": -0.15,
        },
        permission_inputs={},
    )

    assert result.conflict_status == Status.BLOCKED
    assert "CONFLICT_DETECTION_BLOCK" in result.blocker_codes
    assert result.buy_allowed is False
