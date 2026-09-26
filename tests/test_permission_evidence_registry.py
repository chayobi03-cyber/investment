import json
from pathlib import Path

REGISTRY = Path("config/permission_evidence_registry_v0.1.json")


def test_registry_is_structurally_complete():
    cfg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    assert cfg["status"] == "SCHEMA_DEFINED_NOT_VALIDATED"
    assert cfg["global_controls"] == {
        "lookahead_forbidden": True,
        "provenance_hash_required": True,
        "explicit_available_at_required": True,
        "silent_provider_splice_forbidden": True,
    }
    families = {x["family_id"]: x for x in cfg["families"]}
    assert {
        "cross_asset_spot", "macro_liquidity", "derivatives",
        "regulation_market_structure", "geopolitical_transmission"
    } <= set(families)
    for family in families.values():
        assert family["required"] is True
        assert family["datasets"]
        for dataset in family["datasets"]:
            assert dataset["series"]
            assert dataset["primary_sources"]
            assert all(series["available_at_required"] is True for series in dataset["series"])


def test_no_silent_derivatives_provider_splice():
    cfg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    assert cfg["global_controls"]["silent_provider_splice_forbidden"] is True
    derivatives = next(x for x in cfg["families"] if x["family_id"] == "derivatives")
    sources = derivatives["datasets"][0]["primary_sources"]
    assert [x["role"] for x in sources] == ["PRIMARY", "ARCHIVE"]