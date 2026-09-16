import json
import os
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import yfinance as yf

RULE_VERSION = "buy-trigger-v0.1-market-vector"
KST = ZoneInfo("Asia/Seoul")
CRITICAL = {
    "KOSPI": "^KS11",
    "SAMSUNG": "005930.KS",
    "HYNIX": "000660.KS",
    "SP500": "^GSPC",
    "NASDAQ": "^IXIC",
    "VIX": "^VIX",
    "US10Y": "^TNX",
    "BRENT": "BZ=F",
    "DXY": "DX-Y.NYB",
    "USDKRW": "KRW=X",
}


def last_two(symbol: str):
    df = yf.download(symbol, period="5d", interval="1d", auto_adjust=False, progress=False, threads=False)
    if df.empty:
        return None
    close = df["Close"]
    if hasattr(close, "columns"):
        close = close.iloc[:, 0]
    close = close.dropna()
    if len(close) < 2:
        return None
    return float(close.iloc[-1]), float(close.iloc[-2]), str(close.index[-1])


def pct_change(v):
    return None if v is None or v[1] == 0 else (v[0] / v[1] - 1.0) * 100.0


def classify_change(x, good_sign=1.0, soft=0.5, severe=1.5):
    if x is None:
        return "UNKNOWN"
    x *= good_sign
    if x >= soft:
        return "IMPROVING"
    if x <= -severe:
        return "WORSENING"
    return "STABLE"


def checkpoint(now):
    return {
        "08:30": "PREOPEN",
        "09:30": "OPEN_30M",
        "10:30": "ACTIVE_BUY",
        "14:30": "CLOSE_RISK",
    }.get(now.strftime("%H:%M"), "MANUAL")


def main():
    now = datetime.now(timezone.utc).astimezone(KST)
    observations, failures = {}, []
    for name, symbol in CRITICAL.items():
        try:
            v = last_two(symbol)
            if v is None:
                failures.append(name)
                continue
            observations[name] = {
                "symbol": symbol,
                "last": v[0],
                "previous": v[1],
                "change_pct": pct_change(v),
                "source_observed_at": v[2],
            }
        except Exception as exc:
            failures.append(f"{name}:{type(exc).__name__}")

    dq = "GREEN" if not failures else "BLOCKED"
    vals = {k: observations.get(k, {}).get("change_pct") for k in CRITICAL}
    clusters = {
        "MarketTrend": classify_change(vals["KOSPI"]),
        "Leadership": "IMPROVING" if all(v is not None and v >= 0 for v in [vals["HYNIX"], vals["SAMSUNG"]]) else "STABLE" if all(v is not None for v in [vals["HYNIX"], vals["SAMSUNG"]]) else "UNKNOWN",
        "Risk": classify_change(vals["VIX"], good_sign=-1.0),
        "Rates": classify_change(vals["US10Y"], good_sign=-1.0),
        "Energy": classify_change(vals["BRENT"], good_sign=-1.0),
        "FX": classify_change(vals["USDKRW"], good_sign=-1.0),
    }
    worsening = sum(v == "WORSENING" for v in clusters.values())
    improving = sum(v == "IMPROVING" for v in clusters.values())

    if dq != "GREEN":
        permission = "DATA_BLOCKED"
    elif worsening >= 2:
        permission = "B0"
    elif worsening == 1:
        permission = "B1"
    elif improving >= 3:
        permission = "B3"
    elif improving >= 1:
        permission = "B2"
    else:
        permission = "B1"

    # Conservative live-monitor cap: a single daily observation cannot escalate B3
    # when both Korean semiconductor leaders are materially red.
    if permission == "B3" and (vals["HYNIX"] is None or vals["SAMSUNG"] is None or min(vals["HYNIX"], vals["SAMSUNG"]) < -3.0):
        permission = "B2"

    payload = {
        "schema_version": "1.0",
        "rule_version": RULE_VERSION,
        "observed_at": now.isoformat(),
        "available_at": now.isoformat(),
        "checkpoint": checkpoint(now),
        "data_quality": {"status": dq, "failures": failures},
        "observations": observations,
        "clusters": clusters,
        "permission": permission,
        "action": "ALERT_ONLY",
        "note": "Automated monitor only; no order execution. Research rules remain unvalidated until PIT/OOS testing.",
    }
    out = Path(os.environ.get("OUTPUT_PATH", "artifacts/auto_market_monitor/latest.json"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
