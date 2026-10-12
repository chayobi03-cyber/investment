from scripts.market_learning.validate_envelope import validate_envelope


def valid_envelope():
    return {
        "schema_version": "1.0",
        "idempotency_key": "market:eod:2026-10-13:run-v1:sha256-abc",
        "analysis_asof": "2026-10-13T00:00:00Z",
        "session_date": "2026-10-13",
        "run_kind": "EOD_ANALYSIS",
        "session": "KOREA",
        "data_quality": "GREEN",
        "provenance": {
            "code_sha": "abc123",
            "config_version": "market-monitor-v2.0",
            "rule_version": "research-v1",
            "prompt_version": "market-analysis-v1",
            "calculation_version": "labels-v1",
            "input_sha256": "a" * 64,
        },
        "market_state": {
            "regime": "UNCONFIRMED",
            "dimensions": {
                "TREND": {"state": "GREEN", "score": 67.0, "confidence": 0.75, "evidence_ids": []}
            },
            "metrics": {
                "KOSPI_pct": {
                    "value": 0.35,
                    "unit": "percent",
                    "observed_at": "2026-10-12T23:58:00Z",
                    "published_at": "2026-10-12T23:58:00Z",
                    "available_at": "2026-10-12T23:59:00Z",
                    "source_id": "yahoo-chart",
                    "quality_status": "VALID",
                    "required_for_decision": True,
                    "freshness_status": "FRESH_ACTIVE_SESSION",
                }
            },
        },
        "forecasts": [
            {
                "forecast_type": "MARKET_DIRECTION",
                "subject_type": "MARKET",
                "subject_key": "KR_MARKET",
                "target_key": "return_positive",
                "horizon": {"value": 5, "unit": "TRADING_SESSIONS"},
                "direction": "UP",
                "probability_up": 0.58,
                "permission_state": "RESEARCH_ONLY",
                "buy_allowed": False,
                "execution_allowed": False,
            }
        ],
        "decision": {
            "state": "RESEARCH_ONLY",
            "buy_allowed": False,
            "execution_allowed": False,
            "reason_codes": ["PROMOTION_DISABLED"],
        },
    }


def test_valid_envelope_passes():
    assert validate_envelope(valid_envelope()) == []


def test_future_available_at_is_rejected():
    envelope = valid_envelope()
    envelope["market_state"]["metrics"]["KOSPI_pct"]["available_at"] = "2026-10-13T00:00:01Z"
    errors = validate_envelope(envelope)
    assert any("point-in-time violation" in error for error in errors)


def test_future_observation_is_rejected():
    envelope = valid_envelope()
    envelope["market_state"]["metrics"]["KOSPI_pct"]["observed_at"] = "2026-10-13T00:00:01Z"
    errors = validate_envelope(envelope)
    assert any("observation is later" in error for error in errors)


def test_buy_flag_must_remain_false():
    envelope = valid_envelope()
    envelope["decision"]["buy_allowed"] = True
    errors = validate_envelope(envelope)
    assert any("buy_allowed: must be false" in error for error in errors)


def test_execution_flag_must_remain_false():
    envelope = valid_envelope()
    envelope["forecasts"][0]["execution_allowed"] = True
    errors = validate_envelope(envelope)
    assert any("forecasts[0].execution_allowed" in error for error in errors)


def test_red_data_must_fail_closed():
    envelope = valid_envelope()
    envelope["data_quality"] = "RED"
    errors = validate_envelope(envelope)
    assert any("must fail closed" in error for error in errors)


def test_null_value_cannot_be_marked_valid():
    envelope = valid_envelope()
    envelope["market_state"]["metrics"]["KOSPI_pct"]["value"] = None
    errors = validate_envelope(envelope)
    assert any("VALID metric cannot have null value" in error for error in errors)


def test_bad_hash_is_rejected():
    envelope = valid_envelope()
    envelope["provenance"]["input_sha256"] = "bad-hash"
    errors = validate_envelope(envelope)
    assert any("expected lowercase SHA-256" in error for error in errors)


def test_horizon_unit_must_be_explicit():
    envelope = valid_envelope()
    envelope["forecasts"][0]["horizon"]["unit"] = "DAYS"
    errors = validate_envelope(envelope)
    assert any("horizon.unit: invalid unit" in error for error in errors)


def test_timezone_is_required():
    envelope = valid_envelope()
    envelope["analysis_asof"] = "2026-10-13T00:00:00"
    errors = validate_envelope(envelope)
    assert any("timezone offset is required" in error for error in errors)


def test_non_object_payload_is_rejected():
    assert validate_envelope([]) == ["$: expected a JSON object"]


def test_fresh_unrelated_fx_cannot_mask_stale_required_korea():
    envelope = valid_envelope()
    envelope["market_state"]["metrics"]["KOSPI_pct"]["quality_status"] = "STALE"
    envelope["market_state"]["metrics"]["KOSPI_pct"]["freshness_status"] = "STALE"
    envelope["market_state"]["metrics"]["USD_JPY"] = {
        "value": 149.2,
        "unit": "JPY_per_USD",
        "observed_at": "2026-10-12T23:59:40Z",
        "published_at": "2026-10-12T23:59:40Z",
        "available_at": "2026-10-12T23:59:45Z",
        "source_id": "yahoo-chart",
        "quality_status": "VALID",
        "required_for_decision": False,
        "freshness_status": "FRESH_ACTIVE_SESSION",
    }
    errors = validate_envelope(envelope)
    assert any("required evidence is not decision-usable" in error for error in errors)
    assert any("GREEN cannot mask stale/missing required evidence" in error for error in errors)
    assert any("stale/missing required evidence must fail closed" in error for error in errors)


def test_valid_closed_session_close_is_acceptable_when_explicit():
    envelope = valid_envelope()
    metric = envelope["market_state"]["metrics"]["KOSPI_pct"]
    metric["freshness_status"] = "VALID_CLOSED_SESSION"
    assert validate_envelope(envelope) == []
