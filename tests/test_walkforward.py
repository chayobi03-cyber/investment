import numpy as np
import pandas as pd

from investment_pipeline.walkforward import (
    attach_forward_outcomes,
    expanding_quantile_bucket,
    is_monotonic,
    monotonicity_report,
    rank_information_coefficient,
    run_experiment_a,
    walk_forward_folds,
)


def _dates(n: int) -> pd.DatetimeIndex:
    return pd.bdate_range("2020-01-01", periods=n, tz="UTC")


def test_attach_forward_outcomes_matches_known_price_path():
    dates = _dates(6)
    prices = [100.0, 110.0, 121.0, 90.0, 99.0, 108.9]
    df = pd.DataFrame({"ticker": ["A"] * 6, "as_of": dates, "close": prices})
    out = attach_forward_outcomes(df, price_col="close", horizons=(1, 2), ticker_col="ticker", as_of_col="as_of")

    assert round(out.loc[0, "fwd_return_1d"], 6) == 0.10
    assert round(out.loc[1, "fwd_return_1d"], 6) == 0.10
    assert pd.isna(out.loc[5, "fwd_return_1d"])

    # fwd_return_2d at t=0: 121/100 - 1 = 0.21
    assert round(out.loc[0, "fwd_return_2d"], 6) == 0.21
    # forward max drawdown over next 2 steps from t=1 (window 110 -> 121 -> 90):
    # running max is 121, so the worst drawdown from peak is 90/121 - 1.
    assert round(out.loc[1, "fwd_max_drawdown_2d"], 6) == round(90 / 121 - 1, 6)


def test_expanding_quantile_bucket_never_uses_future_rows():
    dates = _dates(6)
    df = pd.DataFrame({"as_of": dates, "score": [10.0, 20.0, 30.0, 40.0, 50.0, 1000.0]})
    early = expanding_quantile_bucket(df.iloc[:5], "score", n_buckets=5, min_history=1)
    full = expanding_quantile_bucket(df, "score", n_buckets=5, min_history=1)
    # Bucket assignment for the first 5 rows must be identical whether or not
    # the huge future observation (1000.0 on the last date) is present.
    assert list(early) == list(full.iloc[:5])


def test_rank_information_coefficient_perfect_relationship():
    score = pd.Series(range(20))
    outcome = pd.Series(range(20)) * 2 + 1
    assert rank_information_coefficient(score, outcome) == 1.0

    inverse_outcome = -pd.Series(range(20))
    assert rank_information_coefficient(score, inverse_outcome) == -1.0


def test_monotonicity_report_and_is_monotonic():
    df = pd.DataFrame(
        {
            "bucket": ["Q1"] * 3 + ["Q2"] * 3 + ["Q3"] * 3,
            "outcome": [-0.02, -0.01, -0.03, 0.0, 0.01, -0.01, 0.05, 0.04, 0.06],
        }
    )
    stats = monotonicity_report(df, "bucket", "outcome")
    assert [s.bucket for s in stats] == ["Q1", "Q2", "Q3"]
    assert is_monotonic(stats) is True

    flat_df = df.copy()
    flat_df["outcome"] = [0.01, 0.01, 0.01, -0.02, -0.02, -0.02, 0.0, 0.0, 0.0]
    assert is_monotonic(monotonicity_report(flat_df, "bucket", "outcome")) is False


def test_walk_forward_folds_are_expanding_and_ordered():
    dates = _dates(120)
    folds = walk_forward_folds(dates, n_folds=4, min_train_periods=60)
    assert len(folds) == 4
    prev_test_end = None
    for train_end, test_start, test_end in folds:
        assert train_end < test_start <= test_end
        if prev_test_end is not None:
            assert test_start > prev_test_end
        prev_test_end = test_end
    # too little history yields no folds rather than a spurious result
    assert walk_forward_folds(_dates(10), n_folds=4, min_train_periods=60) == []


def _synthetic_panel(n: int, seed: int, relationship) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = _dates(n)
    scores = rng.uniform(0, 100, size=n - 1)
    prices = [100.0]
    for t in range(n - 1):
        prices.append(prices[-1] * (1 + relationship(t, scores[t])))
    scores = np.append(scores, np.nan)
    return pd.DataFrame({"ticker": ["A"] * n, "as_of": dates, "close": prices, "score": scores})


def test_run_experiment_a_detects_a_genuine_monotonic_relationship():
    panel = _synthetic_panel(n=140, seed=1, relationship=lambda t, s: (s - 50) / 2000.0)
    report = run_experiment_a(
        panel,
        score_col="score",
        price_col="close",
        horizons=(1,),
        n_buckets=3,
        min_bucket_history=20,
        n_folds=2,
        min_train_periods=50,
    )
    horizon = report["horizons"]["1d"]
    assert horizon["monotonic_full_sample"] is True
    assert horizon["full_sample_rank_ic"] > 0.9
    assert horizon["falsification_status"] == "NOT_FALSIFIED_CANDIDATE"


def test_run_experiment_a_flags_a_regime_flip_as_less_consistent_than_a_stable_relationship():
    stable_panel = _synthetic_panel(n=140, seed=2, relationship=lambda t, s: (s - 50) / 2000.0)

    def flipped_relationship(t, s):
        sign = 1.0 if t < 70 else -1.0
        return sign * (s - 50) / 2000.0

    flipped_panel = _synthetic_panel(n=140, seed=2, relationship=flipped_relationship)

    kwargs = dict(score_col="score", price_col="close", horizons=(1,), n_buckets=3, min_bucket_history=15, n_folds=4, min_train_periods=30)
    stable = run_experiment_a(stable_panel, **kwargs)["horizons"]["1d"]
    flipped = run_experiment_a(flipped_panel, **kwargs)["horizons"]["1d"]

    stable_ics = [f["rank_ic"] for f in stable["walk_forward"]["folds"] if f["rank_ic"] is not None]
    flipped_ics = [f["rank_ic"] for f in flipped["walk_forward"]["folds"] if f["rank_ic"] is not None]
    # Sanity: the flipped construction really does produce folds with
    # opposite-signed rank ICs before and after the t=70 regime flip, while
    # the stable construction does not.
    assert all(ic > 0 for ic in stable_ics)
    assert any(ic > 0 for ic in flipped_ics) and any(ic < 0 for ic in flipped_ics)

    # The walk-forward consistency checks must reflect that degradation:
    # the regime-flip case is strictly less consistent fold-to-fold than
    # the stable case on both metrics, and the flip breaks its status.
    assert flipped["walk_forward"]["fold_sign_agreement"] < stable["walk_forward"]["fold_sign_agreement"]
    assert flipped["walk_forward"]["monotonic_fold_fraction"] < stable["walk_forward"]["monotonic_fold_fraction"]
    assert stable["falsification_status"] == "NOT_FALSIFIED_CANDIDATE"
    assert flipped["falsification_status"] == "FALSIFIED_UNSTABLE_ACROSS_FOLDS"
