#!/usr/bin/env python3
"""Canonical research pipeline primitives: observation -> shock -> freshness -> RS/breadth -> attribution -> episode."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
from typing import Any, Iterable, Mapping, Sequence

SCHEMA_VERSION = "3.0"
UTC = timezone.utc

def _iso(dt: datetime) -> str:
    return dt.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def _pct(current: float | None, base: float | None) -> float | None:
    if current is None or base in (None, 0): return None
    return (current / base - 1.0) * 100.0

def stable_id(*parts: object) -> str:
    return hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:16]

def build_observation(*, series_id: str, symbol: str, observed_at: datetime, available_at: datetime,
                      source: str, prices: Sequence[float], volumes: Sequence[float | None] | None = None,
                      revision_status: str = "final_or_vendor_current", asset_class: str = "equity",
                      session: str | None = None) -> dict[str, Any]:
    closes = [float(x) for x in prices if x is not None]
    if not closes: raise ValueError("prices must contain at least one non-null close")
    last = closes[-1]
    def lag(n: int) -> float | None:
        return _pct(last, closes[-(n+1)]) if len(closes) > n else None
    ma20 = sum(closes[-20:])/20 if len(closes)>=20 else None
    ma50 = sum(closes[-50:])/50 if len(closes)>=50 else None
    ma200 = sum(closes[-200:])/200 if len(closes)>=200 else None
    p20 = sum(closes[-40:-20])/20 if len(closes)>=40 else None
    p50 = sum(closes[-100:-50])/50 if len(closes)>=100 else None
    p200 = sum(closes[-400:-200])/200 if len(closes)>=400 else None
    def dd(window: int) -> float | None:
        xs=closes[-window:]
        return _pct(last, max(xs)) if xs else None
    up=down=0
    for i in range(len(closes)-1,0,-1):
        if closes[i] > closes[i-1]:
            if down: break
            up += 1
        elif closes[i] < closes[i-1]:
            if up: break
            down += 1
        else: break
    vol_anom=None
    if volumes is not None and len(volumes)>=21:
        vals=[v for v in volumes if v is not None]
        if len(vals)>=21 and vals[-1] is not None:
            base=sum(vals[-21:-1])/20
            vol_anom=vals[-1]/base if base else None
    return {
        "schema_version":SCHEMA_VERSION,"observation_id":stable_id(series_id,symbol,_iso(observed_at),source),
        "series_id":series_id,"symbol":symbol,"asset_class":asset_class,
        "observed_at":_iso(observed_at),"available_at":_iso(available_at),"source":source,
        "revision_status":revision_status,"session":session,"price":{"close":last},
        "returns_pct":{"d1":lag(1),"d3":lag(3),"d5":lag(5),"d20":lag(20),"d60":lag(60),"d120":lag(120),"d252":lag(252)},
        "location":{
            "distance_ma20_pct":_pct(last,ma20),"distance_ma50_pct":_pct(last,ma50),"distance_ma200_pct":_pct(last,ma200),
            "drawdown_20d_high_pct":dd(20),"drawdown_60d_high_pct":dd(60),"drawdown_120d_high_pct":dd(120),"drawdown_52w_high_pct":dd(252)},
        "trend":{
            "ma20_slope_pct":_pct(ma20,p20),"ma50_slope_pct":_pct(ma50,p50),"ma200_slope_pct":_pct(ma200,p200),
            "weekly_state":"UP" if (lag(20) or 0)>0 else "DOWN" if (lag(20) or 0)<0 else "UNKNOWN"},
        "structure":{
            "consecutive_up_sessions":up,"consecutive_down_sessions":down,"pullback_depth_pct":dd(20),
            "pullback_duration_sessions":None,"rebound_state":"UNKNOWN","breakout_state":"UNKNOWN",
            "gap_pct":None,"volume_anomaly_x":vol_anom},
        "quality":{"missing_fields":[],"conflict":False,"status":"GREEN"},
        "attribution":{"primary_category":"UNRESOLVED","secondary_categories":[],"confidence":"UNKNOWN",
                       "evidence_ids":[],"observed_persistence_sessions":None,"catalyst_date":None,"catalyst_age_sessions":None},
    }

def signed_shock(current: float | None, baseline: float | None, *, stress_polarity: int = 1) -> dict[str, Any]:
    if stress_polarity not in (-1,1): raise ValueError("stress_polarity must be -1 or +1")
    raw=_pct(current,baseline)
    if raw is None: return {"raw_pct":None,"stress_signed_pct":None,"direction":"UNKNOWN"}
    signed=raw*stress_polarity
    return {"raw_pct":raw,"stress_signed_pct":signed,
            "direction":"STRESS_INCREASING" if signed>0 else "STRESS_DECREASING" if signed<0 else "FLAT"}

def freshness(observed_at: datetime | str, available_at: datetime | str, now: datetime,
               *, max_observation_age_seconds: int, max_availability_lag_seconds: int) -> dict[str, Any]:
    def parse(x):
        if isinstance(x,datetime): return x.astimezone(UTC)
        return datetime.fromisoformat(x.replace("Z","+00:00")).astimezone(UTC)
    obs,av=parse(observed_at),parse(available_at)
    age=max(0.0,(now.astimezone(UTC)-obs).total_seconds())
    lag=max(0.0,(av-obs).total_seconds())
    status="STALE" if age>max_observation_age_seconds else "LATE_AVAILABLE" if lag>max_availability_lag_seconds else "FRESH"
    return {"status":status,"age_seconds":age,"availability_lag_seconds":lag,"fail_closed":status=="STALE"}

def relative_strength(asset_returns: Mapping[str,float|None], benchmark_return: float|None) -> dict[str,float|None]:
    return {k: None if v is None or benchmark_return is None else v-benchmark_return for k,v in asset_returns.items()}

def breadth_snapshot(returns_pct: Iterable[float|None], *, prices_above_ma: Iterable[bool|None] | None=None,
                     source_type: str="true_universe") -> dict[str,Any]:
    xs=[float(x) for x in returns_pct if x is not None]
    adv=sum(x>0 for x in xs); dec=sum(x<0 for x in xs)
    out={"source_type":source_type,"n":len(xs),"advancers":adv,"decliners":dec,
         "unchanged":len(xs)-adv-dec,"advance_ratio":adv/len(xs) if xs else None}
    if prices_above_ma is not None:
        ys=[x for x in prices_above_ma if x is not None]
        out["pct_above_ma"]=sum(bool(x) for x in ys)/len(ys) if ys else None
    return out

def attribution_record(*, material_move: bool, evidence: Sequence[Mapping[str,Any]] | None=None,
                       sector_rs: float|None=None, market_rs: float|None=None,
                       macro_shock_score: float|None=None, technical_confirmed: bool=False) -> dict[str,Any]:
    ev=list(evidence or [])
    if not material_move:
        return {"primary_category":"NONE_MATERIAL","secondary_categories":[],"confidence":"UNKNOWN",
                "evidence_ids":[],"basis":"move_not_material"}
    company=[e for e in ev if e.get("category")=="COMPANY_SPECIFIC" and e.get("direct")]
    sector=[e for e in ev if e.get("category")=="SECTOR_THEMATIC"]
    if company: primary,confidence,basis="COMPANY_SPECIFIC","VERIFIED","direct_company_evidence"
    elif len(sector)>=2 and sector_rs is not None and sector_rs>0: primary,confidence,basis="SECTOR_THEMATIC","CORROBORATED","sector_evidence_plus_relative_strength"
    elif macro_shock_score is not None and macro_shock_score>1.0 and (market_rs is None or abs(market_rs)<2.0):
        primary,confidence,basis="MACRO_CROSS_ASSET","INFERRED","macro_shock_plus_broad_move"
    elif technical_confirmed: primary,confidence,basis="TECHNICAL_FLOW","INFERRED","technical_confirmation_without_direct_catalyst"
    else: primary,confidence,basis="UNRESOLVED","UNKNOWN","insufficient_evidence"
    return {"primary_category":primary,
            "secondary_categories":sorted({e.get("category") for e in ev if e.get("category") and e.get("category")!=primary}),
            "confidence":confidence,"evidence_ids":[str(e["evidence_id"]) for e in ev if e.get("evidence_id")],
            "basis":basis}

@dataclass
class Episode:
    episode_id:str; cluster:str; asset_id:str; start:str; last:str
    max_stress:float=0.0; observations:int=0; closed:bool=False; end:str|None=None

@dataclass
class EpisodeEngine:
    trigger:float=1.0; rearm_below:float=0.25; cooldown_steps:int=5
    _active:dict[tuple[str,str],Episode]=field(default_factory=dict)
    _cooldown:dict[tuple[str,str],int]=field(default_factory=dict)
    completed:list[Episode]=field(default_factory=list)

    def update(self, *, cluster:str, asset_id:str, observed_at:datetime|str, stress_score:float) -> Episode|None:
        key=(cluster,asset_id); ts=_iso(observed_at) if isinstance(observed_at,datetime) else observed_at
        if key in self._cooldown:
            self._cooldown[key]-=1
            if self._cooldown[key]<=0: del self._cooldown[key]
        active=self._active.get(key)
        if active:
            active.last=ts; active.max_stress=max(active.max_stress,stress_score); active.observations+=1
            if stress_score<=self.rearm_below:
                active.closed=True; active.end=ts; self.completed.append(active); del self._active[key]; self._cooldown[key]=self.cooldown_steps
            return active
        if key in self._cooldown or stress_score<self.trigger: return None
        ep=Episode(stable_id(cluster,asset_id,ts),cluster,asset_id,ts,ts,max_stress=stress_score,observations=1)
        self._active[key]=ep
        return ep
