from datetime import date
from pathlib import Path

from research.scripts.r01_gate_report import build_report
from research.scripts.r01_pit_runner import run_pit
from research.scripts.r01_validate_provenance import validate_manifest


BASE = Path(".")


def base_manifest() -> dict:
    return {
        "source_id": "src_test",
        "observation_period": {"start": "2025-07-01", "end": "2025-07-31"},
        "publication": {
            "official_release_page": "https://example.test/release",
            "actual_publication_date": "2025-08-18",
        },
        "availability": {"available_at": "2025-08-18", "precision": "date"},
        "raw_capture": {
            "raw_capture_verified": True,
            "raw_sha256": "a" * 64,
            "content_type": "application/pdf",
        },
        "methodology": {
            "methodology_version": "v1",
            "sample_design_version": "v1",
            "extraction_frame": "frame",
            "index_base_period": "2025-03",
        },
        "revision": {"status": "NOT_VERIFIED"},
        "pit": {"provenance_test_passed": False},
    }


def test_revision_unknown_states_are_fail_closed():
    manifest = base_manifest()
    manifest["revision"]["status"] = "NO_REVISION_CLAIMED"
    result = validate_manifest(manifest, BASE)
    assert result["status"] == "PROVISIONAL"
    assert any("revision/vintage status not verified" in x for x in result["blockers"])


def test_date_precision_pit_blocks_pre_release():
    manifest = base_manifest()
    result = run_pit(manifest, "2025-08-17")
    assert result["decision"] == "BLOCK"


def test_date_precision_pit_requires_human_review_same_day():
    manifest = base_manifest()
    result = run_pit(manifest, "2025-08-18")
    assert result["decision"] == "HUMAN_REVIEW"


def test_date_precision_pit_allows_post_release():
    manifest = base_manifest()
    result = run_pit(manifest, "2025-08-19")
    assert result["decision"] == "ALLOW"


def test_gate_report_keeps_revision_and_pit_blocked():
    manifest = base_manifest()
    report = build_report(manifest, BASE, "2025-08-18")
    assert report["gates"]["release_provenance"] == "PASS"
    assert report["gates"]["methodology_provenance"] == "PASS"
    assert report["gates"]["raw_capture_evidence"] == "PASS"
    assert report["gates"]["revision_vintage"] == "FAIL"
    assert report["gates"]["pit"] == "HUMAN_REVIEW"
    assert report["promotion"]["eligible"] is False
    assert report["downstream"]["backtest"] == "BLOCKED"
