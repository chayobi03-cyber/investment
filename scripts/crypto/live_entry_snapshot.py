#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import requests

from src.investment_pipeline.crypto_entry import generate_signals

KLINES = "https://api.exchange.coinbase.com/products/BTC-USD/candles"
TICKER = "https://api.exchange.coinbase.com/products/BTC-USD/ticker"


def get_daily(days: int = 365) -> pd.DataFrame:
    end = pd.Timestamp.now(tz="UTC").floor("D")
    start = end - pd.Timedelta(days=days + 2)
    rows: list[list[float]] = []
    cursor = end

    while cursor > start:
        batch_start = max(start, cursor - pd.Timedelta(days=300))
        resp = requests.get(
            KLINES,
            params={
                "granularity": 86400,
                "start": batch_start.isoformat(),
                "end": cursor.isoformat(),
            },
            headers={"User-Agent": "investment-research/crypto-live-v0.2"},
            timeout=30,
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        rows.extend(batch)
        cursor = batch_start - pd.Timedelta(seconds=1)

    df = pd.DataFrame(
        rows,
        columns=["timestamp_s", "low", "high", "open", "close", "volume"],
    )
    df["timestamp"] = pd.to_datetime(df["timestamp_s"], unit="s", utc=True)
    df["available_at"] = df["timestamp"] + pd.Timedelta(days=1)
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    now = pd.Timestamp.now(tz="UTC")
    return (
        df[df["available_at"] <= now][
            ["timestamp", "available_at", "open", "high", "low", "close", "volume"]
        ]
        .sort_values("timestamp")
        .drop_duplicates("timestamp")
        .tail(days)
        .reset_index(drop=True)
    )


def get_live_price() -> float:
    resp = requests.get(
        TICKER,
        headers={"User-Agent": "investment-research/crypto-live-v0.2"},
        timeout=15,
    )
    resp.raise_for_status()
    return float(resp.json()["price"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=Path("artifacts/crypto/live_entry.json"))
    args = ap.parse_args()

    daily = get_daily(365)
    if len(daily) < 200:
        raise SystemExit("DATA_NOT_READY: insufficient completed daily history")

    signals = generate_signals(daily)
    last = signals.iloc[-1]
    live = get_live_price()

    prior_high60 = float(last["prior_high60"])
    z1_high = prior_high60 * 0.95
    z1_low = prior_high60 * 0.92
    z2_low = prior_high60 * 0.88
    breakout = prior_high60 * 1.005

    if live >= breakout:
        live_zone = "BREAKOUT"
    elif live > z1_high:
        live_zone = "Z0"
    elif live > z1_low:
        live_zone = "Z1"
    elif live > z2_low:
        live_zone = "Z2"
    else:
        live_zone = "Z3"

    core_state = str(last["entry_state"])
    stabilization = bool(last["stabilization"])
    trend_ok = bool(last["trend_ok"])

    result = {
        "status": "RESEARCH_ONLY_NOT_VALIDATED",
        "rule_version": "crypto-market-regime-entry-v0.2",
        "asset": "BTCUSDT",
        "data_source": "Coinbase BTC-USD public API",
        "decision_bar": str(last["timestamp"]),
        "decision_bar_available_at": str(last["available_at"]),
        "live_price": live,
        "daily_core_state": core_state,
        "daily_zone": str(last["zone"]),
        "live_zone": live_zone,
        "trend_ok": trend_ok,
        "stabilization": stabilization,
        "prior_high60": prior_high60,
        "research_levels": {
            "Z1_upper": z1_high,
            "Z1_lower": z1_low,
            "Z2_lower": z2_low,
            "breakout_confirmation": breakout,
        },
        "promotion_gate": {
            "threshold_evidence": "FAIL",
            "full_buy_permission": "BLOCKED",
            "automatic_order": False,
        },
        "buy_allowed": False,
        "action": "BLOCKED_UNVALIDATED",
        "invalidation": [
            "P0_DATA_NOT_READY",
            "THRESHOLD_OOS_FAIL",
            "FULL_PERMISSION_LAYER_NOT_PROMOTED",
        ],
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
