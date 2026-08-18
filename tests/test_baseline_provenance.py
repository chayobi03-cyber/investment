import json
from pathlib import Path
from urllib.parse import urlparse


MATRIX = Path("docs/data/BASELINE_PROVENANCE_MATRIX.json")


def load_matrix():
    return json.loads(MATRIX.read_text())


def test_baseline_series_identity_and_provenance():
    data = load_matrix()
    series = data["series"]
    assert len(series) == 5
    ids = [item["series_id"] for item in series]
    assert ids == ["SPY", "IEF", "TLT", "GLD", "BIL"]
    assert len(set(ids)) == 5
    for item in series:
        assert item["primary_source"]["source_type"] == "official_issuer"
        assert urlparse(item["primary_source"]["url"]).scheme == "https"
        assert urlparse(item["secondary_source"]["url"]).scheme == "https"
        assert item["pit_rule"]
        assert item["adjustment_rule"]["return_formula"]
        assert item["adjustment_rule"]["vendor_adjusted_close"] == "validation-only_cross_check"


def test_bil_reverse_split_rule_is_explicit():
    bil = next(item for item in load_matrix()["series"] if item["series_id"] == "BIL")
    rule = bil["adjustment_rule"]
    assert rule["split_events"] == "2017-11-30 reverse split 1-for-2"
    assert rule["split_price_factor_before_effective_date"] == 2.0
    assert rule["rule_order"] == [
        "apply_verified_split_factor_to_pre-event_OHLC",
        "then_join_explicit_cash_distributions",
        "then_compute_returns",
    ]


def test_spy_known_bad_observation_remains_quarantined():
    spy = next(item for item in load_matrix()["series"] if item["series_id"] == "SPY")
    assert any(
        anomaly["classification"] == "ERROR"
        and "69.005" in anomaly["observation"]
        and anomaly["action"].startswith("quarantine")
        for anomaly in spy["known_anomalies"]
    )


def test_promotion_contract_is_fail_closed():
    data = load_matrix()
    requirements = data["promotion_requirements"]
    assert requirements["series_count"] == 5
    assert requirements["all_primary_sources_present"] is True
    assert requirements["all_secondary_sources_present"] is True
    assert requirements["all_adjustment_rules_machine_readable"] is True
    assert requirements["no_silent_repairs"] is True
    assert len(requirements["m1b_green_requires"]) >= 6
