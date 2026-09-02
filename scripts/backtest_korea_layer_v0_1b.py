"""Executable Korea Layer / Stress Convergence backtest using public HTTP data.

The test intentionally separates:
1) absolute 2026 KOSPI entry zones (current-regime only), and
2) their drawdown-from-252d-high equivalents (historically comparable).

Stress Convergence v0.2 is reconstructed only for axes with reproducible
public history. Missing coverage is reported rather than imputed.
"""
from __future__ import annotations

import io
import json
import math
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts/korea_layer_backtest"
OUT.mkdir(parents=True, exist_ok=True)
START = pd.Timestamp("2000-01-01")
END = pd.Timestamp("2026-09-03")
ABS_ZONES = {"A_6600_6750": (6600.0, 6750.0), "B_6300_6500": (6300.0, 6500.0), "C_6000_6300": (6000.0, 6300.0)}
HORIZONS = {21: "1m", 63: "3m", 126: "6m", 252: "12m"}
FRED = ["DCOILBRENTEU", "DGS10", "VIXCLS", "BAMLH0A0HYM2", "NFCI", "T5YIFR"]


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "investment-korea-layer-backtest/0.1"})
    with urllib.request.urlopen(req, timeout=60) as r:  # noqa: S310
        return json.loads(r.read().decode("utf-8"))


def yahoo(symbol: str) -> pd.DataFrame:
    p1 = int(START.tz_localize("UTC").timestamp())
    p2 = int(END.tz_localize("UTC").timestamp())
    q = urllib.parse.urlencode({"period1": p1, "period2": p2, "interval": "1d", "events": "history", "includeAdjustedClose": "true"})
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol, safe="")}?{q}"
    payload = get_json(url)["chart"]["result"][0]
    ts = payload.get("timestamp", [])
    qv = payload["indicators"]["quote"][0]
    rows = []
    for i, epoch in enumerate(ts):
        vals = {k: qv[k][i] for k in ["open", "high", "low", "close", "volume"]}
        if vals["close"] is None:
            continue
        rows.append([pd.Timestamp.utcfromtimestamp(epoch).tz_localize(None).normalize(), *[vals[k] for k in ["open", "high", "low", "close", "volume"]]])
    return pd.DataFrame(rows, columns=["date", "open", "high", "low", "close", "volume"]).drop_duplicates("date").set_index("date").sort_index()


def fred(series: str) -> pd.Series:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={urllib.parse.quote(series)}"
    req = urllib.request.Request(url, headers={"User-Agent": "investment-korea-layer-backtest/0.1"})
    with urllib.request.urlopen(req, timeout=60) as r:  # noqa: S310
        raw = r.read()
    d = pd.read_csv(io.BytesIO(raw), parse_dates=["observation_date"])
    d = d.rename(columns={"observation_date": "date", series: series}).set_index("date")[series]
    d = pd.to_numeric(d, errors="coerce")
    return d.loc[START:END]


def persistence_5d(s: pd.Series, threshold: float) -> pd.Series:
    x = s > threshold
    five = x.rolling(5, min_periods=5).sum() >= 5
    two_of_three = x.rolling(3, min_periods=3).sum() >= 2
    return (five | two_of_three).fillna(False)


def persistence_monthly(s: pd.Series, threshold: float) -> pd.Series:
    m = s.resample("ME").last()
    good = m > threshold
    state = good & good.shift(1, fill_value=False)
    return state.reindex(s.index, method="ffill").fillna(False)


def persistence_weekly(s: pd.Series, threshold: float) -> pd.Series:
    w = s.resample("W-FRI").last()
    good = w > threshold
    state = good & good.shift(1, fill_value=False)
    return state.reindex(s.index, method="ffill").fillna(False)


def load() -> tuple[pd.DataFrame, dict]:
    kospi = yahoo("^KS11")["close"].rename("kospi")
    usdkrw = yahoo("KRW=X")["close"].rename("usdkrw")
    d = pd.concat([kospi, usdkrw], axis=1)
    coverage = {"KOSPI": [d["kospi"].first_valid_index(), d["kospi"].last_valid_index(), int(d["kospi"].notna().sum())], "USD/KRW": [d["usdkrw"].first_valid_index(), d["usdkrw"].last_valid_index(), int(d["usdkrw"].notna().sum())]}
    for s in FRED:
        try:
            x = fred(s)
            d = d.join(x, how="outer")
            coverage[s] = [x.first_valid_index(), x.last_valid_index(), int(x.notna().sum())]
        except Exception as exc:
            coverage[s] = {"error": f"{type(exc).__name__}: {exc}"}
            d[s] = np.nan
    return d.sort_index(), coverage


def stress(d: pd.DataFrame) -> pd.DataFrame:
    z = d.copy()
    z["energy_warn"] = persistence_5d(z["DCOILBRENTEU"], 90)
    z["energy_severe"] = persistence_5d(z["DCOILBRENTEU"], 100)
    z["rates_warn"] = persistence_5d(z["DGS10"], 4.75)
    z["credit_warn"] = persistence_5d(z["BAMLH0A0HYM2"], 400)
    z["credit_severe"] = persistence_5d(z["BAMLH0A0HYM2"], 500)
    z["vix_warn"] = persistence_5d(z["VIXCLS"], 25)
    z["vix_severe"] = persistence_5d(z["VIXCLS"], 35)
    z["nfci_warn"] = persistence_weekly(z["NFCI"], 0)
    z["inflation_warn"] = persistence_monthly(z["T5YIFR"], 2.5)
    z["inflationary_leg"] = z["energy_warn"] & z["credit_warn"] & (z["inflation_warn"] | z["energy_severe"]) & z["rates_warn"]
    z["financial_leg"] = z["credit_severe"] & z["vix_severe"] & z["nfci_warn"]
    z["l2_proxy"] = (z["inflationary_leg"] | z["financial_leg"]).fillna(False)
    z["warning_axes"] = sum(z[c].astype(int) for c in ["energy_warn", "inflation_warn", "rates_warn", "credit_warn", "nfci_warn", "vix_warn"])
    z["dd252"] = z["kospi"] / z["kospi"].rolling(252, min_periods=252).max() - 1
    return z


def drawdown_events(z: pd.DataFrame, threshold=-0.15, merge_days=60):
    h = z["dd252"].dropna()
    hits = h[h <= threshold]
    events = []
    if hits.empty:
        return events
    start = prev = None
    trough = 0.0
    for ts, v in hits.items():
        if start is None:
            start = prev = ts; trough = float(v); continue
        if (ts - prev).days > merge_days:
            events.append((start, prev, trough)); start = ts; trough = float(v)
        else:
            trough = min(trough, float(v))
        prev = ts
    events.append((start, prev, trough))
    return events


def entry_events(z: pd.DataFrame, lowdd: float, highdd: float):
    inside = z["dd252"].between(lowdd, highdd, inclusive="both")
    starts = inside & ~inside.shift(1, fill_value=False)
    rows = []
    for ts in z.index[starts]:
        base = float(z.loc[ts, "kospi"])
        r = {"date": ts.date().isoformat(), "kospi": base, "dd252": float(z.loc[ts, "dd252"]), "l2_proxy": bool(z.loc[ts, "l2_proxy"]), "warning_axes": int(z.loc[ts, "warning_axes"])}
        for days, label in HORIZONS.items():
            ix = z.index[z.index >= ts + pd.Timedelta(days=days)]
            if len(ix):
                end = ix[0]
                r[f"ret_{label}"] = float(z.loc[end, "kospi"] / base - 1)
                win = z.loc[ts:end, "kospi"]
                r[f"mdd_{label}"] = float(win.min() / base - 1)
            else:
                r[f"ret_{label}"] = np.nan; r[f"mdd_{label}"] = np.nan
        rows.append(r)
    return pd.DataFrame(rows)


def main():
    raw, coverage = load()
    z = stress(raw).dropna(subset=["kospi", "dd252"])
    latest = z.index.max(); current_high = float(z.loc[latest, "kospi"] / (1 + z.loc[latest, "dd252"]))
    zone_map = []
    summaries = []
    details = []
    for name, (lo, hi) in ABS_ZONES.items():
        dd_lo, dd_hi = min(lo/current_high-1, hi/current_high-1), max(lo/current_high-1, hi/current_high-1)
        zone_map.append({"zone": name, "absolute_low": lo, "absolute_high": hi, "equivalent_dd_low": dd_lo, "equivalent_dd_high": dd_hi})
        e = entry_events(z, dd_lo, dd_hi)
        e["zone"] = name
        if not e.empty: details.append(e)
        s = {"zone": name, "n": len(e), "l2_n": int(e["l2_proxy"].sum()) if not e.empty else 0}
        for label in HORIZONS.values():
            s[f"avg_ret_{label}"] = float(e[f"ret_{label}"].mean()) if not e.empty else np.nan
            s[f"median_ret_{label}"] = float(e[f"ret_{label}"].median()) if not e.empty else np.nan
            s[f"avg_mdd_{label}"] = float(e[f"mdd_{label}"].mean()) if not e.empty else np.nan
        summaries.append(s)
    det = pd.concat(details, ignore_index=True) if details else pd.DataFrame()
    events = drawdown_events(z)
    triggers = z.index[z["l2_proxy"]]
    event_rows=[]
    for start, anchor, trough in events:
        cand = triggers[(triggers >= start-pd.Timedelta(days=365)) & (triggers <= start)]
        trig = cand[0] if len(cand) else pd.NaT
        event_rows.append({"event_start": start.date().isoformat(), "anchor": anchor.date().isoformat(), "trough_dd": trough, "trigger": trig.date().isoformat() if pd.notna(trig) else None, "lead_days": (start-trig).days if pd.notna(trig) else np.nan})
    er = pd.DataFrame(event_rows)
    fp_rows=[]
    for trig in triggers:
        fut=z.loc[trig:trig+pd.Timedelta(days=60),"dd252"].dropna()
        if not bool((fut<=-0.15).any()): fp_rows.append({"trigger":trig.date().isoformat(),"fp":True})
    fp=pd.DataFrame(fp_rows)
    benchmarks=[]
    for name,date in {"2000_dotcom":"2000-09-01","2008_gfc":"2008-01-22","2020_covid":"2020-03-16","2022_rates":"2022-03-07","2011_false_positive":"2011-08-03","2018_false_positive":"2018-12-24"}.items():
        ix=z.index[z.index>=pd.Timestamp(date)]
        if len(ix):
            t=ix[0]; benchmarks.append({"episode":name,"date":t.date().isoformat(),"kospi":float(z.loc[t,"kospi"]),"dd252":float(z.loc[t,"dd252"]),"l2_proxy":bool(z.loc[t,"l2_proxy"]),"inflationary_leg":bool(z.loc[t,"inflationary_leg"]),"financial_leg":bool(z.loc[t,"financial_leg"]),"coverage_credit_available":bool(pd.notna(z.loc[t,"BAMLH0A0HYM2"]))})
    b=pd.DataFrame(benchmarks)
    pd.DataFrame(zone_map).to_csv(OUT/"absolute_to_drawdown_mapping.csv",index=False)
    if not det.empty: det.to_csv(OUT/"korea_layer_entry_events.csv",index=False)
    pd.DataFrame(summaries).to_csv(OUT/"korea_layer_entry_summary.csv",index=False)
    er.to_csv(OUT/"stress_convergence_kospi_events.csv",index=False); fp.to_csv(OUT/"stress_convergence_false_positives.csv",index=False); b.to_csv(OUT/"stress_convergence_benchmark_episodes.csv",index=False)
    metrics={"latest_date":latest.date().isoformat(),"latest_kospi":float(z.loc[latest,"kospi"]),"latest_252d_high":current_high,"l2_proxy_trigger_count":int(z["l2_proxy"].sum()),"drawdown_event_count":len(er),"detected_events":int(er["trigger"].notna().sum()) if not er.empty else 0,"missed_events":int(er["trigger"].isna().sum()) if not er.empty else 0,"false_positive_count":len(fp),"median_lead_days":float(er["lead_days"].median()) if not er.empty and er["lead_days"].notna().any() else None,"mean_lead_days":float(er["lead_days"].mean()) if not er.empty and er["lead_days"].notna().any() else None,"coverage":coverage,"full_v02_score":False,"limitations":["Fed near-term hike probability not reconstructed","AI financing axis not reconstructed","HY OAS historical coverage is reported and not imputed","absolute 6000-6750 levels are not treated as stationary across history"]}
    (OUT/"coverage.json").write_text(json.dumps(coverage,ensure_ascii=False,default=str,indent=2),encoding="utf-8")
    (OUT/"run_metrics.json").write_text(json.dumps(metrics,ensure_ascii=False,default=str,indent=2),encoding="utf-8")
    lines=["# Korea Layer Backtest v0.1b","",f"Latest KOSPI: {metrics['latest_kospi']:,.2f}",f"Latest 252d high: {metrics['latest_252d_high']:,.2f}","","## Interpretation","Absolute 6,000–6,750 zones are mapped into drawdown-equivalent intervals for historical comparison.",f"L2 proxy triggers: {metrics['l2_proxy_trigger_count']}",f"KOSPI >=15% drawdown episodes: {metrics['drawdown_event_count']}",f"Detected with prior L2 proxy: {metrics['detected_events']}",f"Missed: {metrics['missed_events']}",f"False-positive triggers (no >=15% DD in 60d): {metrics['false_positive_count']}",f"Median lead: {metrics['median_lead_days']}",f"Mean lead: {metrics['mean_lead_days']}","","## Limitation","This run is a v0.2 topology proxy, not the complete 0–24 score, because Fed-futures probability and AI-financing history are not reconstructed."]
    (OUT/"RESULT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(metrics,ensure_ascii=False,default=str,sort_keys=True))

if __name__ == "__main__":
    main()
