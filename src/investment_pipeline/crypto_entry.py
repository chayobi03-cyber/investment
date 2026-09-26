from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd

EntryState = Literal["B0", "B1", "B2", "B3", "B4"]


@dataclass(frozen=True)
class EntrySignal:
    state: EntryState
    zone: str
    reason_codes: tuple[str, ...]
    zone_low: float | None
    zone_high: float | None


def validate_ohlcv(frame: pd.DataFrame) -> None:
    required = {"timestamp", "open", "high", "low", "close"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError("missing_columns:" + ",".join(missing))
    if frame.empty:
        raise ValueError("empty_frame")
    if frame["timestamp"].duplicated().any():
        raise ValueError("duplicate_timestamps")
    if not frame["timestamp"].is_monotonic_increasing:
        raise ValueError("timestamps_not_ascending")

    ohlc = frame[["open", "high", "low", "close"]]
    if (ohlc <= 0).any().any():
        raise ValueError("non_positive_ohlc")
    if (frame["high"] < ohlc[["open", "close"]].max(axis=1)).any():
        raise ValueError("invalid_high")
    if (frame["low"] > ohlc[["open", "close"]].min(axis=1)).any():
        raise ValueError("invalid_low")


def add_entry_features(frame: pd.DataFrame) -> pd.DataFrame:
    df = frame.copy()
    validate_ohlcv(df)
    for col in ("open", "high", "low", "close"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    if df[["open", "high", "low", "close"]].isna().any().any():
        raise ValueError("non_numeric_ohlc")

    df["ma20"] = df["close"].rolling(20, min_periods=20).mean()
    df["ma50"] = df["close"].rolling(50, min_periods=50).mean()
    df["ma200"] = df["close"].rolling(200, min_periods=200).mean()
    df["ret3"] = df["close"].pct_change(3)
    df["ret5"] = df["close"].pct_change(5)

    # Shifted reference prevents today's high from defining today's zone.
    df["prior_high60"] = df["high"].rolling(60, min_periods=60).max().shift(1)
    df["prior_high20"] = df["high"].rolling(20, min_periods=20).max().shift(1)
    df["prior_low20"] = df["low"].rolling(20, min_periods=20).min().shift(1)
    df["drawdown60"] = df["close"] / df["prior_high60"] - 1.0

    df["trend_ok"] = (
        (df["close"] > df["ma200"])
        & (df["ma20"] > df["ma50"])
        & (df["ma50"] > df["ma200"])
    )
    df["stabilization"] = (
        (df["ret3"] > 0)
        & (df["close"] >= df["ma20"])
        & df["trend_ok"]
    )
    df["breakout"] = (
        (df["close"] > df["prior_high60"])
        & (df["ret5"] > 0)
        & df["trend_ok"]
    )

    df["zone"] = "Z3"
    df.loc[df["drawdown60"].isna(), "zone"] = "UNKNOWN"
    df.loc[df["drawdown60"] > -0.05, "zone"] = "Z0"
    df.loc[(df["drawdown60"] <= -0.05) & (df["drawdown60"] > -0.08), "zone"] = "Z1"
    df.loc[(df["drawdown60"] <= -0.08) & (df["drawdown60"] > -0.12), "zone"] = "Z2"
    return df


def signal_from_row(row: pd.Series) -> EntrySignal:
    required = [
        "close", "ma20", "ma50", "ma200",
        "ret3", "ret5", "prior_high60", "drawdown60",
    ]
    if any(pd.isna(row[k]) for k in required):
        return EntrySignal("B0", "UNKNOWN", ("DATA_NOT_READY",), None, None)

    zone = str(row["zone"])
    trend_ok = bool(row["trend_ok"])
    stabilization = bool(row["stabilization"])
    breakout = bool(row["breakout"])
    high60 = float(row["prior_high60"])

    zone_bounds = {
        "Z1": (high60 * 0.92, high60 * 0.95),
        "Z2": (high60 * 0.88, high60 * 0.92),
        "Z3": (0.0, high60 * 0.88),
    }

    if not trend_ok:
        return EntrySignal("B0", zone, ("TREND_NOT_READY",), None, None)

    if breakout:
        if stabilization:
            return EntrySignal(
                "B3", "BREAKOUT",
                ("BREAKOUT_CONFIRMED", "TREND_VALID"),
                None, None,
            )
        return EntrySignal(
            "B2", "BREAKOUT",
            ("BREAKOUT_WATCH", "TREND_VALID"),
            None, None,
        )

    if zone == "Z0":
        if float(row["drawdown60"]) >= -0.02:
            return EntrySignal(
                "B1", "Z0",
                ("NO_CHASE", "PULLBACK_NOT_REACHED"),
                *zone_bounds["Z1"],
            )
        return EntrySignal("B0", "Z0", ("PULLBACK_NOT_REACHED",), *zone_bounds["Z1"])

    if zone in {"Z1", "Z2"}:
        if stabilization:
            return EntrySignal(
                "B3", zone,
                ("PULLBACK_STABILIZED", "TREND_VALID"),
                *zone_bounds[zone],
            )
        return EntrySignal(
            "B2", zone,
            ("PULLBACK_REACHED", "WAIT_STABILIZATION"),
            *zone_bounds[zone],
        )

    if zone == "Z3":
        if stabilization and float(row["close"]) >= float(row["ma50"]):
            return EntrySignal(
                "B4", zone,
                ("DEEP_DISLOCATION", "STABILIZED", "MA50_RECLAIM"),
                *zone_bounds[zone],
            )
        if stabilization:
            return EntrySignal(
                "B3", zone,
                ("DEEP_DISLOCATION", "STABILIZED"),
                *zone_bounds[zone],
            )
        return EntrySignal(
            "B2", zone,
            ("DEEP_DISLOCATION", "WAIT_STABILIZATION"),
            *zone_bounds[zone],
        )

    return EntrySignal("B0", zone, ("UNRESOLVED",), None, None)


def generate_signals(frame: pd.DataFrame) -> pd.DataFrame:
    df = add_entry_features(frame)
    signals = df.apply(signal_from_row, axis=1)
    out = df.copy()
    out["entry_state"] = signals.map(lambda s: s.state)
    out["entry_reason"] = signals.map(lambda s: "|".join(s.reason_codes))
    out["zone_low"] = signals.map(lambda s: s.zone_low)
    out["zone_high"] = signals.map(lambda s: s.zone_high)
    return out


def cluster_episodes(signals: pd.DataFrame, cooldown_bars: int = 5) -> pd.DataFrame:
    if cooldown_bars < 1:
        raise ValueError("cooldown_bars_must_be_positive")
    out = signals.copy()
    primary = []
    last_primary_pos: int | None = None

    for pos, (_, row) in enumerate(out.iterrows()):
        candidate = str(row["entry_state"]) in {"B2", "B3", "B4"}
        if not candidate:
            primary.append(False)
            continue
        if last_primary_pos is None or pos - last_primary_pos > cooldown_bars:
            primary.append(True)
            last_primary_pos = pos
        else:
            primary.append(False)

    out["primary_event"] = primary
    return out


def _future_window(series: pd.Series, horizon: int, reducer: str) -> pd.Series:
    future = series.shift(-1)
    reversed_future = future.iloc[::-1]
    if reducer == "min":
        values = reversed_future.rolling(horizon, min_periods=horizon).min().iloc[::-1]
    else:
        values = reversed_future.rolling(horizon, min_periods=horizon).max().iloc[::-1]
    return values


def add_forward_outcomes(
    signals: pd.DataFrame,
    horizons: tuple[int, ...] = (1, 5, 20, 60),
) -> pd.DataFrame:
    out = signals.copy()
    entry = out["open"].shift(-1)

    for h in horizons:
        future_close = out["close"].shift(-h - 1)
        future_low = _future_window(out["low"], h, "min")
        future_high = _future_window(out["high"], h, "max")

        out[f"entry_price_{h}d"] = entry
        out[f"forward_return_{h}d"] = future_close / entry - 1.0
        out[f"mae_{h}d"] = future_low / entry - 1.0
        out[f"mfe_{h}d"] = future_high / entry - 1.0
    return out
