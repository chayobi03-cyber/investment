"""Walk-forward fold layout shared by p0_p6, decomposition and asset review must not drift."""

import json
from datetime import timedelta

import numpy as np
import pandas as pd
import pytest

from scripts.crypto import run_asset_review_v0_1 as review
from scripts.crypto import run_crypto_decomposition_v0_2 as decomposition
from scripts.crypto import run_crypto_p0_p6_v0_2 as p0_p6
from src.investment_pipeline.crypto_entry import (
    V02_COOLDOWN_BARS,
    add_forward_outcomes,
    cluster_episodes,
    generate_signals,
)

CFG = json.loads(open("config/crypto_asset_review_v0.1.json", encoding="utf-8").read())

# (n, [(train_rows == test_start, test_end), ...]) for the frozen layout:
# test_size = max(100, n // 10), first train_end = max(200, int(n * 0.50)).
GOLDEN_FOLDS = [
    (0, []),
    (199, []),
    (299, []),
    (300, [(200, 300)]),
    (399, [(200, 300)]),
    (400, [(200, 300), (300, 400)]),
    (650, [(325, 425), (425, 525), (525, 625)]),
    (1000, [(500, 600), (600, 700), (700, 800), (800, 900), (900, 1000)]),
    (1001, [(500, 600), (600, 700), (700, 800), (800, 900), (900, 1000)]),
    (1099, [(549, 658), (658, 767), (767, 876), (876, 985), (985, 1094)]),
    (1100, [(550, 660), (660, 770), (770, 880), (880, 990), (990, 1100)]),
    (3000, [(1500, 1800), (1800, 2100), (2100, 2400), (2400, 2700), (2700, 3000)]),
]


def walk(seed: int, n: int, vol: float = 0.025) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    drift = np.repeat(rng.choice([0.004, -0.006, 0.0, 0.008], size=n // 30 + 1), 30)[:n]
    close = 100 * np.exp(np.cumsum(drift + rng.normal(0, vol, n)))
    open_ = close * np.exp(rng.normal(0, 0.01, n))
    ts = pd.date_range("2020-01-01", periods=n, freq="D", tz="UTC")
    return pd.DataFrame({
        "timestamp": ts, "available_at": ts + timedelta(days=1),
        "open": open_, "high": np.maximum(open_, close) * 1.01, "low": np.minimum(open_, close) * 0.99,
        "close": close, "volume": rng.lognormal(16, 0.3, n),
    })


@pytest.mark.parametrize("n,bounds", GOLDEN_FOLDS)
def test_fold_boundaries_are_pinned(n, bounds):
    folds = p0_p6.fold_boundaries(n)
    assert decomposition.fold_boundaries(n) == folds
    assert folds == [
        {"split_id": f"WF{i + 1:02d}", "train_rows": a, "test_start": a, "test_end": b}
        for i, (a, b) in enumerate(bounds)
    ]
    for fold in folds:
        assert list(fold) == ["split_id", "train_rows", "test_start", "test_end"]
        assert all(type(fold[k]) is int for k in ("train_rows", "test_start", "test_end"))


def test_p0_p6_walk_forward_is_pinned():
    signals = add_forward_outcomes(
        cluster_episodes(generate_signals(walk(1, 650)), cooldown_bars=V02_COOLDOWN_BARS)
    )
    expected = []
    for i, (a, b) in enumerate(dict(GOLDEN_FOLDS)[650]):
        test = signals.iloc[a:b]
        primary = test[test["primary_event"] & test["entry_state"].isin(["B2", "B3", "B4"])]
        expected.append({
            "split_id": f"WF{i + 1:02d}",
            "train_rows": a,
            "test_rows": b - a,
            "test_start": str(signals["timestamp"].iloc[a]),
            "test_end": str(signals["timestamp"].iloc[b - 1]),
            "threshold_retuned": False,
            "metrics": p0_p6.event_stats(primary),
        })
    out = p0_p6.walk_forward(signals)
    assert json.dumps(out, default=str) == json.dumps(expected, default=str)
    assert all(isinstance(f["test_start"], str) and isinstance(f["test_end"], str) for f in out)


def test_decomposition_walk_forward_rows_follow_the_folds():
    raw = walk(2, 650)
    result = decomposition.decompose(raw)
    rows = result["walk_forward"]
    assert [(r["split_id"], r["train_rows"], r["test_start"], r["test_end"]) for r in rows] == [
        (f"WF{i + 1:02d}", a, a, b) for i, (a, b) in enumerate(dict(GOLDEN_FOLDS)[650])
    ]
    assert list(rows[0])[:4] == ["split_id", "train_rows", "test_start", "test_end"]


@pytest.mark.parametrize("scaled", [False, True])
def test_asset_review_walk_forward_is_pinned(monkeypatch, scaled):
    raw, btc = walk(3, 650, vol=0.04), walk(4, 650)
    assert len(review.signals_for(raw, 1.0)) == len(raw)
    cfg = CFG["scaled_variant"] if scaled else None
    seen_rows = []
    real_scale_factor = review.scale_factor

    def spy(asset, base, rows, c):
        seen_rows.append(rows)
        return real_scale_factor(asset, base, rows, c)

    monkeypatch.setattr(review, "scale_factor", spy)
    out = review.walk_forward_summary(raw, btc, cfg)
    bounds = dict(GOLDEN_FOLDS)[650]
    assert seen_rows == ([a for a, _ in bounds] if scaled else [])
    assert out["folds_total"] == len(bounds)
    assert [f["test_start"] for f in out["folds"]] == [str(raw["timestamp"].iloc[a].date()) for a, _ in bounds]
    for fold, (a, b) in zip(out["folds"], bounds, strict=True):
        signals = review.signals_for(raw, fold["k"])
        r20 = pd.to_numeric(
            review.primary_events(signals.iloc[a:b])["forward_return_20d"], errors="coerce"
        ).dropna()
        assert fold["events"] == len(review.primary_events(signals.iloc[a:b]))
        assert fold["median_return_20d"] == (None if r20.empty else float(r20.median()))
