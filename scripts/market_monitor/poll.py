#!/usr/bin/env python3
"""Background market monitor with explicit return horizons and fail-closed freshness.

Yahoo Chart remains an unofficial external source. Return horizons and source
freshness are kept distinct; failures are DATA GAP, never imputed values.
"""

from __future__ import annotations

import json
import math
import os
import sys
import time
from datetime import datetime, time as clock_time, timezone
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config" / "market_monitor.json"
LOCAL_STATE = ROOT / "runtime" / "market_state.json"
UTC = timezone.utc


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_timestamp(value: str | None) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        return None
    return dt.astimezone(UTC)


def timestamp_iso(value: int | float) -> str:
    return datetime.fromtimestamp(value, UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def pct_change(new_value: float | None, reference_value: float | None) -> float | None:
    if new_value is None or reference_value is None or reference_value == 0:
        return None
    return (new_value / reference_value - 1.0) * 100.0


def market_session_for_series(group: str, name: str) -> str | None:
    """Map a series to an explicit market clock; this is not inferred from freshness."""
    if group == "indices":
        return "KOREA" if name in {"KOSPI", "KOSDAQ"} else "US"
    if group == "korea_leaders":
        return "KOREA"
    if group == "us_leaders":
        return "US"
    if group == "macro":
        if name == "USD_KRW":
            return "KOREA"
        if name in {"US10Y", "US2Y_TNOTE_FUT", "DXY", "WTI", "BRENT", "GOLD"}:
            return "US"
    return None


def _clock_bounds(now: datetime, session: str, cfg: dict) -> tuple[bool | None, ZoneInfo | None, datetime | None, datetime | None]:
    schedule = cfg.get("market_sessions", {}).get(session)
    if not schedule:
        return None, None, None, None
    try:
        zone = ZoneInfo(schedule["timezone"])
        local_now = now.astimezone(zone)
        open_clock = clock_time.fromisoformat(schedule["open"])
        close_clock = clock_time.fromisoformat(schedule["close"])
        start = datetime.combine(local_now.date(), open_clock, tzinfo=zone)
        end = datetime.combine(local_now.date(), close_clock, tzinfo=zone)
        weekday = local_now.isoweekday()
        weekday_ok = weekday in schedule.get("weekdays", [1, 2, 3, 4, 5])
        active = weekday_ok and start <= local_now <= end
        return active, zone, start, end
    except (KeyError, ValueError, ZoneInfoNotFoundError):
        return None, None, None, None


def _timezone_for(meta: dict, market_session: str | None, cfg: dict) -> ZoneInfo:
    schedule = cfg.get("market_sessions", {}).get(market_session or "")
    timezone_name = (schedule or {}).get("timezone") or meta.get("exchangeTimezoneName")
    if not timezone_name:
        raise ValueError("missing exchange timezone")
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"invalid exchange timezone: {timezone_name}") from exc


def _period_return(pairs: list[tuple[int, float]], horizon_minutes: int, zone: ZoneInfo) -> float | None:
    """Return a horizon-specific move only from same-session bars spanning that horizon."""
    if len(pairs) < 2:
        return None
    latest_ts, latest_px = pairs[-1]
    latest_date = datetime.fromtimestamp(latest_ts, UTC).astimezone(zone).date()
    target_seconds = horizon_minutes * 60
    lower = max(60, int(target_seconds * 0.6))
    upper = int(target_seconds * 1.4)
    candidates = []
    for ts, px in pairs[:-1]:
        if datetime.fromtimestamp(ts, UTC).astimezone(zone).date() != latest_date:
            continue
        elapsed = latest_ts - ts
        if lower <= elapsed <= upper:
            candidates.append((abs(elapsed - target_seconds), px))
    if not candidates:
        return None
    _, reference_px = min(candidates, key=lambda item: item[0])
    return pct_change(latest_px, reference_px)


def _daily_closes(pairs: list[tuple[int, float]], zone: ZoneInfo) -> list[tuple[object, int, float]]:
    """Extract the last regular-session bar for each exchange-local date."""
    by_date: dict[object, tuple[int, float]] = {}
    for ts, px in pairs:
        day = datetime.fromtimestamp(ts, UTC).astimezone(zone).date()
        existing = by_date.get(day)
        if existing is None or ts > existing[0]:
            by_date[day] = (ts, px)
    return [(day, ts, px) for day, (ts, px) in sorted(by_date.items())]


def summarize_chart_payload(
    symbol: str,
    meta: dict,
    timestamps: list,
    closes: list,
    market_session: str | None = None,
    cfg: dict | None = None,
    now: datetime | None = None,
) -> dict:
    """Pure chart-to-observation conversion. Kept isolated for deterministic regression tests."""
    cfg = cfg or load_config()
    now = (now or datetime.now(UTC)).astimezone(UTC)
    pairs = sorted(
        (
            (int(ts), float(px))
            for ts, px in zip(timestamps or [], closes or [])
            if ts is not None and px is not None and math.isfinite(float(px))
        ),
        key=lambda item: item[0],
    )
    if not pairs:
        raise ValueError("empty price series")

    zone = _timezone_for(meta, market_session, cfg)
    session_state, _, session_start, session_end = _clock_bounds(now, market_session, cfg)
    if session_state is None:
        periods = (meta.get("currentTradingPeriod") or {}).get("regular") or {}
        start_epoch, end_epoch = periods.get("start"), periods.get("end")
        if isinstance(start_epoch, (int, float)) and isinstance(end_epoch, (int, float)) and end_epoch > start_epoch:
            session_start = datetime.fromtimestamp(start_epoch, UTC).astimezone(zone)
            session_end = datetime.fromtimestamp(end_epoch, UTC).astimezone(zone)
            session_state = session_start <= now <= session_end
        else:
            session_state = None

    latest_ts, latest_px = pairs[-1]
    latest_dt = datetime.fromtimestamp(latest_ts, UTC).astimezone(zone)
    local_now = now.astimezone(zone)
    closes_by_day = _daily_closes(pairs, zone)
    prior_day_close = None
    for day, ts, px in reversed(closes_by_day[:-1]):
        if day < latest_dt.date():
            prior_day_close = (ts, px)
            break

    current_session_pct = None
    if session_state is True and latest_dt.date() == local_now.date() and prior_day_close:
        current_session_pct = pct_change(latest_px, prior_day_close[1])

    completed_closes = closes_by_day[:]
    exclude_latest_date = False
    if session_state is True and latest_dt.date() == local_now.date():
        exclude_latest_date = True
    elif latest_dt.date() == local_now.date():
        # A same-day bar is a completed close only after the configured close time,
        # with a final observation reasonably near the close. Otherwise it is partial/stale.
        close_epoch = session_end.timestamp() if session_end else None
        if close_epoch is None or now.timestamp() < close_epoch or latest_ts < close_epoch - 60 * 60:
            exclude_latest_date = True
    if exclude_latest_date and completed_closes:
        completed_closes = completed_closes[:-1]

    daily_pct = None
    completed_close_at = None
    if completed_closes:
        completed_close_at = completed_closes[-1][1]
    if len(completed_closes) >= 2:
        daily_pct = pct_change(completed_closes[-1][2], completed_closes[-2][2])

    prev_5m_px = pairs[-2][1] if len(pairs) >= 2 and (
        0 < pairs[-1][0] - pairs[-2][0] <= 10 * 60
        and datetime.fromtimestamp(pairs[-1][0], UTC).astimezone(zone).date()
        == datetime.fromtimestamp(pairs[-2][0], UTC).astimezone(zone).date()
    ) else None

    return {
        "symbol": symbol,
        "price": latest_px,
        "prev_price_5m": prev_5m_px,
        "change_pct_5m": _period_return(pairs, 5, zone),
        "change_pct_15m": _period_return(pairs, 15, zone),
        "session_change_pct": current_session_pct,
        "last_completed_session_return_pct": daily_pct,
        "last_completed_session_close_at": timestamp_iso(completed_close_at) if completed_close_at else None,
        "timestamp": timestamp_iso(latest_ts),
        "currency": meta.get("currency"),
        "exchange": meta.get("exchangeName"),
        "exchange_timezone": zone.key,
        "market_session": market_session or "UNKNOWN",
        "market_session_state": "ACTIVE" if session_state is True else "CLOSED" if session_state is False else "UNKNOWN",
        "return_calculation_version": "returns-5m-15m-close-close-v1",
    }


def fetch_chart(
    symbol: str,
    range_: str = "5d",
    interval: str = "5m",
    market_session: str | None = None,
    cfg: dict | None = None,
) -> dict:
    cfg = cfg or load_config()
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/"
        f"{quote(symbol, safe='')}?range={quote(range_)}&interval={quote(interval)}"
        "&includePrePost=false&events=div%2Csplits"
    )
    req = Request(
        url,
        headers={
            "User-Agent": "investment-market-monitor/2.1",
            "Accept": "application/json",
        },
    )
    with urlopen(req, timeout=12) as resp:
        body = resp.read()
    payload = json.loads(body)
    chart = payload.get("chart", {})
    if chart.get("error"):
        raise ValueError(f"chart provider error: {chart['error']}")
    results = chart.get("result") or []
    if not results:
        raise ValueError("empty chart result")
    result = results[0]
    meta = result.get("meta", {})
    timestamps = result.get("timestamp") or []
    quote0 = (result.get("indicators", {}).get("quote") or [{}])[0]
    closes = quote0.get("close") or []
    return summarize_chart_payload(
        symbol, meta, timestamps, closes, market_session=market_session, cfg=cfg, now=datetime.now(UTC)
    )


def safe_fetch(symbol: str, market_session: str | None = None, cfg: dict | None = None) -> dict:
    try:
        return {"ok": True, **fetch_chart(symbol, market_session=market_session, cfg=cfg)}
    except Exception as exc:
        return {"ok": False, "symbol": symbol, "error": f"{type(exc).__name__}: {exc}"}


def flatten_symbols(cfg: dict) -> dict:
    out = {}
    for group, mapping in cfg["symbols"].items():
        for name, symbol in mapping.items():
            out[f"{group}.{name}"] = symbol
    return out


def session_bucket(now: datetime | None = None, cfg: dict | None = None) -> str:
    cfg = cfg or load_config()
    now = (now or datetime.now(UTC)).astimezone(UTC)
    korea, _, _, _ = _clock_bounds(now, "KOREA", cfg)
    us, _, _, _ = _clock_bounds(now, "US", cfg)
    if korea and us:
        return "OVERLAP"
    if korea:
        return "KOREA"
    if us:
        return "US"
    return "GLOBAL_TRANSITION"


def status_from_change(change, threshold):
    if change is None:
        return "N/A"
    x = abs(change)
    if x >= threshold:
        return "RED"
    if x >= threshold * 0.5:
        return "AMBER"
    return "GREEN"


def _worst_status(*statuses: str) -> str:
    rank = {"N/A": -1, "GREEN": 0, "AMBER": 1, "RED": 2}
    known = [status for status in statuses if status in rank and status != "N/A"]
    return max(known, key=lambda s: rank[s]) if known else "N/A"


def _series_age_minutes(item: dict, asof: datetime) -> float | None:
    observed = parse_timestamp(item.get("timestamp"))
    if observed is None:
        return None
    age = (asof - observed).total_seconds() / 60
    return age if age >= 0 else None


def _freshness_status(item: dict | None, asof: datetime, cfg: dict) -> tuple[str, float | None]:
    if not item or not item.get("ok"):
        return "MISSING", None
    age = _series_age_minutes(item, asof)
    if age is None:
        return "UNKNOWN", None
    thresholds = cfg["thresholds"]
    market_state = item.get("market_session_state")
    if market_state == "ACTIVE":
        if age > thresholds["max_stale_minutes"]:
            return "STALE", age
        if item.get("change_pct_15m") is None:
            return "UNKNOWN", age
        return "FRESH_ACTIVE_SESSION", age
    if market_state == "CLOSED":
        if age > thresholds.get("max_closed_session_age_minutes", 4320):
            return "STALE", age
        if item.get("last_completed_session_return_pct") is None:
            return "UNKNOWN", age
        return "VALID_CLOSED_SESSION", age
    return "UNKNOWN", age


def _item_status_change(item: dict | None, freshness: str, intraday_threshold: float, daily_threshold: float) -> str:
    if not item or not item.get("ok"):
        return "N/A"
    if freshness == "FRESH_ACTIVE_SESSION":
        return status_from_change(item.get("change_pct_15m"), intraday_threshold)
    if freshness == "VALID_CLOSED_SESSION":
        return status_from_change(item.get("last_completed_session_return_pct"), daily_threshold)
    return "N/A"


def _daily_move(item: dict | None, freshness: str) -> float | None:
    if item and item.get("ok") and freshness == "VALID_CLOSED_SESSION":
        return item.get("last_completed_session_return_pct")
    return None


def _completed_daily_move(item: dict | None, freshness: str) -> float | None:
    if item and item.get("ok") and freshness in {"FRESH_ACTIVE_SESSION", "VALID_CLOSED_SESSION"}:
        return item.get("last_completed_session_return_pct")
    return None


def _active_move(item: dict | None, freshness: str, field: str = "change_pct_15m") -> float | None:
    if item and item.get("ok") and freshness == "FRESH_ACTIVE_SESSION":
        return item.get(field)
    return None


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _breadth(items: list[tuple[dict, str]], use_session: bool) -> tuple[float | None, int]:
    values = []
    for item, freshness in items:
        if not item or not item.get("ok"):
            continue
        if freshness == "FRESH_ACTIVE_SESSION":
            value = item.get("session_change_pct") if use_session else item.get("change_pct_15m")
        elif freshness == "VALID_CLOSED_SESSION":
            value = item.get("last_completed_session_return_pct")
        else:
            value = None
        if value is not None:
            values.append(float(value))
    if not values:
        return None, 0
    return sum(1 for value in values if value > 0) / len(values), len(values)


def build_state(cfg: dict, raw: dict) -> dict:
    groups = raw["groups"]
    idx = groups["indices"]
    macro = groups["macro"]
    korea = groups["korea_leaders"]
    us = groups["us_leaders"]
    asof = parse_timestamp(raw.get("collected_at")) or datetime.now(UTC)
    session = session_bucket(asof, cfg)
    all_raw = {
        f"{group}.{name}": item
        for group, mapping in groups.items()
        for name, item in mapping.items()
    }

    freshness_by_series = {}
    ages_by_series = {}
    freshness_statuses = {}
    for series_key, item in all_raw.items():
        status, age = _freshness_status(item, asof, cfg)
        freshness_by_series[series_key] = status
        freshness_statuses[series_key] = status
        ages_by_series[series_key] = round(age, 1) if age is not None else None

    freshness_by_group = {}
    for group in groups:
        statuses = [freshness_statuses.get(f"{group}.{name}", "MISSING") for name in groups[group]]
        if not statuses or any(s in {"MISSING", "UNKNOWN"} for s in statuses):
            freshness_by_group[group] = "RED" if not statuses or any(s == "MISSING" for s in statuses) else "AMBER"
        elif any(s == "STALE" for s in statuses):
            freshness_by_group[group] = "AMBER"
        else:
            freshness_by_group[group] = "GREEN"

    required_series = cfg["thresholds"].get("required_series", [])
    required_statuses = [freshness_statuses.get(key, "MISSING") for key in required_series]
    if not required_statuses or any(s in {"MISSING", "UNKNOWN"} for s in required_statuses):
        data_quality = "RED"
    elif any(s == "STALE" for s in required_statuses):
        data_quality = "AMBER"
    else:
        data_quality = "GREEN"

    dth = cfg["thresholds"]["material_abs_pct_15m"]
    dth_daily = cfg["thresholds"].get("material_abs_pct_daily", {"index": 2.0, "macro": 1.0, "leader": 3.0, "risk": 10.0})

    if session == "KOREA":
        intraday_trend_names = ["KOSPI", "KOSDAQ"]
    elif session == "US":
        intraday_trend_names = ["SP500", "NASDAQ", "SOX"]
    else:
        intraday_trend_names = []
    fresh_trend_items = []
    for name in intraday_trend_names:
        item = idx.get(name)
        freshness = freshness_statuses.get(f"indices.{name}", "UNKNOWN")
        if item and freshness == "FRESH_ACTIVE_SESSION" and item.get("change_pct_15m") is not None:
            fresh_trend_items.append(item)
    if fresh_trend_items:
        trend_horizon = "15m"
        trend = _mean([item["change_pct_15m"] for item in fresh_trend_items])
        trend_status = status_from_change(trend, dth["index"])
        session_returns = [item.get("session_change_pct") for item in fresh_trend_items if item.get("session_change_pct") is not None]
        if session_returns:
            daily_threshold = dth_daily.get("index", 2.0)
            trend_status = _worst_status(
                trend_status,
                status_from_change(_mean(session_returns), daily_threshold),
                *[status_from_change(value, daily_threshold) for value in session_returns],
            )
    else:
        trend_horizon = "daily_close_to_close"
        daily_names = ["KOSPI", "KOSDAQ", "NASDAQ", "SOX"]
        daily_values = [
            (name, _daily_move(idx.get(name), freshness_statuses.get(f"indices.{name}", "UNKNOWN")))
            for name in daily_names
        ]
        valid_daily = [(name, value) for name, value in daily_values if value is not None]
        trend = _mean([value for _, value in valid_daily])
        daily_threshold = dth_daily.get("index", 2.0)
        trend_status = _worst_status(
            status_from_change(trend, daily_threshold),
            *[status_from_change(value, daily_threshold) for _, value in valid_daily],
        )

    vix = idx.get("VIX", {})
    vix_status = freshness_statuses.get("indices.VIX", "MISSING")
    vix_change_15m = _active_move(vix, vix_status)
    vix_daily = _completed_daily_move(vix, vix_status)
    risk_status = (
        status_from_change(vix_change_15m, dth["index"])
        if vix_change_15m is not None
        else status_from_change(vix_daily, dth_daily.get("risk", 10.0))
    )

    if session == "KOREA":
        breadth_group = "korea_leaders"
        breadth_source = korea
    elif session == "US":
        breadth_group = "us_leaders"
        breadth_source = us
    else:
        breadth_group = "all_leaders"
        breadth_source = {**korea, **us}
    breadth_items = [
        (item, freshness_statuses.get(f"{group}.{name}", "UNKNOWN"))
        for name, item in breadth_source.items()
        for group in ([breadth_group] if breadth_group != "all_leaders" else [
            "korea_leaders" if name in korea else "us_leaders"
        ])
    ]
    has_active_breadth = any(f == "FRESH_ACTIVE_SESSION" for _, f in breadth_items)
    breadth, breadth_count = _breadth(breadth_items, use_session=has_active_breadth)
    expected_breadth_count = (
        len(cfg["symbols"]["korea_leaders"]) if breadth_group == "korea_leaders"
        else len(cfg["symbols"]["us_leaders"]) if breadth_group == "us_leaders"
        else len(cfg["symbols"]["korea_leaders"]) + len(cfg["symbols"]["us_leaders"])
    )
    min_coverage = cfg["thresholds"].get("breadth_proxy_min_coverage", 0.5)
    if expected_breadth_count and breadth_count / expected_breadth_count < min_coverage:
        breadth = None

    breadth_status = (
        "RED" if breadth is not None and breadth < cfg["thresholds"]["breadth_proxy_red"]
        else "GREEN" if breadth is not None and breadth >= cfg["thresholds"]["breadth_proxy_green"]
        else "AMBER" if breadth is not None else "N/A"
    )

    def macro_status(name: str, group: str, threshold_key: str) -> str:
        item = groups[group].get(name)
        status = freshness_statuses.get(f"{group}.{name}", "UNKNOWN")
        daily_threshold = dth_daily.get(threshold_key, dth_daily.get("macro", 1.0))
        return _item_status_change(item, status, dth["macro"], daily_threshold)

    age_values = [ages_by_series.get(key) for key in required_series if ages_by_series.get(key) is not None]
    max_required_age = max(age_values) if age_values else None

    state = {
        "schema_version": "2.1",
        "asof": raw.get("collected_at") or now_iso(),
        "session": session,
        "REGIME": "UNCONFIRMED",
        "RISK": risk_status,
        "TREND": trend_status,
        "BREADTH": breadth_status,
        "LEADERS": breadth_status,
        "RATES": macro_status("US10Y", "macro", "macro"),
        "FX": macro_status("USD_KRW", "macro", "macro"),
        "OIL": macro_status("WTI", "macro", "macro"),
        "GOLD": macro_status("GOLD", "macro", "macro"),
        "GEO": "N/A",
        "BUY_TRIGGER": "UNCONFIRMED",
        "DATA_QUALITY": data_quality,
        "metrics": {
            # Legacy names are retained as aliases for the validated 15-minute move only.
            # They are null outside a validated current session; use the explicit fields below.
            "KOSPI_pct": idx.get("KOSPI", {}).get("change_pct_15m"),
            "NASDAQ_pct": idx.get("NASDAQ", {}).get("change_pct_15m"),
            "SOX_pct": idx.get("SOX", {}).get("change_pct_15m"),
            "VIX_pct": vix_change_15m,
            "KOSPI_5m_pct": idx.get("KOSPI", {}).get("change_pct_5m"),
            "KOSPI_15m_pct": idx.get("KOSPI", {}).get("change_pct_15m"),
            "KOSPI_session_pct": idx.get("KOSPI", {}).get("session_change_pct"),
            "KOSPI_daily_close_pct": idx.get("KOSPI", {}).get("last_completed_session_return_pct"),
            "KOSDAQ_15m_pct": idx.get("KOSDAQ", {}).get("change_pct_15m"),
            "KOSDAQ_session_pct": idx.get("KOSDAQ", {}).get("session_change_pct"),
            "KOSDAQ_daily_close_pct": idx.get("KOSDAQ", {}).get("last_completed_session_return_pct"),
            "NASDAQ_5m_pct": idx.get("NASDAQ", {}).get("change_pct_5m"),
            "NASDAQ_15m_pct": idx.get("NASDAQ", {}).get("change_pct_15m"),
            "NASDAQ_daily_close_pct": idx.get("NASDAQ", {}).get("last_completed_session_return_pct"),
            "SOX_15m_pct": idx.get("SOX", {}).get("change_pct_15m"),
            "SOX_daily_close_pct": idx.get("SOX", {}).get("last_completed_session_return_pct"),
            "VIX_15m_pct": vix_change_15m,
            "VIX_daily_close_pct": vix_daily,
            "trend_horizon": trend_horizon,
            "trend_selected_pct": trend,
            "breadth_proxy": breadth,
            "breadth_sample_count": breadth_count,
            "US10Y_15m_pct": groups["macro"].get("US10Y", {}).get("change_pct_15m"),
            "US10Y_daily_close_pct": groups["macro"].get("US10Y", {}).get("last_completed_session_return_pct"),
            "USD_KRW_15m_pct": groups["macro"].get("USD_KRW", {}).get("change_pct_15m"),
            "USD_KRW_daily_close_pct": groups["macro"].get("USD_KRW", {}).get("last_completed_session_return_pct"),
            "WTI_15m_pct": groups["macro"].get("WTI", {}).get("change_pct_15m"),
            "WTI_daily_close_pct": groups["macro"].get("WTI", {}).get("last_completed_session_return_pct"),
            "GOLD_15m_pct": groups["macro"].get("GOLD", {}).get("change_pct_15m"),
            "GOLD_daily_close_pct": groups["macro"].get("GOLD", {}).get("last_completed_session_return_pct"),
            "freshness_by_series": freshness_by_series,
            "freshness_by_group": freshness_by_group,
            "freshness_age_minutes_by_series": ages_by_series,
            "freshness_max_required_minutes": round(max_required_age, 1) if max_required_age is not None else None,
            "freshness_min": None,
        },
    }
    return state


def delta(prev: dict | None, cur: dict) -> list[str]:
    if not prev:
        return ["INITIAL_STATE"]
    changes = []
    keys = ["REGIME", "RISK", "TREND", "BREADTH", "LEADERS", "RATES", "FX", "OIL", "GOLD", "BUY_TRIGGER", "DATA_QUALITY"]
    for k in keys:
        if prev.get(k) != cur.get(k):
            changes.append(f"{k}:{prev.get(k)}->{cur.get(k)}")
    return changes[:5]


def should_alert(prev: dict | None, cur: dict, changes: list[str]) -> tuple[str, bool]:
    # A first snapshot with degraded critical data must still raise an alert.
    if cur.get("DATA_QUALITY") in {"RED", "AMBER"} and (
        prev is None or prev.get("DATA_QUALITY") != cur.get("DATA_QUALITY")
    ):
        return "P1", True
    if not prev:
        if cur.get("RISK") == "RED" or cur.get("TREND") == "RED":
            if cur.get("metrics", {}).get("VIX_15m_pct") is not None or cur.get("metrics", {}).get("VIX_daily_close_pct") is not None:
                return "P0", True
            return "P1", True
        if cur.get("BREADTH") == "RED" or cur.get("LEADERS") == "RED":
            return "P1", True
        return "P2", False
    p0 = any(cur.get(k) == "RED" and prev.get(k) != "RED" for k in ["RISK", "TREND"]) and (
        cur.get("metrics", {}).get("VIX_15m_pct") is not None
        or cur.get("metrics", {}).get("VIX_daily_close_pct") is not None
    )
    p1 = any(cur.get(k) != prev.get(k) for k in ["BREADTH", "LEADERS", "RATES", "FX", "OIL", "BUY_TRIGGER"])
    if p0:
        return "P0", True
    if p1 and len(changes) >= 2:
        return "P1", True
    return "P2", False


def main() -> int:
    cfg = load_config()
    flat = flatten_symbols(cfg)
    groups = {g: {} for g in cfg["symbols"]}
    all_raw = {}
    for key, symbol in flat.items():
        group, name = key.split(".", 1)
        result = safe_fetch(symbol, market_session_for_series(group, name), cfg)
        result["series_key"] = key
        groups[group][name] = result
        all_raw[key] = result
        time.sleep(0.15)

    raw = {"collected_at": now_iso(), "groups": groups, "all": all_raw}
    current = build_state(cfg, raw)

    previous = None
    if LOCAL_STATE.exists():
        try:
            previous = json.loads(LOCAL_STATE.read_text(encoding="utf-8")).get("state")
        except Exception:
            previous = None

    changes = delta(previous, current)
    severity, alert = should_alert(previous, current, changes)

    event = {
        "schema_version": "2.1",
        "asof": current["asof"],
        "alert": alert,
        "severity": severity,
        "session": current["session"],
        "delta": changes,
        "state": current,
        "data_quality": current["DATA_QUALITY"],
    }

    LOCAL_STATE.parent.mkdir(parents=True, exist_ok=True)
    LOCAL_STATE.write_text(
        json.dumps({"state": current, "event": event, "raw": raw}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(event, ensure_ascii=False))
    # CI can use this output as the event payload; no trade execution occurs.
    return 0


if __name__ == "__main__":
    sys.exit(main())
