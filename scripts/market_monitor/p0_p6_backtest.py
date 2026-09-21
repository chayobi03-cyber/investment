#!/usr/bin/env python3
"""Episode-clustered P0~P6 backtest harness. Fails closed until PIT history is complete."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from statistics import median
from typing import Any,Iterable

HORIZONS=(5,20,60)
REQUIRED={"date","asset_id","episode_id","close","price_signal"}

def load_jsonl(path:Path)->list[dict[str,Any]]:
    out=[]
    with path.open(encoding="utf-8") as f:
        for n,line in enumerate(f,1):
            if not line.strip(): continue
            row=json.loads(line)
            missing=REQUIRED-row.keys()
            if missing: raise ValueError(f"line {n}: missing fields {sorted(missing)}")
            out.append(row)
    return out

def signal_level(r):
    layers=[
      ["price_signal"],
      ["price_signal","price_location_pass"],
      ["price_signal","price_location_pass","extension_pass"],
      ["price_signal","price_location_pass","extension_pass","leadership_pass"],
      ["price_signal","price_location_pass","extension_pass","leadership_pass","macro_pass"],
      ["price_signal","price_location_pass","extension_pass","leadership_pass","macro_pass","attribution_pass"],
      ["price_signal","price_location_pass","extension_pass","leadership_pass","macro_pass","attribution_pass","fundamentals_pass"]]
    level=-1
    for i,fields in enumerate(layers):
        if all(bool(r.get(x)) for x in fields): level=i
    return level

def dedupe_episode_entries(rows,split):
    chosen=set(); out={i:[] for i in range(7)}
    for r in rows:
        if r.get("split")!=split: continue
        level=signal_level(r)
        if level<0: continue
        key=(str(r["asset_id"]),str(r["episode_id"]))
        if key in chosen: continue
        chosen.add(key)
        for p in range(level+1): out[p].append(r)
    return out

def metrics(rows:list[dict[str,Any]],universe_rows:Iterable[dict[str,Any]]):
    out={"n":len(rows)}
    base=sum(bool(r.get("price_signal")) for r in universe_rows)
    out["trigger_frequency"]=len(rows)/base if base else None
    for h in HORIZONS:
        rets=[]; maes=[]; rebound=[]
        for r in rows:
            series=r.get("asset_rows")
            if not isinstance(series,list): continue
            try: idx=next(i for i,x in enumerate(series) if x.get("date")==r["date"])
            except StopIteration: continue
            future=[x.get("close") for x in series[idx+1:idx+h+1] if x.get("close") is not None]
            if len(future)<h: continue
            entry=float(r["close"]); rets.append((float(future[-1])/entry-1)*100)
            maes.append(min((float(x)/entry-1)*100 for x in future))
            hit=next((j for j,x in enumerate(future,1) if float(x)>=entry),None)
            if hit is not None: rebound.append(hit)
        out[f"{h}d_mean_return"]=sum(rets)/len(rets) if rets else None
        out[f"{h}d_median_return"]=median(rets) if rets else None
        out[f"{h}d_positive_rate"]=sum(x>0 for x in rets)/len(rets) if rets else None
        out[f"{h}d_worst_return"]=min(rets) if rets else None
        out[f"{h}d_max_adverse_excursion"]=min(maes) if maes else None
        out[f"{h}d_time_to_rebound_median"]=median(rebound) if rebound else None
    return out

def run(path:Path):
    rows=load_jsonl(path)
    if len(rows)<1000: return {"status":"DATA_NOT_READY","reason":"at least 1000 PIT observation rows required"}
    needed={"price_location_pass","extension_pass","leadership_pass","macro_pass","attribution_pass","fundamentals_pass"}
    if not needed.issubset(rows[0]): return {"status":"DATA_NOT_READY","reason":f"missing gate fields: {sorted(needed-rows[0].keys())}"}
    if not all(isinstance(r.get("asset_rows"),list) for r in rows):
        return {"status":"DATA_NOT_READY","reason":"asset_rows history required for forward outcomes"}
    return {"status":"OK","splits":{
        s:{f"P{p}":metrics(dedupe_episode_entries(rows,s)[p],[r for r in rows if r.get("split")==s]) for p in range(7)}
        for s in ("development","validation","oos")}}

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("input",type=Path); ap.add_argument("--output",type=Path)
    a=ap.parse_args(); payload=json.dumps(run(a.input),ensure_ascii=False,indent=2)
    if a.output: a.output.write_text(payload+"\n",encoding="utf-8")
    print(payload)
