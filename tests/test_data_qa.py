from src.data_qa.validation import flag_return_outliers, qa_pass, validate_ohlc


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


def test_large_return_is_review_not_deleted():
    rows = [
        {"symbol": "TEST", "timestamp": "2026-01", "close": 100},
        {"symbol": "TEST", "timestamp": "2026-02", "close": 140},
    ]
    issues = flag_return_outliers(rows, threshold=0.25)
    assert len(issues) == 1
    assert issues[0].severity == "REVIEW"
