#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import requests

from src.investment_pipeline.crypto_entry import generate_signals

KLINES = "https://api.binance.com/api/v3/klines"
PRICE = "https://api.binance.com/api/v3/ticker/price"


def get_daily(days: int = 365) -> pd.DataFrame:
    resp = requests.get(
        KLINES,
        params={"symbol": "BTCUSDT", "interval": "1d", "limit": days},
        timeout=30,
    )
    resp.raise_for_status()
    rows = resp.json()
    now = pd.Timestamp.now(tz="UTC")

    df = pd.DataFrame(
        rows,
        columns=[
            "timestamp_ms", "open", "high", "low", "close", "volume",
            "close_time_ms", "quote_volume", "trades",
            "taker_buy_base", "taker_buy_quote", "ignore",
        ],
    )
    df["timestamp"] = pd.to_datetime(df["timestamp_ms"], unit="ms", utc=True)
    df["available_at"] = pd.to_datetime(df["close_time_ms"], unit="ms", utc=True)
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df[df["available_at"] <= now][
        ["timestamp", "available_at", "open", "high", "low", "close", "volume"]
    ].reset_index(drop=True)


def get_live_price() -> float:
    resp = requests.get(PRICE, params={"symbol": "BTCUSDT"}, timeout=15)
    resp.raise_for_status()
    return float(resp.json()["price"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=Path("artifacts/crypto/live_entry.json"))
    args = ap.parse_args()

    daily = get_daily(365)
    signals = generate_signals(daily)
    last = signals.iloc[-1]
    live = get_live_price()

    prior_high60 = float(last["prior_high60"])
    z1_high = prior_high60 * 0.95
    z1_low = prior_high60 * 0.92
    z2_high = z1_low
    z2_low = prior_high60 * 0.88

    if live > z1_high:
        live_zone = "Z0"
    elif live > z1_low:
        live_zone = "Z1"
    elif live > z2_low:
        live_zone = "Z2"
    else:
        live_zone = "Z3"

    result = {
        "status": "RESEARCH_ONLY",
        "asset": "BTCUSDT",
        "decision_bar": str(last["timestamp"]),
        "decision_bar_available_at": str(last["available_at"]),
        "live_price": live,
        "daily_state": str(last["entry_state"]),
        "daily_zone": str(last["zone"]),
        "daily_trend_ok": bool(last["trend_ok"]),
        "daily_stabilization": bool(last["stabilization"]),
        "live_zone": live_zone,
        "prior_high60": prior_high60,
        "triggers": {
            "Z1_enter": z1_high,
            "Z2_enter": z1_low,
            "Z3_enter": z2_low,
        },
        "distance_to_first_trigger_pct": (live / z1_high - 1.0) * 100.0,
        "action": (
            "WAIT"
            if live > z1_high
            else "WATCH_Z1_CONFIRMATION"
            if live > z1_low
            else "WATCH_Z2_CONFIRMATION"
            if live > z2_low
            else "DEEP_DISLOCATION_WATCH"
        ),
        "automatic_order": False,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
