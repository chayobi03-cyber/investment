"""Parity: mobile/entry.js must reproduce crypto_entry.generate_signals exactly."""

import json
import shutil
import subprocess
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.investment_pipeline.crypto_entry import generate_signals

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")
COMPARED = [
    "ma20", "ma50", "ma200", "ret3", "volume_ratio20", "prior_high60",
    "drawdown60", "trend_ok", "stabilization", "breakout", "zone",
    "entry_state", "entry_reason", "zone_low", "zone_high",
]


def random_walk(seed: int, n: int = 420) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    # Regime-switching drift so trend, pullback, breakout and crash states all occur.
    drift = np.repeat(rng.choice([0.004, -0.006, 0.0, 0.008], size=n // 30 + 1), 30)[:n]
    close = 30000 * np.exp(np.cumsum(drift + rng.normal(0, 0.025, n)))
    open_ = close * np.exp(rng.normal(0, 0.012, n))
    high = np.maximum(open_, close) * (1 + rng.uniform(0, 0.02, n))
    low = np.minimum(open_, close) * (1 - rng.uniform(0, 0.02, n))
    ts = pd.date_range("2024-01-01", periods=n, freq="D", tz="UTC")
    return pd.DataFrame({
        "timestamp": ts, "available_at": ts + timedelta(days=1),
        "open": open_, "high": high, "low": low, "close": close,
        "volume": rng.lognormal(10, 0.4, n),
    })


def run_js(frame: pd.DataFrame) -> list[dict]:
    rows = [
        {
            "timestamp": int(r.timestamp.timestamp() * 1000),
            "available_at": int(r.available_at.timestamp() * 1000),
            "open": r.open, "high": r.high, "low": r.low, "close": r.close, "volume": r.volume,
        }
        for r in frame.itertuples()
    ]
    script = (
        "import { generateSignals } from './mobile/entry.js';"
        "let s='';process.stdin.on('data',d=>s+=d).on('end',()=>{"
        "const out=generateSignals(JSON.parse(s)).map(r=>Object.fromEntries("
        "Object.entries(r).map(([k,v])=>[k,typeof v==='number'&&!Number.isFinite(v)?null:v])));"
        "process.stdout.write(JSON.stringify(out));});"
    )
    proc = subprocess.run(
        [NODE, "--input-type=module", "-e", script],
        input=json.dumps(rows), capture_output=True, text=True, cwd=ROOT, check=True,
    )
    return json.loads(proc.stdout)


@pytest.mark.skipif(NODE is None, reason="node not installed")
@pytest.mark.parametrize("seed", range(8))
def test_js_matches_python(seed):
    frame = random_walk(seed)
    py = generate_signals(frame)
    js = run_js(frame)
    assert len(js) == len(py)
    for i, (jr, (_, pr)) in enumerate(zip(js, py.iterrows())):
        for col in COMPARED:
            pv, jv = pr[col], jr[col]
            if pv is None or (isinstance(pv, float) and np.isnan(pv)) or pv is pd.NA:
                assert jv is None, (i, col, pv, jv)
            elif isinstance(pv, (bool, np.bool_)):
                assert jv is bool(pv), (i, col, pv, jv)
            elif isinstance(pv, str):
                assert jv == pv, (i, col, pv, jv)
            else:
                assert jv == pytest.approx(float(pv), rel=1e-9, abs=1e-12), (i, col, pv, jv)


@pytest.mark.skipif(NODE is None, reason="node not installed")
def test_states_are_exercised():
    states = set()
    for seed in range(8):
        states |= set(generate_signals(random_walk(seed))["entry_state"])
    assert {"B0", "B1", "B2", "B3"} <= states
