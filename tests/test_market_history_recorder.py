import csv
import json

import pytest

from scripts.market_learning.record_monitor_snapshot import (
    append_run,
    build_envelope,
)


def fixture_snapshot(*, quality="GREEN", freshness="VALID_CLOSED_SESSION", schema="2.1"):
    asof = "2026-10-12T23:30:00Z"
    timestamp = "2026-10-12T06:30:00Z"
    state = {
        "schema_version": schema,
        "asof": asof,
        "session": "GLOBAL_TRANSITION",
        "REGIME": "UNCONFIRMED",
        "RISK": "RED",
        "TREND": "RED",
        "BREADTH": "AMBER",
        "LEADERS": "AMBER",
        "RATES": "GREEN",
        "FX": "GREEN",
        "OIL": "GREEN",
        "GOLD": "GREEN",
        "GEO": "N/A",
        "BUY_TRIGGER": "UNCONFIRMED",
        "DATA_QUALITY": quality,
        "metrics": {
            "freshness_by_series": {"indices.KOSPI": freshness, "macro.USD_JPY": "FRESH_ACTIVE_SESSION"},
            "trend_selected_pct": -3.65,
            "breadth_proxy": 0.25,
            "freshness_max_required_minutes": 1020.0,
        },
    }
    kospi = {
        "ok": True,
        "symbol": "^KS11",
        "price": 6384.24,
        "prev_price_5m": 6388.0,
        "change_pct_5m": -0.06,
        "change_pct_15m": -0.10,
        "session_change_pct": -0.20,
        "last_completed_session_return_pct": -3.65,
        "last_completed_session_close_at": "2026-10-12T06:30:00Z",
        "timestamp": timestamp,
        "currency": "KRW",
        "exchange": "KSE",
        "exchange_timezone": "Asia/Seoul",
        "market_session": "KOREA",
        "market_session_state": "CLOSED" if freshness == "VALID_CLOSED_SESSION" else "ACTIVE",
        "return_calculation_version": "returns-5m-15m-close-close-v1",
        "series_key": "indices.KOSPI",
    }
    usd_jpy = {
        "ok": True,
        "symbol": "JPY=X",
        "price": 149.2,
        "change_pct_5m": 0.01,
        "change_pct_15m": 0.03,
        "session_change_pct": 0.05,
        "last_completed_session_return_pct": 0.1,
        "timestamp": timestamp,
        "currency": "JPY",
        "market_session": "US",
        "market_session_state": "ACTIVE",
        "return_calculation_version": "returns-5m-15m-close-close-v1",
        "series_key": "macro.USD_JPY",
    }
    return {
        "state": state,
        "event": {"alert": True, "severity": "P0", "delta": ["TREND:GREEN->RED"]},
        "raw": {
            "collected_at": asof,
            "groups": {"indices": {"KOSPI": kospi}, "macro": {"USD_JPY": usd_jpy}},
            "all": {"indices.KOSPI": kospi, "macro.USD_JPY": usd_jpy},
        },
    }


def test_monitor_envelope_preserves_explicit_closed_session_horizon():
    snapshot = fixture_snapshot()
    config = {"version": "test-config-v2.1", "thresholds": {"required_series": ["indices.KOSPI"]}}
    envelope = build_envelope(
        snapshot,
        config=config,
        code_sha="a" * 40,
        run_kind="PREOPEN_ANALYSIS",
    )

    assert envelope["data_quality"] == "GREEN"
    assert envelope["decision"]["state"] == "RESEARCH_ONLY"
    assert envelope["decision"]["buy_allowed"] is False
    assert envelope["decision"]["execution_allowed"] is False
    assert envelope["session_date"] == "2026-10-13"
    assert envelope["forecasts"] == []  # The monitor emits states, not fabricated forecasts.
    metrics = envelope["market_state"]["metrics"]
    assert metrics["indices.KOSPI.last_completed_session_return_pct"]["value"] == -3.65
    assert metrics["indices.KOSPI.last_completed_session_return_pct"]["required_for_decision"] is True
    assert metrics["indices.KOSPI.change_pct_15m"]["quality_status"] == "STALE"
    assert metrics["indices.KOSPI.change_pct_15m"]["required_for_decision"] is False


def test_fresh_fx_does_not_hide_stale_required_korea_series():
    snapshot = fixture_snapshot(quality="GREEN", freshness="STALE")
    config = {"version": "test-config-v2.1", "thresholds": {"required_series": ["indices.KOSPI"]}}
    envelope = build_envelope(
        snapshot,
        config=config,
        code_sha="b" * 40,
        run_kind="PREOPEN_ANALYSIS",
    )

    assert envelope["data_quality"] == "AMBER"
    assert envelope["decision"]["state"] == "BLOCKED"
    assert "REQUIRED_STALE:indices.KOSPI" in envelope["summary"]["unresolved_gaps"]
    assert envelope["decision"]["buy_allowed"] is False
    assert envelope["decision"]["execution_allowed"] is False


def test_missing_required_series_forces_red_and_blocked():
    snapshot = fixture_snapshot(quality="GREEN", freshness="UNKNOWN")
    config = {"version": "test-config-v2.1", "thresholds": {"required_series": ["indices.KOSPI"]}}
    envelope = build_envelope(
        snapshot,
        config=config,
        code_sha="c" * 40,
        run_kind="PREOPEN_ANALYSIS",
    )

    assert envelope["data_quality"] == "RED"
    assert envelope["decision"]["state"] == "BLOCKED"
    assert any(reason.startswith("REQUIRED_MISSING_OR_UNKNOWN:indices.KOSPI") for reason in envelope["summary"]["unresolved_gaps"])


def test_legacy_monitor_schema_is_rejected():
    snapshot = fixture_snapshot(schema="2.0")
    config = {"version": "test-config-v2.1", "thresholds": {"required_series": ["indices.KOSPI"]}}
    with pytest.raises(ValueError, match="legacy monitor state rejected"):
        build_envelope(
            snapshot,
            config=config,
            code_sha="d" * 40,
            run_kind="PREOPEN_ANALYSIS",
        )


def test_history_append_is_idempotent_and_retains_original_source(tmp_path):
    snapshot = fixture_snapshot()
    config = {"version": "test-config-v2.1", "thresholds": {"required_series": ["indices.KOSPI"]}}
    envelope = build_envelope(
        snapshot,
        config=config,
        code_sha="e" * 40,
        run_kind="PREOPEN_ANALYSIS",
    )

    inserted, run_id = append_run(envelope, root=tmp_path, source_snapshot=snapshot)
    repeated, repeated_id = append_run(envelope, root=tmp_path, source_snapshot=snapshot)

    assert inserted is True
    assert repeated is False
    assert run_id == repeated_id
    with (tmp_path / "market_runs.csv").open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 1
    assert rows[0]["run_id"] == run_id
    assert rows[0]["input_sha256"] == envelope["provenance"]["input_sha256"]
    assert json.loads(rows[0]["source_snapshot_json"])["raw"]["groups"]["indices"]["KOSPI"]["price"] == 6384.24
    assert json.loads(rows[0]["envelope_json"])["idempotency_key"] == envelope["idempotency_key"]


def test_same_run_id_with_modified_record_is_rejected(tmp_path):
    snapshot = fixture_snapshot()
    config = {"version": "test-config-v2.1", "thresholds": {"required_series": ["indices.KOSPI"]}}
    envelope = build_envelope(
        snapshot,
        config=config,
        code_sha="f" * 40,
        run_kind="PREOPEN_ANALYSIS",
    )
    append_run(envelope, root=tmp_path, source_snapshot=snapshot)

    tampered = dict(envelope)
    tampered["decision"] = dict(envelope["decision"])
    tampered["decision"]["reason_codes"] = list(envelope["decision"]["reason_codes"]) + ["TAMPERED"]
    with pytest.raises(ValueError, match="immutable record conflict"):
        append_run(tampered, root=tmp_path, source_snapshot=snapshot)
