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
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/crypto/live_entry.json"),
    )
    args = ap.parse_args()

    daily = get_daily(365)
    signals = generate_signals(daily)
    last = signals.iloc[-1]
    live = get_live_price()

    prior_high60 = float(last["prior_high60"])
    buy1_trigger = prior_high60 * 0.95
    buy2_trigger = prior_high60 * 0.92
    buy3_trigger = prior_high60 * 0.88
    breakout_trigger = prior_high60

    daily_trend = bool(last["trend_ok"])
    daily_stabilization = bool(last["stabilization"])
    close_gte_ma20 = bool(last["close"] >= last["ma20"]) if pd.notna(last["ma20"]) else False
    close_gte_ma50 = bool(last["close"] >= last["ma50"]) if pd.notna(last["ma50"]) else False

    if live > breakout_trigger:
        live_zone = "BREAKOUT"
    elif live > buy1_trigger:
        live_zone = "Z0"
    elif live > buy2_trigger:
        live_zone = "Z1"
    elif live > buy3_trigger:
        live_zone = "Z2"
    else:
        live_zone = "Z3"

    if not daily_trend:
        execution_state = "BLOCKED"
    elif live >= prior_high60 * 0.98 and live < breakout_trigger:
        execution_state = "WAIT_NO_CHASE"
    elif live <= buy1_trigger and live > buy2_trigger and daily_stabilization and close_gte_ma20:
        execution_state = "BUY_1_READY"
    elif live <= buy2_trigger and live > buy3_trigger and daily_stabilization and close_gte_ma20:
        execution_state = "BUY_2_READY"
    elif live <= buy3_trigger and daily_stabilization and close_gte_ma20 and close_gte_ma50:
        execution_state = "BUY_3_READY"
    elif live > breakout_trigger and daily_trend:
        execution_state = "BREAKOUT_CONFIRMATION_WATCH"
    else:
        execution_state = "WAIT_CONFIRMATION"

    result = {
        "status": "RESEARCH_ONLY",
        "asset": "BTCUSDT",
        "decision_bar": str(last["timestamp"]),
        "decision_bar_available_at": str(last["available_at"]),
        "live_price": live,
        "daily_state": str(last["entry_state"]),
        "daily_zone": str(last["zone"]),
        "live_zone": live_zone,
        "daily_trend_ok": daily_trend,
        "daily_stabilization": daily_stabilization,
        "reference_prior_60d_high": prior_high60,
        "execution_state": execution_state,
        "purchase_plan": {
            "BUY_1": {
                "trigger_price": buy1_trigger,
                "allocation_of_crypto_sleeve": 0.20,
                "requires": ["Z1_REACHED", "3D_RETURN_GT_0", "CLOSE_GTE_MA20"],
            },
            "BUY_2": {
                "trigger_price": buy2_trigger,
                "allocation_of_crypto_sleeve": 0.25,
                "requires": ["Z2_REACHED", "3D_RETURN_GT_0", "CLOSE_GTE_MA20"],
            },
            "BUY_3": {
                "trigger_price": buy3_trigger,
                "allocation_of_crypto_sleeve": 0.30,
                "requires": [
                    "Z3_REACHED",
                    "3D_RETURN_GT_0",
                    "CLOSE_GTE_MA20",
                    "CLOSE_GTE_MA50",
                ],
            },
            "BUY_4": {
                "trigger_price": "confirmation event",
                "allocation_of_crypto_sleeve": 0.25,
                "requires": [
                    "stabilization_persistence",
                    "independent_risk_cluster_confirmation",
                ],
            },
            "BREAKOUT": {
                "trigger_price": breakout_trigger,
                "execution": "next_session_after_confirmed_daily_close",
                "allocation": "separate research path",
            },
        },
        "current_confirmation": {
            "ret_3d_positive": float(last["ret3"]) > 0 if pd.notna(last["ret3"]) else False,
            "close_gte_ma20": close_gte_ma20,
            "close_gte_ma50": close_gte_ma50,
        },
        "invalidation": [
            "STRUCTURAL_TREND_BREAK",
            "DATA_NOT_READY",
            "MULTI_SHOCK",
            "SEVERE_SYSTEMIC_STRESS",
        ],
        "automatic_order": False,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
