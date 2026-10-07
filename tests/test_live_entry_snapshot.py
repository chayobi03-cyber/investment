"""live_entry_snapshot.py per-product fetch, with Coinbase mocked."""

import json
import sys

import pandas as pd
import pytest

from scripts.crypto import live_entry_snapshot as snap_mod


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
