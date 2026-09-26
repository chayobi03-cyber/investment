#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time
from pathlib import Path

import pandas as pd
import requests

COINBASE_URL = "https://api.exchange.coinbase.com/products/BTC-USD/candles"
COINBASE_MAX_CANDLES = 300


def fetch(days: int) -> pd.DataFrame:
    if days < 200:
        raise ValueError("days_must_be_at_least_200")

    end = pd.Timestamp.now(tz="UTC").floor("D")
    start = end - pd.Timedelta(days=days + 2)
    rows: list[list[float]] = []

    cursor = end
    while cursor > start:
        batch_start = max(start, cursor - pd.Timedelta(days=COINBASE_MAX_CANDLES))
        params = {
            "granularity": 86400,
            "start": batch_start.isoformat(),
            "end": cursor.isoformat(),
        }
        resp = requests.get(
            COINBASE_URL,
            params=params,
            headers={"User-Agent": "investment-research/crypto-p0-p6-v0.2"},
            timeout=30,
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        rows.extend(batch)
        cursor = batch_start - pd.Timedelta(seconds=1)
        time.sleep(0.10)

    df = pd.DataFrame(rows, columns=["timestamp_s", "low", "high", "open", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp_s"], unit="s", utc=True)
    # Research decision is made at the completed daily candle close.
    df["available_at"] = df["timestamp"] + pd.Timedelta(days=1)
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    result = (
        df[["timestamp", "available_at", "open", "high", "low", "close", "volume"]]
        .sort_values("timestamp")
        .drop_duplicates("timestamp")
    )

    now = pd.Timestamp.now(tz="UTC")
    result = result[result["available_at"] <= now].tail(days).reset_index(drop=True)
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=3000)
    ap.add_argument("--out", type=Path, default=Path("artifacts/crypto/btc_1d_pit.csv"))
    args = ap.parse_args()

    df = fetch(args.days)
    if len(df) < 200:
        raise SystemExit(f"P0_FAIL: only {len(df)} completed daily candles available")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    print(
        f"source=coinbase rows={len(df)} start={df['timestamp'].min()} "
        f"end={df['timestamp'].max()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
