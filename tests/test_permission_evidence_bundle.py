from pathlib import Path
import json

from scripts.crypto.validate_permission_evidence_bundle import REQUIRED, read


def test_required_evidence_columns_are_pit_safe():
    assert REQUIRED == {
        "asset", "series_id", "observation_timestamp", "available_at",
        "source_id", "unit", "value", "ingested_at", "provenance_hash",
    }


def test_validator_exists():
    assert Path("scripts/crypto/validate_permission_evidence_bundle.py").exists()

def test_gap_manifest_is_fail_closed(tmp_path):
    data = tmp_path / "evidence.csv"
    data.write_text(
        "asset,series_id,observation_timestamp,available_at,source_id,unit,value,ingested_at,provenance_hash\n"
        "BTC,S,2026-09-20T00:00:00Z,2026-09-21T00:00:00Z,SRC,raw,1,2026-09-21T00:00:00Z,0123456789abcdef\n",
        encoding="utf-8",
    )
    data.with_suffix(".manifest.json").write_text(
        json.dumps({"status": "COLLECTED_WITH_GAPS"}), encoding="utf-8"
    )
    try:
        read(data)
    except SystemExit as exc:
        assert "source_manifest_has_gaps" in str(exc)
    else:
        raise AssertionError("gap manifest must fail closed")
