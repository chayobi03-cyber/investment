#!/usr/bin/env python3
"""Build a reproducible daily PIT-like research panel from historical vendor data.

This is a vendor-history proxy, not an archival revision-history reconstruction.
\`available_at == observed_at\` is only a market-data timing convention;
fundamentals are not synthesized here and remain unavailable for P6.
"""
from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yfinance as yf

from scripts.market_monitor.decision_pipeline import build_observation, stable_id

SOURCE = "yahoo_finance_history"
SOURCE_ID = "yahoo_finance_history"
RULE_VERSION = "observation-v3.0-pit-proxy"
PIT_STATUS = "VENDOR_HISTORY_PROXY"
START_DATE = "2000-01-01"

SPLITS = (
    ("development", "2000-01-01", "2019-01-01"),
    ("validation", "2019-01-01", "2022-01-01"),
    ("oos", "2022-01-01", "2100-01-01"),
)

SYMBOLS = {
    "KOSPI": ("benchmark", "^KS11"),
    "KOSDAQ": ("benchmark", "^KQ11"),
    "SP500": ("benchmark", "^GSPC"),
    "NASDAQ": ("benchmark", "^IXIC"),
    "SOX": ("benchmark", "^SOX"),
    "VIX": ("macro", "^VIX"),
    "US10Y": ("macro", "^TNX"),
    "USD_KRW": ("macro", "KRW=X"),
    "USD_JPY": ("macro", "JPY=X"),
    "DXY": ("macro", "DX-Y.NYB"),
    "WTI": ("macro", "CL=F"),
    "BRENT": ("macro", "BZ=F"),
    "GOLD": ("macro", "GC=F"),
    "SAMSUNG": ("equity", "005930.KS"),
    "SK_HYNIX": ("equity", "000660.KS"),
    "SK_SQUARE": ("equity", "402340.KS"),
    "SAMSUNG_SDI": ("equity", "006400.KS"),
    "KB_FIN": ("equity", "105560.KS"),
    "HYUNDAI": ("equity", "005380.KS"),
    "SAMSUNG_FIRE": ("equity", "000810.KS"),
    "SK_INNO": ("equity", "096770.KS"),
    "DOOSAN_ENERBILITY": ("equity", "034020.KS"),
    "NAVER": ("equity", "035420.KS"),
    "SAMSUNG_BIO": ("equity", "207940.KS"),
    "TSM": ("equity", "TSM"),
    "AVGO": ("equity", "AVGO"),
}

ASSET_BENCHMARK = {
    "SAMSUNG": "KOSPI",
    "SK_HYNIX": "KOSPI",
    "SK_SQUARE": "KOSPI",
    "SAMSUNG_SDI": "KOSPI",
    "KB_FIN": "KOSPI",
    "HYUNDAI": "KOSPI",
    "SAMSUNG_FIRE": "KOSPI",
    "SK_INNO": "KOSPI",
    "DOOSAN_ENERBILITY": "KOSPI",
    "NAVER": "KOSPI",
    "SAMSUNG_BIO": "KOSPI",
    "TSM": "NASDAQ",
    "AVGO": "NASDAQ",
}

LEADERS = list(ASSET_BENCHMARK)

MACRO_SHOCK_THRESHOLDS = {
    "WTI": 2.0,
    "BRENT": 2.0,
    "US10Y": 1.0,
    "USD_KRW": 1.0,
    "VIX": 5.0,
}


def fetch_one(name: str, symbol: str) -> tuple[str, pd.DataFrame | None, str | None]:
    try:
        df = yf.download(
            symbol,
            start=START_DATE,
            end=datetime.now(timezone.utc).date().isoformat(),
            interval="1d",
            auto_adjust=False,
            actions=False,
            progress=False,
            threads=False,
        )
        if df.empty:
            return name, None, "empty"
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.reset_index()
        date_col = "Date" if "Date" in df.columns else "Datetime"
        df = df.rename(columns={date_col: "date"})
        df["date"] = pd.to_datetime(df["date"], utc=True).dt.normalize()

        for col in ("Open", "High", "Low", "Close", "Adj Close", "Volume"):
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        raw_close = df["Close"]
        if (
            "Adj Close" in df.columns
            and name not in {"VIX", "US10Y", "USD_KRW", "USD_JPY", "DXY", "WTI", "BRENT", "GOLD"}
        ):
            factor = (df["Adj Close"] / raw_close).replace([float("inf"), float("-inf")], pd.NA)
            factor = factor.fillna(1.0)
            close = df["Adj Close"].fillna(raw_close)
        else:
            factor = pd.Series(1.0, index=df.index)
            close = raw_close

        out = pd.DataFrame(
            {
                "date": df["date"],
                "open": df["Open"] * factor if "Open" in df.columns else close,
                "high": df["High"] * factor if "High" in df.columns else close,
                "low": df["Low"] * factor if "Low" in df.columns else close,
                "close_raw": raw_close,
                "close": close,
                "volume": df["Volume"] if "Volume" in df.columns else pd.Series([None] * len(df)),
            }
        ).dropna(subset=["date", "close"])

        return name, out.sort_values("date").drop_duplicates("date"), None
    except Exception as exc:
        return name, None, f"{type(exc).__name__}: {exc}"


def series_feature_rows(name: str, df: pd.DataFrame) -> list[dict[str, Any]]:
    kind, symbol = SYMBOLS[name]
    rows: list[dict[str, Any]] = []

    closes = df["close"].tolist()
    volumes = df["volume"].tolist()
    dates = df["date"].tolist()

    for i, dt in enumerate(dates):
        observed_at = dt.to_pydatetime()
        obs = build_observation(
            series_id=name,
            symbol=symbol,
            observed_at=observed_at,
            available_at=observed_at,
            source=SOURCE,
            prices=closes[: i + 1],
            volumes=volumes[: i + 1],
            revision_status="vendor_current_historical",
            asset_class=kind,
            session="DAILY_CLOSE",
        )
        obs.update(
            {
                "source_id": SOURCE_ID,
                "rule_version": RULE_VERSION,
                "pit_status": PIT_STATUS,
                "raw_value": float(df.iloc[i]["close_raw"]),
                "normalized_value": float(df.iloc[i]["close"]),
                "normalization_status": "ADJUSTED_OHLC_WHEN_AVAILABLE",
                "date": dt.date().isoformat(),
            }
        )
        rows.append(obs)

    return rows


def split_for_date(date: str) -> str | None:
    for split, start, end in SPLITS:
        if start <= date < end:
            return split
    return None


def macro_context(day: dict[str, dict[str, Any]]) -> tuple[dict[str, float | None], int]:
    moves: dict[str, float | None] = {}
    worsening = 0
    for name, threshold in MACRO_SHOCK_THRESHOLDS.items():
        row = day.get(name)
        value = row["returns_pct"]["d1"] if row else None
        moves[name] = value
        if value is not None and value >= threshold:
            worsening += 1
    return moves, worsening


def daily_breadth(day: dict[str, dict[str, Any]]) -> dict[str, Any]:
    leaders = [day[name] for name in LEADERS if name in day]
    adv = sum(1 for row in leaders if (row["returns_pct"]["d1"] or 0) > 0)
    dec = sum(1 for row in leaders if (row["returns_pct"]["d1"] or 0) < 0)
    return {
        "source_type": "watchlist_proxy",
        "n": len(leaders),
        "advancers": adv,
        "decliners": dec,
        "unchanged": len(leaders) - adv - dec,
        "advance_ratio": adv / len(leaders) if leaders else None,
    }


def make_event(
    *,
    date: str,
    split: str,
    asset: str,
    row: dict[str, Any],
    day: dict[str, dict[str, Any]],
    episode_id: str,
) -> dict[str, Any]:
    benchmark = day.get(ASSET_BENCHMARK[asset])
    asset_d20 = row["returns_pct"]["d20"]
    benchmark_d20 = benchmark["returns_pct"]["d20"] if benchmark else None
    rs20 = None if asset_d20 is None or benchmark_d20 is None else asset_d20 - benchmark_d20

    breadth = daily_breadth(day)
    macro_moves, worsening = macro_context(day)

    dd20 = row["location"]["drawdown_20d_high_pct"]
    dd60 = row["location"]["drawdown_60d_high_pct"]
    ma50 = row["location"]["distance_ma50_pct"]
    d5 = row["returns_pct"]["d5"]
    d20 = row["returns_pct"]["d20"]
    ma20 = row["location"]["distance_ma20_pct"]

    price_signal = dd20 is not None and dd20 <= -10.0

    price_location_pass = price_signal and (
        (dd60 is not None and dd60 <= -8.0)
        or (ma50 is not None and ma50 <= -5.0)
    )

    extension_pass = (
        d5 is not None
        and d5 <= 8.0
        and (ma20 is None or ma20 <= 8.0)
        and row["structure"]["consecutive_up_sessions"] < 5
    )

    leadership_pass = (
        (rs20 is not None and rs20 >= 0.0)
        or (breadth["advance_ratio"] is not None and breadth["advance_ratio"] >= 0.50)
    )

    macro_pass = worsening < 2 and all(
        day.get(name) is not None for name in ("WTI", "US10Y", "USD_KRW", "VIX")
    )

    # Evidence-first: synchronized macro stress is the only evidence we can
    # construct from the vendor history itself. No headline/company evidence
    # is invented; such cases stay UNKNOWN in P5.
    attribution_confidence = "INFERRED" if worsening >= 1 and (d20 is not None and d20 < 0) else "UNKNOWN"
    attribution_pass = attribution_confidence != "UNKNOWN"

    return {
        "schema_version": "3.0",
        "date": date,
        "split": split,
        "asset_id": asset,
        "symbol": SYMBOLS[asset][1],
        "close": row["price"]["close"],
        "price_signal": bool(price_signal),
        "price_location_pass": bool(price_location_pass),
        "extension_pass": bool(extension_pass),
        "leadership_pass": bool(leadership_pass),
        "macro_pass": bool(macro_pass),
        "attribution_pass": bool(attribution_pass),
        "fundamentals_pass": False,
        "episode_id": episode_id,
        "rs20": rs20,
        "breadth_proxy": breadth,
        "macro_moves_d1": macro_moves,
        "attribution_confidence": attribution_confidence,
        "attribution_status": "MARKET_TRANSMISSION_ONLY",
        "pit_status": PIT_STATUS,
        "fundamentals_status": "DATA_NOT_READY",
        "entry_open": None,
        "entry_date": None,
        "asset_rows": [],
    }


def build_events(rows_by_name: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    by_date: dict[str, dict[str, dict[str, Any]]] = {}

    for name, rows in rows_by_name.items():
        for row in rows:
            by_date.setdefault(row["date"], {})[name] = row

    events: list[dict[str, Any]] = []

    for asset in LEADERS:
        asset_rows = rows_by_name.get(asset, [])
        active = False
        cooldown_until = -1

        for i, row in enumerate(asset_rows):
            date = row["date"]
            split = split_for_date(date)
            if split is None:
                continue

            day = by_date.get(date, {})
            dd20 = row["location"]["drawdown_20d_high_pct"]
            price_signal = dd20 is not None and dd20 <= -10.0

            if active and (dd20 is None or dd20 > -5.0):
                active = False
                cooldown_until = i + 5

            if price_signal and not active and i >= cooldown_until:
                episode_id = stable_id(asset, "episode", date)
                event = make_event(
                    date=date,
                    split=split,
                    asset=asset,
                    row=row,
                    day=day,
                    episode_id=episode_id,
                )
                events.append(event)
                active = True

    return events


def add_forward_outcomes(events: list[dict[str, Any]], raw: dict[str, pd.DataFrame]) -> None:
    for event in events:
        df = raw.get(event["asset_id"])
        if df is None:
            continue

        dates = df["date"].astype(str).str[:10].tolist()
        idxs = [i for i, value in enumerate(dates) if value == event["date"]]
        if not idxs:
            continue

        i = idxs[0]
        future = df.iloc[i + 1 : i + 1 + 60]
        if future.empty:
            continue

        entry_open = float(future.iloc[0]["open"])
        event["entry_open"] = entry_open
        event["entry_date"] = str(future.iloc[0]["date"])[:10]
        event["asset_rows"] = [
            {
                "date": str(row["date"])[:10],
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
            }
            for _, row in future.iterrows()
        ]

        for horizon in (5, 20, 60):
            if len(future) < horizon:
                continue
            target = future.iloc[horizon - 1]
            final_close = float(target["close"])
            low_path = future.iloc[:horizon]["low"].astype(float)
            event[f"forward_{horizon}d_return_pct"] = (final_close / entry_open - 1.0) * 100.0
            event[f"forward_{horizon}d_mae_pct"] = (low_path.min() / entry_open - 1.0) * 100.0

        event["entry_opportunity_label"] = (
            event.get("forward_20d_return_pct") is not None
            and event["forward_20d_return_pct"] > 0
        )


def build(out_dir: Path, workers: int = 5) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)

    downloaded: dict[str, pd.DataFrame] = {}
    failures: dict[str, str] = {}

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(fetch_one, name, symbol): name
            for name, (_, symbol) in SYMBOLS.items()
        }
        for future in as_completed(futures):
            name, df, error = future.result()
            if df is None:
                failures[name] = error or "unknown"
            else:
                downloaded[name] = df

    rows_by_name = {
        name: series_feature_rows(name, df)
        for name, df in downloaded.items()
    }

    pit_path = out_dir / "pit_observations.jsonl"
    with pit_path.open("w", encoding="utf-8") as fh:
        for name in sorted(rows_by_name):
            for row in rows_by_name[name]:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    events = build_events(rows_by_name)
    add_forward_outcomes(events, downloaded)

    event_path = out_dir / "p0p6_events.jsonl"
    with event_path.open("w", encoding="utf-8") as fh:
        for row in events:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    manifest = {
        "schema_version": "3.0",
        "pit_status": PIT_STATUS,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "start_date": START_DATE,
        "built_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "series_requested": len(SYMBOLS),
        "series_downloaded": len(downloaded),
        "series_failed": failures,
        "pit_rows": sum(len(value) for value in rows_by_name.values()),
        "asset_count": len(LEADERS),
        "event_rows": len(events),
        "fundamentals_status": "DATA_NOT_READY",
        "pit_archival_revisions": False,
        "note": (
            "Historical vendor prices are usable for price/market path experiments, "
            "but this is not an archival point-in-time revision database. "
            "P6 remains blocked until PIT fundamentals are connected."
        ),
    }

    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("artifacts/historical_pit_v3"))
    ap.add_argument("--workers", type=int, default=5)
    args = ap.parse_args()

    manifest = build(args.out, workers=args.workers)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0 if manifest["series_downloaded"] >= 10 else 2


if __name__ == "__main__":
    raise SystemExit(main())
