import pandas as pd

from investment_pipeline.completeness import check_stock_snapshot
from investment_pipeline.factors import normalize_point_in_time


def test_completeness_fails_when_one_ticker_missing():
    df = pd.DataFrame([{"ticker": "A", "as_of": "2026-09-08", "close": 1}])
    report = check_stock_snapshot(df, ["A", "B"], ["ticker", "as_of", "close"])
    assert report.status == "FAIL"
    assert report.completeness_pct == 50.0


def test_point_in_time_normalization_never_uses_future_rows():
    df = pd.DataFrame({
        "as_of": pd.to_datetime(["2026-01-01", "2026-02-01", "2026-03-01"], utc=True),
        "signal": [10.0, 20.0, 1000.0],
    })
    out = normalize_point_in_time(df, ["signal"])
    # At 2026-02-01 only 10 and 20 are eligible, so 20 is the 100th percentile.
    assert out.loc[1, "signal_score"] == 100.0
    # A future 1000 must not change the 2026-02-01 result to 66.7.
    assert out.loc[1, "signal_score"] != 66.66666666666667
