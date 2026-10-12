"""Parity: mobile/entry.js liveZone/buildSnapshot must match live_entry_snapshot.py exactly."""

import json
import math
import shutil
import subprocess
import sys
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from scripts.crypto import live_entry_snapshot as snap_mod
from src.investment_pipeline.crypto_entry import generate_signals

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")
LEVEL_KEYS = ["Z1_upper", "Z1_lower", "Z2_lower", "breakout_confirmation"]


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
    # At, one ulp above and one ulp below each boundary, plus far-away prices.
    out = [h * 2.0, h, h * 0.5, 0.0]
    for b in (h * 1.005, h * 0.95, h * 0.92, h * 0.88):
        out += [b, math.nextafter(b, math.inf), math.nextafter(b, -math.inf)]
    return out


def grid() -> list[tuple[float, float]]:
    rng = np.random.default_rng(3)
    hs = [1.0, 100.0, 30000.0, 79967.53562553386, 123456.789]
    hs += [float(x) for x in rng.uniform(1, 2e5, 40)]
    cases = [(p, h) for h in hs for p in boundary_prices(h)]
    # Price form and drawdown form disagree here; the price form is the frozen one.
    cases.append((75969.15884425717, 79967.53562553386))
    # Missing prior_high60 never matches a level and falls through to Z3.
    cases += [(p, math.nan) for p in (0.0, 1.0, 1e9)]
    return cases


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


def run_js(payload: dict) -> dict:
    # NaN is not valid JSON, so a missing level travels as null and becomes NaN in JS.
    script = (
        "import { liveZone, researchLevels, buildSnapshot } from './mobile/entry.js';"
        "let s='';process.stdin.on('data',d=>s+=d).on('end',()=>{"
        "const p=JSON.parse(s);const n=(h)=>h===null?NaN:h;"
        "const zones=p.cases.map(([x,h])=>liveZone(x,n(h)));"
        "const levels=p.hs.map((h)=>researchLevels(n(h)));"
        "const snaps=p.prices.map((x)=>buildSnapshot(p.rows,x,'test'));"
        "process.stdout.write(JSON.stringify({zones,levels,"
        "snaps:snaps.map((q)=>({live_zone:q.live_zone,prior_high60:q.prior_high60,"
        "research_levels:q.research_levels}))}));});"
    )
    proc = subprocess.run(
        [NODE, "--input-type=module", "-e", script],
        input=json.dumps(payload), capture_output=True, text=True, cwd=ROOT, check=True,
    )
    return json.loads(proc.stdout)


def js_rows(frame: pd.DataFrame) -> list[dict]:
    return [
        {
            "timestamp": int(r.timestamp.timestamp() * 1000),
            "available_at": int(r.available_at.timestamp() * 1000),
            "open": r.open, "high": r.high, "low": r.low, "close": r.close, "volume": r.volume,
        }
        for r in frame.itertuples()
    ]


def as_json(h: float):
    return None if math.isnan(h) else h


def test_python_live_zone_matches_golden_grid():
    for p, h in grid():
        assert snap_mod.live_zone(p, h) == golden_zone(p, h), (p, h)


@pytest.mark.skipif(NODE is None, reason="node not installed")
def test_js_live_zone_matches_python_grid():
    cases = grid()
    hs = sorted({h for _, h in cases if not math.isnan(h)}) + [math.nan]
    js = run_js({
        "cases": [[p, as_json(h)] for p, h in cases],
        "hs": [as_json(h) for h in hs], "rows": [], "prices": [],
    })
    for (p, h), jz in zip(cases, js["zones"], strict=True):
        assert jz == snap_mod.live_zone(p, h) == golden_zone(p, h), (p, h)
    assert set(js["zones"]) == {"BREAKOUT", "Z0", "Z1", "Z2", "Z3"}
    for h, jl in zip(hs, js["levels"], strict=True):
        pl = snap_mod.research_levels(h)
        assert list(jl) == list(pl) == LEVEL_KEYS
        if math.isnan(h):
            assert all(v is None for v in jl.values())
            assert all(math.isnan(v) for v in pl.values())
        else:
            assert jl == pl == {
                "Z1_upper": h * 0.95, "Z1_lower": h * 0.92,
                "Z2_lower": h * 0.88, "breakout_confirmation": h * 1.005,
            }, h


@pytest.mark.skipif(NODE is None, reason="node not installed")
def test_js_snapshot_matches_python_snapshot(tmp_path, monkeypatch):
    daily = fixed_daily()
    h = float(generate_signals(daily).iloc[-1]["prior_high60"])
    prices = boundary_prices(h)
    js = run_js({"cases": [], "hs": [], "rows": js_rows(daily), "prices": prices})
    monkeypatch.setattr(snap_mod, "get_daily", lambda product, days: daily)
    for price, jsnap in zip(prices, js["snaps"], strict=True):
        monkeypatch.setattr(snap_mod, "get_live_price", lambda product, p=price: p)
        out = tmp_path / "s.json"
        monkeypatch.setattr(sys, "argv", ["x", "--output", str(out)])
        assert snap_mod.main() == 0
        py = json.loads(out.read_text())
        assert jsnap["prior_high60"] == py["prior_high60"] == h
        assert jsnap["live_zone"] == py["live_zone"] == golden_zone(price, h), price
        assert list(jsnap["research_levels"]) == list(py["research_levels"]) == LEVEL_KEYS
        assert jsnap["research_levels"] == py["research_levels"]
