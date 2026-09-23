#!/usr/bin/env python3
"""Capture KIS evidence for the entry-timing research gate.

No order/trading path exists. Missing credentials or source data fail closed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

BASE = "https://openapi.koreainvestment.com:9443"
RULE_VERSION = "entry-evidence-instrumentation-v1"
ESTIMATE_TR = "HHPTJ04160200"
INVESTOR_TR = "FHKST01010900"
MINUTE_TR = "FHKST03010230"
DEFAULT_SYMBOLS = ["005930","000660","006400","105560","005380","000810","096770","034020","035420","207940"]

http = requests.Session()
http.headers.update({"User-Agent": "investment-entry-evidence/1.0"})

def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")

def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"missing required environment variable: {name}")
    return value

def sha256_bytes(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()

def sha256_json(payload: Any) -> str:
    return sha256_bytes(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",",":")).encode())

def write_json(path: Path, payload: Any) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False, indent=2).encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    return {"path": str(path), "sha256": sha256_bytes(body), "bytes": len(body)}

def issue_token() -> str:
    appkey = require_env("KIS_APP_KEY")
    secret = require_env("KIS_APP_SECRET")
    response = http.post(f"{BASE}/oauth2/tokenP", json={
        "grant_type":"client_credentials","appkey":appkey,"appsecret":secret
    }, timeout=20)
    response.raise_for_status()
    payload = response.json()
    if payload.get("rt_cd") not in (None,"0") or not payload.get("access_token"):
        raise RuntimeError(f"KIS token failure: {payload}")
    return str(payload["access_token"])

def kis_get(token: str, path: str, tr_id: str, params: dict[str, Any]) -> dict[str, Any]:
    response = http.get(f"{BASE}{path}", params=params, headers={
        "authorization":f"Bearer {token}",
        "appkey":require_env("KIS_APP_KEY"),
        "appsecret":require_env("KIS_APP_SECRET"),
        "tr_id":tr_id,
        "custtype":"P",
    }, timeout=20)
    response.raise_for_status()
    payload = response.json()
    if payload.get("rt_cd") not in (None,"0"):
        raise RuntimeError(f"KIS API failure {tr_id}: {payload}")
    return payload

def fetch_estimate(token: str, symbol: str) -> dict[str, Any]:
    return kis_get(token, "/uapi/domestic-stock/v1/quotations/investor-trend-estimate", ESTIMATE_TR,
                    {"MKSC_SHRN_ISCD":symbol})

def fetch_daily_investor(token: str, symbol: str) -> dict[str, Any]:
    return kis_get(token, "/uapi/domestic-stock/v1/quotations/inquire-investor", INVESTOR_TR,
                    {"FID_COND_MRKT_DIV_CODE":"J","FID_INPUT_ISCD":symbol})

def fetch_minute(token: str, symbol: str, date_yyyymmdd: str, hour: str) -> dict[str, Any]:
    return kis_get(token, "/uapi/domestic-stock/v1/quotations/inquire-time-dailychartprice", MINUTE_TR, {
        "FID_COND_MRKT_DIV_CODE":"J","FID_INPUT_ISCD":symbol,
        "FID_INPUT_HOUR_1":hour,"FID_INPUT_DATE_1":date_yyyymmdd,
        "FID_PW_DATA_INCU_YN":"Y","FID_FAKE_TICK_INCU_YN":"",
    })

def first_regular_bar(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    rows = [r for r in rows if r.get("stck_cntg_hour")]
    rows.sort(key=lambda r: str(r["stck_cntg_hour"]))
    return next((r for r in rows if str(r["stck_cntg_hour"]) >= "090000"), None)

def to_num(value: Any) -> float | None:
    if value in (None,""): return None
    try: return float(value)
    except (TypeError,ValueError): return None

def derive_gap(previous_close: Any, session_open: Any) -> float | None:
    prev, op = to_num(previous_close), to_num(session_open)
    if prev in (None,0) or op is None: return None
    return (op/prev - 1.0)*100.0

def kst_bar_timestamp(date_yyyymmdd: str, hhmmss: str) -> str:
    return f"{date_yyyymmdd[:4]}-{date_yyyymmdd[4:6]}-{date_yyyymmdd[6:8]}T{hhmmss[:2]}:{hhmmss[2:4]}:{hhmmss[4:6]}+09:00"

def collect_minute(token: str, symbol: str, date_yyyymmdd: str, raw_dir: Path, artifacts: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    rows: list[dict[str, Any]] = []
    summary = None
    cursor = "153000"
    for page in range(1,11):
        payload = fetch_minute(token, symbol, date_yyyymmdd, cursor)
        h = sha256_json(payload)
        artifacts.append(write_json(raw_dir/symbol/date_yyyymmdd/f"minute_{page:02d}_{h[:12]}.json", payload))
        output = payload.get("output2") or []
        if summary is None: summary = payload.get("output1") or {}
        if not output: break
        rows.extend(output)
        times = [str(r["stck_cntg_hour"]) for r in output if r.get("stck_cntg_hour")]
        if not times: break
        earliest = min(times)
        if earliest <= "090000" or len(output) < 120: break
        cursor = earliest
        time.sleep(0.2)
    unique = {str(r["stck_cntg_hour"]): r for r in rows if r.get("stck_cntg_hour")}
    return [unique[k] for k in sorted(unique)], summary

def build_records(run_id: str, symbol: str, requested_date: str, estimate: dict[str,Any],
                  daily: dict[str,Any], minute_rows: list[dict[str,Any]], summary: dict[str,Any] | None,
                  captured_at: str) -> list[dict[str,Any]]:
    out: list[dict[str,Any]] = []

    for row in estimate.get("output2") or []:
        out.append({"run_id":run_id,"evidence_type":"foreign_flow_estimate","symbol":symbol,
                    "observation_date":requested_date,"observed_at":captured_at,"available_at":captured_at,
                    "timestamp_semantics":"COLLECTOR_CAPTURE","quality_status":"AMBER",
                    "source_id":"KIS_OPEN_API","source_tr":ESTIMATE_TR,"rule_version":RULE_VERSION,
                    "sampling_class":"dealer_estimate","raw_payload":row})

    for row in daily.get("output") or []:
        d = str(row.get("stck_bsop_date") or requested_date)
        out.append({"run_id":run_id,"evidence_type":"foreign_flow_daily_confirmed","symbol":symbol,
                    "observation_date":d,"observed_at":f"{d[:4]}-{d[4:6]}-{d[6:8]}T15:30:00+09:00",
                    "available_at":captured_at,"timestamp_semantics":"DERIVED_SESSION_CLOSE",
                    "quality_status":"GREEN","source_id":"KIS_OPEN_API","source_tr":INVESTOR_TR,
                    "rule_version":RULE_VERSION,"foreign_net_buy_qty":to_num(row.get("frgn_ntby_qty")),
                    "foreign_net_buy_value":to_num(row.get("frgn_ntby_tr_pbmn")),"raw_payload":row})

    for row in minute_rows:
        t = str(row.get("stck_cntg_hour",""))
        observed = kst_bar_timestamp(requested_date,t) if len(requested_date)==8 and len(t)==6 else captured_at
        out.append({"run_id":run_id,"evidence_type":"intraday_1m","symbol":symbol,
                    "observation_date":requested_date,"observed_at":observed,"available_at":captured_at,
                    "timestamp_semantics":"SOURCE_BAR_TIME","quality_status":"GREEN",
                    "source_id":"KIS_OPEN_API","source_tr":MINUTE_TR,"rule_version":RULE_VERSION,
                    "open":to_num(row.get("stck_oprc")),"high":to_num(row.get("stck_hgpr")),
                    "low":to_num(row.get("stck_lwpr")),"close":to_num(row.get("stck_prpr")),
                    "volume":to_num(row.get("cntg_vol")),"raw_payload":row})

    first = first_regular_bar(minute_rows)
    prev = to_num(first.get("stck_prdy_clpr")) if first else None
    op = to_num(first.get("stck_oprc")) if first else None
    if prev is None and summary: prev = to_num(summary.get("stck_prdy_clpr"))
    gap = derive_gap(prev,op)
    if gap is not None:
        out.append({"run_id":run_id,"evidence_type":"opening_gap_derived","symbol":symbol,
                    "observation_date":requested_date,"observed_at":captured_at,"available_at":captured_at,
                    "timestamp_semantics":"DERIVED_FROM_SOURCE_BARS","quality_status":"GREEN",
                    "source_id":"KIS_OPEN_API","source_tr":MINUTE_TR,"rule_version":RULE_VERSION,
                    "previous_close":prev,"session_open":op,"gap_pct":gap,
                    "raw_payload":{"first_bar":first,"summary":summary}})
    return out

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True, help="YYYYMMDD trading date")
    ap.add_argument("--symbols", default=",".join(DEFAULT_SYMBOLS))
    ap.add_argument("--output", type=Path, default=Path("artifacts/entry_evidence"))
    ap.add_argument("--skip-daily-investor", action="store_true")
    args = ap.parse_args()
    symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")+"-"+hashlib.sha256(os.urandom(16)).hexdigest()[:8]
    out = args.output/run_id
    raw_dir = out/"raw"
    out.mkdir(parents=True, exist_ok=True)
    manifest = {"schema_version":"entry-evidence.v1","run_id":run_id,"rule_version":RULE_VERSION,
                "started_at":now_iso(),"requested_date":args.date,"symbols":symbols,
                "status":"DATA_NOT_READY","failures":{},"artifacts":[]}
    try:
        token = issue_token()
    except Exception as exc:
        manifest["failures"]["AUTH"] = f"{type(exc).__name__}: {exc}"
        manifest["completed_at"] = now_iso()
        (out/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
        print(json.dumps(manifest,ensure_ascii=False))
        return 2

    records=[]
    for symbol in symbols:
        captured = now_iso()
        try:
            estimate = fetch_estimate(token,symbol)
            h=sha256_json(estimate)
            manifest["artifacts"].append(write_json(raw_dir/symbol/args.date/f"estimate_{h[:12]}.json",estimate))
            daily = {} if args.skip_daily_investor else fetch_daily_investor(token,symbol)
            if daily:
                h=sha256_json(daily)
                manifest["artifacts"].append(write_json(raw_dir/symbol/args.date/f"investor_daily_{h[:12]}.json",daily))
            minute_rows, summary = collect_minute(token,symbol,args.date,raw_dir,manifest["artifacts"])
            records.extend(build_records(run_id,symbol,args.date,estimate,daily,minute_rows,summary,captured))
        except Exception as exc:
            manifest["failures"][symbol] = f"{type(exc).__name__}: {exc}"
        time.sleep(0.2)

    observations=out/"observations.jsonl"
    with observations.open("w",encoding="utf-8") as fh:
        for row in records: fh.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+"\n")
    manifest["artifacts"].append({"path":str(observations),"sha256":sha256_bytes(observations.read_bytes()),"bytes":observations.stat().st_size})
    manifest["completed_at"]=now_iso()
    manifest["counts"]={
        "all_records":len(records),
        "foreign_flow_estimate":sum(r["evidence_type"]=="foreign_flow_estimate" for r in records),
        "foreign_flow_daily_confirmed":sum(r["evidence_type"]=="foreign_flow_daily_confirmed" for r in records),
        "intraday_1m":sum(r["evidence_type"]=="intraday_1m" for r in records),
        "opening_gap_derived":sum(r["evidence_type"]=="opening_gap_derived" for r in records),
    }
    manifest["status"]="OK" if not manifest["failures"] else "PARTIAL_OK"
    (out/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(manifest,ensure_ascii=False))
    return 0 if manifest["status"]=="OK" else 2

if __name__=="__main__":
    raise SystemExit(main())
