#!/usr/bin/env python3
"""Background market monitor: raw quotes -> compact state -> event.

Provider is intentionally isolated behind fetch_chart(). The Yahoo chart endpoint
is treated as an external, unofficial source; failures are DATA GAP, not imputed.
"""

from __future__ import annotations

import json
import math
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

try:
    from scripts.market_monitor.decision_pipeline import build_observation, freshness, signed_shock
except ModuleNotFoundError:
    from decision_pipeline import build_observation, freshness, signed_shock

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config" / "market_monitor.json"
LOCAL_STATE = ROOT / "runtime" / "market_state.json"
UTC = timezone.utc
KST = ZoneInfo("Asia/Seoul")


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def fetch_chart(symbol: str, range_: str = "1d", interval: str = "5m") -> dict:
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/"
        f"{quote(symbol, safe='')}?range={quote(range_)}&interval={quote(interval)}"
        "&includePrePost=false&events=div%2Csplits"
    )
    req = Request(
        url,
        headers={
            "User-Agent": "investment-market-monitor/2.0",
            "Accept": "application/json",
        },
    )
    with urlopen(req, timeout=12) as resp:
        body = resp.read()
    payload = json.loads(body)
    result = payload["chart"]["result"][0]
    meta = result.get("meta", {})
    timestamps = result.get("timestamp") or []
    quote0 = (result.get("indicators", {}).get("quote") or [{}])[0]
    closes = quote0.get("close") or []
    pairs = [(ts, px) for ts, px in zip(timestamps, closes) if px is not None and math.isfinite(px)]
    if not pairs:
        raise ValueError("empty price series")
    latest_ts, latest_px = pairs[-1]
    prev_px = pairs[-2][1] if len(pairs) >= 2 else None
    return {
        "symbol": symbol,
        "price": float(latest_px),
        "prev_price": float(prev_px) if prev_px is not None else None,
        "change_pct": ((latest_px / prev_px) - 1) * 100 if prev_px else None,
        "timestamp": datetime.fromtimestamp(latest_ts, UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "currency": meta.get("currency"),
        "exchange": meta.get("exchangeName"),
    }


def safe_fetch(symbol: str) -> dict:
    try:
        return {"ok": True, **fetch_chart(symbol)}
    except Exception as exc:
        return {"ok": False, "symbol": symbol, "error": f"{type(exc).__name__}: {exc}"}


def build_live_observation(name: str, group: str, result: dict, available_at: datetime) -> dict | None:
    if not result.get("ok"):
        return None
    observed_at = datetime.fromisoformat(result["timestamp"].replace("Z", "+00:00"))
    prices = [result.get("prev_price"), result.get("price")]
    prices = [x for x in prices if x is not None]
    if not prices:
        return None
    asset_class = "equity" if group in {"korea_leaders", "us_leaders"} else "macro" if group == "macro" else "index"
    obs = build_observation(
        series_id=name,
        symbol=result["symbol"],
        observed_at=observed_at,
        available_at=available_at,
        source="yahoo_finance_chart",
        prices=prices,
        revision_status="vendor_current_live",
        asset_class=asset_class,
        session=session_bucket(),
    )
    polarity = 1 if name in {"VIX", "US10Y", "USD_KRW", "USD_JPY", "DXY", "WTI", "BRENT"} else None
    obs["source_id"] = "yahoo_finance_chart"
    obs["rule_version"] = "observation-v3.0-live-adapter"
    obs["raw_value"] = result.get("price")
    obs["normalized_value"] = result.get("price")
    obs["normalization_status"] = "NOT_APPLIED_LIVE"
    obs["live_status"] = "LIVE_TRANSPORT_ONLY"
    obs["freshness"] = freshness(
        observed_at,
        available_at,
        available_at,
        max_observation_age_seconds=1800,
        max_availability_lag_seconds=60,
    )
    if polarity is not None and len(prices) >= 2:
        obs["signed_shock"] = signed_shock(prices[-1], prices[-2], stress_polarity=polarity)
    else:
        obs["signed_shock"] = {"raw_pct": result.get("change_pct"), "stress_signed_pct": None, "direction": "UNSPECIFIED"}
    return obs


def flatten_symbols(cfg: dict) -> dict:
    out = {}
    for group, mapping in cfg["symbols"].items():
        for name, symbol in mapping.items():
            out[f"{group}.{name}"] = symbol
    return out


def session_bucket() -> str:
    now = datetime.now(KST)
    hm = now.hour * 60 + now.minute
    # Korea cash session 09:00-15:30 KST; US regular session 22:30-05:00 KST
    korea = 9 * 60 <= hm <= 15 * 60 + 30
    us = hm >= 22 * 60 + 30 or hm <= 5 * 60
    if korea and us:
        return "OVERLAP"
    if korea:
        return "KOREA"
    if us:
        return "US"
    return "GLOBAL_TRANSITION"


def pct_change(a, b):
    if a in (None, 0) or b is None:
        return None
    return (b / a - 1) * 100


def status_from_change(change, threshold):
    if change is None:
        return "N/A"
    x = abs(change)
    if x >= threshold:
        return "RED"
    if x >= threshold * 0.5:
        return "AMBER"
    return "GREEN"


def build_state(cfg: dict, raw: dict) -> dict:
    idx = raw["groups"]["indices"]
    macro = raw["groups"]["macro"]
    korea = raw["groups"]["korea_leaders"]
    us = raw["groups"]["us_leaders"]

    trend_changes = [v.get("change_pct") for v in [idx.get("KOSPI"), idx.get("NASDAQ"), idx.get("SOX")] if v and v.get("ok")]
    trend = sum(trend_changes) / len(trend_changes) if trend_changes else None

    leader_items = [v for v in list(korea.values()) + list(us.values()) if v.get("ok")]
    up = sum(1 for v in leader_items if (v.get("change_pct") or 0) > 0)
    breadth = up / len(leader_items) if leader_items else None

    vix = idx.get("VIX", {})
    vix_change = vix.get("change_pct") if v.get("ok") else None

    stale_cut = cfg["thresholds"]["max_stale_minutes"]
    observed_at = []
    for v in raw["all"].values():
        if v.get("ok") and v.get("timestamp"):
            observed_at.append(datetime.fromisoformat(v["timestamp"].replace("Z", "+00:00")))
    if observed_at:
        newest = max(observed_at)
        age_min = max(0.0, (datetime.now(UTC) - newest).total_seconds() / 60)
    else:
        age_min = None

    dth = cfg["thresholds"]["material_abs_pct_15m"]
    trend_status = status_from_change(trend, dth["index"])
    risk_status = status_from_change(vix_change, dth["index"])
    breadth_status = (
        "RED" if breadth is not None and breadth < cfg["thresholds"]["breadth_proxy_red"]
        else "GREEN" if breadth is not None and breadth >= cfg["thresholds"]["breadth_proxy_green"]
        else "AMBER" if breadth is not None else "N/A"
    )
    data_quality = "RED" if not raw["all"] else ("AMBER" if age_min is None or age_min > stale_cut else "GREEN")

    state = {
        "schema_version": "2.0",
        "asof": now_iso(),
        "session": session_bucket(),
        "REGIME": "UNCONFIRMED",
        "RISK": risk_status,
        "TREND": trend_status,
        "BREADTH": breadth_status,
        "LEADERS": "GREEN" if breadth is not None and breadth >= 0.70 else "RED" if breadth is not None and breadth < 0.30 else "AMBER" if breadth is not None else "N/A",
        "RATES": status_from_change(
            macro.get("US10Y", {}).get("change_pct") if macro.get("US10Y", {}).get("ok") else None,
            dth["macro"],
        ),
        "FX": status_from_change(
            macro.get("USD_KRW", {}).get("change_pct") if macro.get("USD_KRW", {}).get("ok") else None,
            dth["macro"],
        ),
        "OIL": status_from_change(
            macro.get("WTI", {}).get("change_pct") if macro.get("WTI", {}).get("ok") else None,
            dth["macro"],
        ),
        "GOLD": status_from_change(
            macro.get("GOLD", {}).get("change_pct") if macro.get("GOLD", {}).get("ok") else None,
            dth["macro"],
        ),
        "GEO": "N/A",
        "BUY_TRIGGER": "UNCONFIRMED",
        "DATA_QUALITY": data_quality,
        "metrics": {
            "KOSPI_pct": idx.get("KOSPI", {}).get("change_pct"),
            "NASDAQ_pct": idx.get("NASDAQ", {}).get("change_pct"),
            "SOX_pct": idx.get("SOX", {}).get("change_pct"),
            "VIX_pct": vix_change,
            "breadth_proxy": breadth,
            "US10Y_pct": macro.get("US10Y", {}).get("change_pct"),
            "USD_KRW_pct": macro.get("USD_KRW", {}).get("change_pct"),
            "WTI_pct": macro.get("WTI", {}).get("change_pct"),
            "GOLD_pct": macro.get("GOLD", {}).get("change_pct"),
            "freshness_min": age_min,
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
    if not prev:
        return "P2", False
    severe = {"RED"}
    p0 = any(cur.get(k) == "RED" and prev.get(k) != "RED" for k in ["RISK", "TREND"]) and (
        cur.get("metrics", {}).get("VIX_pct") is not None
    )
    p1 = any(cur.get(k) != prev.get(k) for k in ["BREADTH", "LEADERS", "RATES", "FX", "OIL", "BUY_TRIGGER"])
    if cur.get("DATA_QUALITY") == "RED":
        return "P1", True
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
        result = safe_fetch(symbol)
        groups[group][name] = result
        all_raw[key] = result
        time.sleep(0.15)

    raw = {"collected_at": now_iso(), "groups": groups, "all": all_raw}
    current = build_state(cfg, raw)
    available_at = datetime.now(UTC)
    observations_v3 = {}
    for key, result in all_raw.items():
        group, name = key.split(".", 1)
        observation = build_live_observation(name, group, result, available_at)
        if observation is not None:
            observations_v3[key] = observation
    current["observation_schema_version"] = "3.0"
    current["observations_v3"] = observations_v3

    previous = None
    if LOCAL_STATE.exists():
        try:
            previous = json.loads(LOCAL_STATE.read_text(encoding="utf-8")).get("state")
        except Exception:
            previous = None

    changes = delta(previous, current)
    severity, alert = should_alert(previous, current, changes)

    event = {
        "schema_version": "2.0",
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
