from pathlib import Path

from scripts.crypto.validate_permission_evidence_bundle import REQUIRED


def test_required_evidence_columns_are_pit_safe():
    assert REQUIRED == {
        "asset", "series_id", "observation_timestamp", "available_at",
        "source_id", "unit", "value", "ingested_at", "provenance_hash",
    }


def test_validator_exists():
    assert Path("scripts/crypto/validate_permission_evidence_bundle.py").exists()
