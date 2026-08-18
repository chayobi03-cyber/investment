import json
from pathlib import Path

from src.data_qa.validation import flag_return_outliers, qa_pass, validate_ohlc

ROOT = Path(__file__).resolve().parents[1]


def test_known_qa_fixture_produces_blocking_and_review_findings():
    fixture = json.loads((ROOT / "fixtures/qa_market_sample.json").read_text())
    rows = fixture["rows"]

    ohlc_issues = validate_ohlc(rows)
    outlier_issues = flag_return_outliers(
        [row for row in rows if "close" in row],
        threshold=0.25,
    )

    assert any(i.code == "NON_POSITIVE_PRICE" and i.severity == "ERROR" for i in ohlc_issues)
    assert any(i.code == "INTRAPERIOD_RANGE_ANOMALY" and i.severity == "REVIEW" for i in ohlc_issues)
    assert not qa_pass(ohlc_issues)
    assert all(i.severity == "REVIEW" for i in outlier_issues)
