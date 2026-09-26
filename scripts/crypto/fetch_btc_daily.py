#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time
from pathlib import Path

import pandas as pd
import requests

BASE_URL = "https://api.binance.com/api/v3/klines"


def fetch(days: int) -> pd.DataFrame:
    if days < 200:
        raise ValueError("days_must_be_at_least_200")

    rows: list[list] = []
    end_time = int(time.time() * 1000)

    while len(rows) < days:
        params = {
            "symbol": "BTCUSDT",
            "interval": "1d",
            "limit": 1000,
            "endTime": end_time,
        }
        resp = requests.get(BASE_URL, params=params, timeout=30)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        rows = batch + rows
        earliest = int(batch[0][0])
        if len(batch) < 1000:
            break
        end_time = earliest - 1
        time.sleep(0.05)

    rows = rows[-days:]
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
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    result = (
        df[
            ["timestamp", "available_at", "open", "high", "low", "close", "volume"]
        ]
        .sort_values("timestamp")
        .drop_duplicates("timestamp")
    )

    now = pd.Timestamp.now(tz="UTC")
    return result[result["available_at"] <= now].reset_index(drop=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=3000)
    ap.add_argument("--out", type=Path, default=Path("artifacts/crypto/btc_1d_pit.csv"))
    args = ap.parse_args()

    df = fetch(args.days)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    print(
        f"rows={len(df)} start={df['timestamp'].min()} "
        f"end={df['timestamp'].max()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
