"""Asset review v0.1: scaled variant, k estimation, history handling, end to end."""

import json
import sys
from datetime import timedelta

import numpy as np
import pandas as pd
import pytest

from scripts.crypto import run_asset_review_v0_1 as review
from src.investment_pipeline.crypto_entry import generate_signals

CFG = json.loads(open("config/crypto_asset_review_v0.1.json", encoding="utf-8").read())


def walk(seed: int, n: int, vol: float = 0.025, start="2018-01-01", base_returns=None) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    drift = np.repeat(rng.choice([0.004, -0.006, 0.0, 0.008], size=n // 30 + 1), 30)[:n]
    rets = drift + rng.normal(0, vol, n) if base_returns is None else base_returns
    close = 100 * np.exp(np.cumsum(rets))
    open_ = close * np.exp(rng.normal(0, 0.01, n))
    ts = pd.date_range(start, periods=n, freq="D", tz="UTC")
    return pd.DataFrame({
        "timestamp": ts, "available_at": ts + timedelta(days=1),
        "open": open_, "high": np.maximum(open_, close) * 1.01, "low": np.minimum(open_, close) * 0.99,
        "close": close, "volume": rng.lognormal(16, 0.3, n),
    })


def test_k_of_one_reproduces_frozen_rule():
    raw = walk(1, 600)
    frozen = generate_signals(raw)
    scaled = review.signals_for(raw, 1.0)
    assert (scaled["entry_state"].values == frozen["entry_state"].values).all()
    assert (scaled["zone"].values == frozen["zone"].values).all()


def test_scaled_zones_are_frozen_zones_of_normalised_drawdown():
    raw = walk(2, 600)
    k = 2.0
    out = review.signals_for(raw, k)
    dd = generate_signals(raw)["drawdown60"] / k
    expected = np.select(
        [dd.isna(), dd > -0.05, dd > -0.08, dd > -0.12], ["UNKNOWN", "Z0", "Z1", "Z2"], default="Z3"
    )
    assert (out["zone"].values == expected).all()
    # outcomes and the baseline keep the real drawdown
    assert out["drawdown60"].equals(generate_signals(raw)["drawdown60"])
    assert set(out["entry_state"]) - set(generate_signals(raw)["entry_state"]) <= {"B1", "B2", "B3", "B4"}


def test_scale_factor_uses_vol_ratio_and_clips():
    btc = walk(3, 800)
    btc_rets = np.log(btc["close"]).diff().fillna(0).to_numpy()
    double = walk(4, 800, base_returns=btc_rets * 2)
    assert review.scale_factor(double, btc, 600, CFG["scaled_variant"]) == pytest.approx(2.0, abs=0.01)
    wild = walk(5, 800, base_returns=btc_rets * 5)
    assert review.scale_factor(wild, btc, 600, CFG["scaled_variant"]) == 3.0


def test_scale_factor_only_sees_development_rows():
    btc = walk(6, 800)
    btc_rets = np.log(btc["close"]).diff().fillna(0).to_numpy()
    rets = np.concatenate([btc_rets[:600] * 1.5, btc_rets[600:] * 4])  # regime change after dev
    asset = walk(7, 800, base_returns=rets)
    assert review.scale_factor(asset, btc, 600, CFG["scaled_variant"]) == pytest.approx(1.5, abs=0.01)


def test_latest_contiguous_drops_history_before_a_listing_gap():
    old = walk(8, 300, start="2019-01-01")
    new = walk(9, 500, start="2022-01-01")
    out, gaps = review.latest_contiguous(pd.concat([old, new], ignore_index=True), 1)
    assert gaps == 1
    assert out["timestamp"].min() == new["timestamp"].min() and len(out) == 500


def test_short_outage_is_kept_but_listing_halt_is_cut():
    a = walk(20, 300, start="2020-01-01")
    out, gaps = review.latest_contiguous(a.drop(index=[100, 101, 102]).reset_index(drop=True), 7)
    assert gaps == 0 and len(out) == 297


def test_bad_series_is_reported_not_fatal():
    bad = walk(21, 500)
    bad.loc[10, "high"] = bad.loc[10, "low"] * 0.5  # invalid high
    r = review.review_asset("DOGE", bad, walk(22, 500), CFG)
    assert r["status"] == "P0_FAIL" and "invalid highs" in r["reason"]


def test_end_to_end_report(tmp_path, monkeypatch, capsys):
    frames = []
    for i, (sym, n) in enumerate([("BTC", 2400), ("ETH", 2400), ("SOL", 1500), ("XRP", 2000), ("SUI", 700)]):
        f = walk(10 + i, n, vol=0.025 if sym == "BTC" else 0.04)
        f["timestamp"] = f["timestamp"] + (pd.Timestamp("2026-10-01", tz="UTC") - f["timestamp"].max())
        f["available_at"] = f["timestamp"] + timedelta(days=1)
        f["asset"] = sym
        frames.append(f)
    csv = tmp_path / "multi.csv"
    pd.concat(frames).to_csv(csv, index=False)
    out = tmp_path / "review.json"
    summary = tmp_path / "summary.md"
    monkeypatch.setattr(sys, "argv", ["x", str(csv), "--output", str(out), "--summary", str(summary)])
    assert review.main() == 0

    data = json.loads(out.read_text())
    by = {a["asset"]: a for a in data["assets"]}
    assert data["buy_allowed"] is False
    assert set(by["BTC"]["variants"]) == {"frozen"}
    assert {by[s]["tier"] for s in ("BTC", "ETH", "SOL")} == {"MONITORED"}
    assert by["ETH"]["rule_fit"] in {"FROZEN_PASS", "SCALED_PASS", "BOTH_PASS", "NEITHER_PASS"}
    assert by["ETH"]["variants"]["scaled"]["k"] > 1.0
    assert set(by["ETH"]["variants"]["frozen"]["threshold_validation"]["checks"]) == {
        "minimum_oos_events", "oos_20d_median_positive", "oos_60d_median_positive",
        "oos_20d_positive_rate_ge_50pct", "oos_60d_positive_rate_ge_50pct",
        "oos_20d_median_mae_gt_minus_15pct", "oos_20d_not_materially_below_simple_baseline",
    }
    assert by["SUI"]["screen"]["history_ok"] is False and by["SUI"]["tier"] == "NOT_RECOMMENDED"
    assert {a.split(":")[0] for a in data["recommendation_order"]} == {"XRP", "SUI"}
    assert {"DOGE", "LINK"} <= set(data["missing_assets"])
    assert "| ETH |" in summary.read_text()
