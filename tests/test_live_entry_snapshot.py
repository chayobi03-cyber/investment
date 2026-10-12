"""live_entry_snapshot.py per-product fetch, with Coinbase mocked."""

import json
import math
import sys
from datetime import timedelta

import numpy as np
import pandas as pd
import pytest

from scripts.crypto import live_entry_snapshot as snap_mod
from src.investment_pipeline.crypto_entry import generate_signals


class FakeResp:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self.payload


def fake_get_factory(calls):
    def fake_get(url, params=None, **_):
        calls.append(url)
        if url.endswith("/ticker"):
            return FakeResp({"price": "150.0"})
        start = pd.Timestamp(params["start"]).timestamp()
        end = pd.Timestamp(params["end"]).timestamp()
        rows = []
        t = int(start // 86400 * 86400)
        while t <= end:
            px = 100 + (t / 86400) % 50
            rows.append([t, px * 0.99, px * 1.01, px, px * 1.001, 10.0])
            t += 86400
        return FakeResp(rows[::-1])
    return fake_get


@pytest.mark.parametrize("product,asset", [("BTC-USD", "BTCUSDT"), ("ETH-USD", "ETHUSDT"), ("SOL-USD", "SOLUSDT")])
def test_product_selects_endpoint_and_asset(tmp_path, monkeypatch, product, asset):
    calls = []
    monkeypatch.setattr(snap_mod.requests, "get", fake_get_factory(calls))
    out = tmp_path / "s.json"
    argv = ["x", "--output", str(out)] + ([] if product == "BTC-USD" else ["--product", product])
    monkeypatch.setattr(sys, "argv", argv)
    assert snap_mod.main() == 0
    data = json.loads(out.read_text())
    assert data["asset"] == asset
    assert data["data_source"] == f"Coinbase {product} public API"
    assert data["buy_allowed"] is False
    assert calls and all(f"/products/{product}/" in u for u in calls)


SNAPSHOT_KEYS = [
    "status", "rule_version", "asset", "data_source", "decision_bar",
    "decision_bar_available_at", "live_price", "daily_core_state", "daily_zone",
    "live_zone", "trend_ok", "stabilization", "prior_high60", "research_levels",
    "promotion_gate", "buy_allowed", "action", "invalidation",
]


def fixed_daily(n: int = 365) -> pd.DataFrame:
    rng = np.random.default_rng(11)
    close = 30000 * np.exp(np.cumsum(rng.normal(0.001, 0.02, n)))
    open_ = close * np.exp(rng.normal(0, 0.01, n))
    ts = pd.date_range("2024-01-01", periods=n, freq="D", tz="UTC")
    return pd.DataFrame({
        "timestamp": ts, "available_at": ts + timedelta(days=1),
        "open": open_, "high": np.maximum(open_, close) * 1.01,
        "low": np.minimum(open_, close) * 0.99, "close": close,
        "volume": rng.lognormal(10, 0.4, n),
    })


def golden_zone(price: float, h: float) -> str:
    # Frozen multiplicative ladder: >= breakout, then strict > for Z0/Z1/Z2.
    if price >= h * 1.005:
        return "BREAKOUT"
    if price > h * 0.95:
        return "Z0"
    if price > h * 0.92:
        return "Z1"
    if price > h * 0.88:
        return "Z2"
    return "Z3"


def boundary_prices(h: float) -> list[float]:
    out = [h * 2.0, h, h * 0.5]
    for b in (h * 1.005, h * 0.95, h * 0.92, h * 0.88):
        out += [b, math.nextafter(b, math.inf), math.nextafter(b, -math.inf)]
    return out


def test_live_zone_and_research_levels_are_pinned(tmp_path, monkeypatch):
    daily = fixed_daily()
    h = float(generate_signals(daily).iloc[-1]["prior_high60"])
    monkeypatch.setattr(snap_mod, "get_daily", lambda product, days: daily)
    zones = set()
    for price in boundary_prices(h):
        monkeypatch.setattr(snap_mod, "get_live_price", lambda product, p=price: p)
        out = tmp_path / "s.json"
        monkeypatch.setattr(sys, "argv", ["x", "--output", str(out)])
        assert snap_mod.main() == 0
        data = json.loads(out.read_text())
        assert list(data) == SNAPSHOT_KEYS
        assert data["prior_high60"] == h
        assert data["live_zone"] == golden_zone(price, h), price
        zones.add(data["live_zone"])
        levels = data["research_levels"]
        assert list(levels) == ["Z1_upper", "Z1_lower", "Z2_lower", "breakout_confirmation"]
        assert levels == {
            "Z1_upper": h * 0.95, "Z1_lower": h * 0.92,
            "Z2_lower": h * 0.88, "breakout_confirmation": h * 1.005,
        }
    assert zones == {"BREAKOUT", "Z0", "Z1", "Z2", "Z3"}
