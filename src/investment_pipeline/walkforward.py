"""Walk-forward / point-in-time predictive validation.

Implements Market Decision Framework v1.0 Level 3-5 validation
(historical simulation, out-of-sample, walk-forward) and operationalizes
"Experiment A: score monotonicity" from
docs/research/MARKET_DECISION_FRAMEWORK_RESEARCH_2026-09-08.md.

Core idea (see docs/investment/WALKFORWARD_VALIDATION_METHODOLOGY_V1.md):
a rule that "predicts the past" is evaluated by, at every historical anchor
date t, using only information available at or before t (the State layer)
to answer whether the *already-realized* outcome after t (the Outcome
layer) could have been anticipated. Nothing here consumes information
from after t when producing a score, a bucket edge, or a fold boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


def _forward_return(values: np.ndarray, h: int) -> np.ndarray:
    n = len(values)
    out = np.full(n, np.nan)
    for i in range(n - h):
        base = values[i]
        if base == 0 or np.isnan(base) or np.isnan(values[i + h]):
            continue
        out[i] = values[i + h] / base - 1.0
    return out


def _forward_max_drawdown(values: np.ndarray, h: int) -> np.ndarray:
    n = len(values)
    out = np.full(n, np.nan)
    for i in range(n - h):
        window = values[i : i + h + 1]
        if np.isnan(window).any():
            continue
        running_max = np.maximum.accumulate(window)
        drawdowns = window / running_max - 1.0
        out[i] = float(drawdowns.min())
    return out


def attach_forward_outcomes(
    panel: pd.DataFrame,
    price_col: str,
    horizons: Iterable[int] = (5, 20, 60, 120),
    ticker_col: str = "ticker",
    as_of_col: str = "as_of",
) -> pd.DataFrame:
    """Attach realized forward return / forward max-drawdown columns.

    This is the Outcome layer (Market Decision Framework v1.0 section 9).
    It must never feed back into score construction or normalization; it
    exists only to evaluate a score that was already computed using data
    available at `as_of`.
    """
    out = panel.copy()
    out[as_of_col] = pd.to_datetime(out[as_of_col], utc=True)
    out = out.sort_values([ticker_col, as_of_col]).reset_index(drop=True)
    for h in horizons:
        fwd_ret_col = f"fwd_return_{h}d"
        fwd_dd_col = f"fwd_max_drawdown_{h}d"
        out[fwd_ret_col] = np.nan
        out[fwd_dd_col] = np.nan
        for _, idx in out.groupby(ticker_col).groups.items():
            idx = idx.sort_values() if hasattr(idx, "sort_values") else idx
            prices = out.loc[idx, price_col].to_numpy(dtype=float)
            out.loc[idx, fwd_ret_col] = _forward_return(prices, h)
            out.loc[idx, fwd_dd_col] = _forward_max_drawdown(prices, h)
    return out


def expanding_quantile_bucket(
    panel: pd.DataFrame,
    score_col: str,
    as_of_col: str = "as_of",
    n_buckets: int = 5,
    min_history: int = 30,
) -> pd.Series:
    """Bucket `score_col` using quantile edges built only from the
    point-in-time history available as of each row's date.

    Using full-sample quantile edges to bucket a point-in-time score is a
    subtle look-ahead leak even when the score itself is point-in-time
    correct: the bucket boundary would still depend on observations that
    happen after the decision date. This recomputes edges per date from an
    expanding window, matching the pooled-history convention already used
    by `investment_pipeline.factors.normalize_point_in_time`.
    """
    df = panel[[as_of_col, score_col]].copy()
    df[as_of_col] = pd.to_datetime(df[as_of_col], utc=True)
    buckets = pd.Series(index=df.index, dtype="object")
    for date, idx in df.groupby(as_of_col).groups.items():
        history = pd.to_numeric(df.loc[df[as_of_col] <= date, score_col], errors="coerce").dropna()
        if len(history) < min_history:
            buckets.loc[idx] = None
            continue
        edges = np.quantile(history, np.linspace(0, 1, n_buckets + 1))
        edges[0], edges[-1] = -np.inf, np.inf
        for i in idx:
            v = df.loc[i, score_col]
            if pd.isna(v):
                buckets.loc[i] = None
            else:
                b = int(np.searchsorted(edges, v, side="right") - 1)
                b = min(max(b, 0), n_buckets - 1)
                buckets.loc[i] = f"Q{b + 1}"
    return buckets


def rank_information_coefficient(score: pd.Series, outcome: pd.Series) -> float | None:
    """Spearman rank correlation without a scipy dependency."""
    df = pd.DataFrame({"score": pd.to_numeric(score, errors="coerce"), "outcome": pd.to_numeric(outcome, errors="coerce")}).dropna()
    if len(df) < 5:
        return None
    corr = df["score"].rank().corr(df["outcome"].rank())
    return float(corr) if pd.notna(corr) else None


@dataclass(frozen=True)
class BucketStat:
    bucket: str
    n: int
    mean_outcome: float | None
    median_outcome: float | None
    hit_rate: float | None
    std_outcome: float | None


def monotonicity_report(panel: pd.DataFrame, bucket_col: str, outcome_col: str) -> list[BucketStat]:
    stats = []
    for bucket, g in panel.groupby(bucket_col, dropna=True):
        vals = pd.to_numeric(g[outcome_col], errors="coerce").dropna()
        stats.append(
            BucketStat(
                bucket=str(bucket),
                n=int(len(vals)),
                mean_outcome=float(vals.mean()) if len(vals) else None,
                median_outcome=float(vals.median()) if len(vals) else None,
                hit_rate=float((vals > 0).mean()) if len(vals) else None,
                std_outcome=float(vals.std()) if len(vals) > 1 else None,
            )
        )
    return sorted(stats, key=lambda s: s.bucket)


def is_monotonic(stats: list[BucketStat], min_buckets: int = 3) -> bool | None:
    means = [s.mean_outcome for s in stats if s.mean_outcome is not None]
    if len(means) < min_buckets:
        return None
    increasing = all(a <= b for a, b in zip(means, means[1:]))
    decreasing = all(a >= b for a, b in zip(means, means[1:]))
    return bool(increasing or decreasing)


def walk_forward_folds(
    dates: pd.Series,
    n_folds: int = 4,
    min_train_periods: int = 60,
) -> list[tuple[pd.Timestamp, pd.Timestamp, pd.Timestamp]]:
    """Expanding-window walk-forward fold boundaries.

    Fold k treats everything up to `train_end` as the frozen history used
    to build state (scores, bucket edges); rows strictly after `train_end`
    and up to `test_end` are the held-out test window for that fold. This
    is Market Decision Framework v1.0 Level 5.
    """
    unique_dates = pd.Series(pd.to_datetime(dates, utc=True).unique()).sort_values().reset_index(drop=True)
    n = len(unique_dates)
    if n <= min_train_periods:
        return []
    remaining = n - min_train_periods
    fold_size = max(remaining // n_folds, 1)
    folds: list[tuple[pd.Timestamp, pd.Timestamp, pd.Timestamp]] = []
    train_end_idx = min_train_periods
    for k in range(n_folds):
        if train_end_idx >= n:
            break
        test_start_idx = train_end_idx
        test_end_idx = min(train_end_idx + fold_size, n - 1) if k < n_folds - 1 else n - 1
        folds.append((unique_dates[train_end_idx - 1], unique_dates[test_start_idx], unique_dates[test_end_idx]))
        train_end_idx = test_end_idx + 1
    return folds


@dataclass(frozen=True)
class FoldResult:
    train_end: str
    test_start: str
    test_end: str
    n_obs: int
    rank_ic: float | None
    monotonic: bool | None


def walk_forward_stability(
    panel: pd.DataFrame,
    score_col: str,
    outcome_col: str,
    as_of_col: str = "as_of",
    n_folds: int = 4,
    min_train_periods: int = 60,
    n_buckets: int = 5,
    min_bucket_history: int = 30,
) -> dict:
    """Measure whether the score-outcome relationship is *consistent*
    across time (정합성), not just present once in full-sample history.
    """
    panel = panel.copy()
    panel[as_of_col] = pd.to_datetime(panel[as_of_col], utc=True)
    folds = walk_forward_folds(panel[as_of_col], n_folds=n_folds, min_train_periods=min_train_periods)
    all_buckets = expanding_quantile_bucket(panel, score_col, as_of_col, n_buckets, min_bucket_history)

    fold_results: list[FoldResult] = []
    for train_end, test_start, test_end in folds:
        test_mask = (panel[as_of_col] > train_end) & (panel[as_of_col] <= test_end)
        test_slice = panel.loc[test_mask]
        if test_slice.empty:
            continue
        ic = rank_information_coefficient(test_slice[score_col], test_slice[outcome_col])
        stats = monotonicity_report(test_slice.assign(_bucket=all_buckets.loc[test_slice.index]), "_bucket", outcome_col)
        fold_results.append(
            FoldResult(
                train_end=str(train_end.date()),
                test_start=str(test_start.date()),
                test_end=str(test_end.date()),
                n_obs=int(len(test_slice)),
                rank_ic=ic,
                monotonic=is_monotonic(stats),
            )
        )

    ics = [f.rank_ic for f in fold_results if f.rank_ic is not None]
    full_ic = rank_information_coefficient(panel[score_col], panel[outcome_col])
    same_sign = None
    if ics and full_ic is not None and full_ic != 0:
        same_sign = float(np.mean([1.0 if (ic > 0) == (full_ic > 0) else 0.0 for ic in ics]))
    monotonic_flags = [f.monotonic for f in fold_results if f.monotonic is not None]

    # Fold-vs-fold sign agreement is a stricter consistency check than
    # comparing each fold to the pooled full-sample IC: a regime flip can
    # average out to a near-zero (or accidentally matching) full-sample IC
    # while individual folds still disagree sharply with each other.
    fold_sign_agreement = None
    signed = [1 if ic > 0 else (-1 if ic < 0 else 0) for ic in ics]
    if signed:
        majority = max(signed.count(1), signed.count(-1))
        fold_sign_agreement = float(majority / len(signed))

    return {
        "folds": [f.__dict__ for f in fold_results],
        "full_sample_rank_ic": full_ic,
        "fold_rank_ic_mean": float(np.mean(ics)) if ics else None,
        "fold_rank_ic_std": float(np.std(ics)) if ics else None,
        "fold_same_sign_as_full_sample": same_sign,
        "fold_sign_agreement": fold_sign_agreement,
        "monotonic_fold_fraction": float(np.mean(monotonic_flags)) if monotonic_flags else None,
    }


def _falsification_status(stats: list[BucketStat], stability: dict) -> str:
    """Apply falsification rules #1 and #3 from Market Decision Framework
    v1.0 section 12: no stable conditional separation, or OOS/fold
    performance collapses (sign-flips) relative to the full-sample result
    or disagrees fold-to-fold.
    """
    monotonic = is_monotonic(stats)
    if monotonic is None:
        return "INSUFFICIENT_DATA"
    if not monotonic:
        return "FALSIFIED_NO_STABLE_SEPARATION"
    same_sign = stability.get("fold_same_sign_as_full_sample")
    sign_agreement = stability.get("fold_sign_agreement")
    monotonic_fraction = stability.get("monotonic_fold_fraction")
    if same_sign is not None and same_sign < 0.5:
        return "FALSIFIED_UNSTABLE_ACROSS_FOLDS"
    if sign_agreement is not None and sign_agreement < 0.8:
        return "FALSIFIED_UNSTABLE_ACROSS_FOLDS"
    if monotonic_fraction is not None and monotonic_fraction < 0.8:
        return "FALSIFIED_UNSTABLE_ACROSS_FOLDS"
    return "NOT_FALSIFIED_CANDIDATE"


def run_experiment_a(
    panel: pd.DataFrame,
    score_col: str,
    price_col: str,
    as_of_col: str = "as_of",
    ticker_col: str = "ticker",
    horizons: Iterable[int] = (5, 20, 60, 120),
    n_buckets: int = 5,
    min_bucket_history: int = 30,
    n_folds: int = 4,
    min_train_periods: int = 60,
) -> dict:
    """Run Experiment A (score monotonicity) with walk-forward stability,
    per horizon. Returns a JSON-serializable report including a
    `falsification_status` per horizon, per the governance rule to record
    falsification status on every market-rule record.
    """
    with_outcomes = attach_forward_outcomes(panel, price_col, horizons, ticker_col, as_of_col)

    horizon_reports = {}
    for h in horizons:
        outcome_col = f"fwd_return_{h}d"
        buckets = expanding_quantile_bucket(with_outcomes, score_col, as_of_col, n_buckets, min_bucket_history)
        bucketed = with_outcomes.assign(_bucket=buckets)
        stats = monotonicity_report(bucketed, "_bucket", outcome_col)
        stability = walk_forward_stability(
            with_outcomes,
            score_col,
            outcome_col,
            as_of_col,
            n_folds,
            min_train_periods,
            n_buckets,
            min_bucket_history,
        )
        horizon_reports[f"{h}d"] = {
            "bucket_stats": [s.__dict__ for s in stats],
            "monotonic_full_sample": is_monotonic(stats),
            "full_sample_rank_ic": rank_information_coefficient(with_outcomes[score_col], with_outcomes[outcome_col]),
            "walk_forward": stability,
            "falsification_status": _falsification_status(stats, stability),
        }
    return {"score_col": score_col, "price_col": price_col, "n_buckets": n_buckets, "horizons": horizon_reports}
