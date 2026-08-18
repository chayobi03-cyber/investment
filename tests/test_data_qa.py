from src.data_qa.validation import (
    find_duplicate_timestamps,
    find_missing_timestamps,
    find_point_in_time_violations,
    find_timestamp_order_issues,
    flag_return_outliers,
    gate_pass,
    qa_pass,
    validate_ohlc,
)


def test_extreme_intraperiod_range_is_reviewed():
    rows = [{
        "symbol": "SPY",
        "timestamp": "2026-02",
        "open": 689.58,
        "high": 697.14,
        "low": 69.005,
        "close": 685.99,
    }]
    issues = validate_ohlc(rows)
    assert any(issue.code == "INTRAPERIOD_RANGE_ANOMALY" for issue in issues)
    assert qa_pass(issues)
    assert not gate_pass(issues)


def test_non_positive_price_is_blocking():
    rows = [{
        "symbol": "TEST",
        "timestamp": "2026-01",
        "open": 10,
        "high": 11,
        "low": 0,
        "close": 10,
    }]
    issues = validate_ohlc(rows)
    assert any(issue.code == "NON_POSITIVE_PRICE" for issue in issues)
    assert not qa_pass(issues)
    assert not gate_pass(issues)


def test_large_return_is_review_not_deleted():
    rows = [
        {"symbol": "TEST", "timestamp": "2026-01", "close": 100},
        {"symbol": "TEST", "timestamp": "2026-02", "close": 140},
    ]
    issues = flag_return_outliers(rows, threshold=0.25)
    assert len(issues) == 1
    assert issues[0].severity == "REVIEW"
    assert not gate_pass(issues)


def test_duplicate_timestamp_is_error():
    rows = [
        {"symbol": "TEST", "timestamp": "2026-01"},
        {"symbol": "TEST", "timestamp": "2026-01"},
    ]
    issues = find_duplicate_timestamps(rows)
    assert [issue.code for issue in issues] == ["DUPLICATE_TIMESTAMP"]
    assert not gate_pass(issues)


def test_missing_expected_observation_is_error():
    rows = [{"symbol": "TEST", "timestamp": "2026-01"}]
    issues = find_missing_timestamps(rows, {"TEST": ["2026-01", "2026-02"]})
    assert any(issue.code == "MISSING_OBSERVATION" for issue in issues)
    assert not gate_pass(issues)


def test_timestamp_order_is_error():
    rows = [
        {"symbol": "TEST", "timestamp": "2026-02"},
        {"symbol": "TEST", "timestamp": "2026-01"},
    ]
    issues = find_timestamp_order_issues(rows)
    assert any(issue.code == "TIMESTAMP_ORDER" for issue in issues)
    assert not gate_pass(issues)


def test_point_in_time_violation_is_error():
    rows = [{"symbol": "TEST", "timestamp": "2026-03", "decision_timestamp": "2026-02"}]
    issues = find_point_in_time_violations(rows)
    assert any(issue.code == "POINT_IN_TIME_VIOLATION" for issue in issues)
    assert not gate_pass(issues)
