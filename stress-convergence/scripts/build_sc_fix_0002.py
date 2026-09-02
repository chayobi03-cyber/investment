#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import io
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "fixtures" / "SC-FIX-0002"
RAW = OUT / "raw"
OUT.mkdir(parents=True, exist_ok=True)
RAW.mkdir(parents=True, exist_ok=True)

START = "1993-01-01"
END = "2022-01-10"
FRED = ["DGS10", "DGS2", "CPIAUCSL", "UNRATE"]
HY_URL = "https://raw.githubusercontent.com/TGRADEA/gradea-fred-archive/main/BAMLH0A0HYM2.csv"

WINDOWS = [
    ("1994_tightening", "1994-01-01", "1994-12-31", None, "FP"),
    ("2000_dotcom", "1999-01-01", "2000-03-24", "2000-03-24", "CRISIS"),
    ("2004_05_tightening", "2004-01-01", "2005-12-31", None, "FP"),
    ("2008_gfc", "2006-01-01", "2007-10-09", "2007-10-09", "CRISIS"),
    ("2013_taper", "2013-05-01", "2013-09-30", None, "FP"),
    ("2016_china_energy", "2015-08-01", "2016-02-29", None, "FP"),
    ("2017_reflation_fed", "2016-11-01", "2017-12-31", None, "FP"),
    ("2018_q4_tightening_selloff", "2018-09-01", "2018-12-31", None, "FP"),
    ("2020_covid", "2019-01-01", "2020-02-19", "2020-02-19", "CRISIS"),
    ("2021_reflation_taper", "2021-01-01", "2021-12-31", None, "FP"),
    ("2022_rate_shock", "2021-01-01", "2022-01-03", "2022-01-03", "CRISIS"),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download_text(url: str, path: Path) -> None:
    r = requests.get(url, headers={"User-Agent": "stress-convergence/SC-FIX-0002"}, timeout=120)
    r.raise_for_status()
    path.write_text(r.text, encoding="utf-8")


def get_fred(sid: str) -> pd.Series:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&cosd={START}&coed={END}"
    path = RAW / f"{sid}.csv"
    download_text(url, path)
    d = pd.read_csv(path)
    d.columns = ["date", sid]
    d["date"] = pd.to_datetime(d["date"])
    d[sid] = pd.to_numeric(d[sid], errors="coerce")
    return d.set_index("date")[sid]


def get_yahoo(symbol: str, filename: str) -> pd.Series:
    p1 = int(pd.Timestamp(START, tz="UTC").timestamp())
    p2 = int((pd.Timestamp(END, tz="UTC") + pd.Timedelta(days=2)).timestamp())
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        f"?period1={p1}&period2={p2}&interval=1d&events=history&includeAdjustedClose=true"
    )
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=120)
    r.raise_for_status()
    path = RAW / filename
    path.write_text(r.text, encoding="utf-8")
    j = r.json()["chart"]["result"][0]
    dates = pd.to_datetime(j["timestamp"], unit="s", utc=True).tz_convert(None).normalize()
    vals = j["indicators"]["quote"][0]["close"]
    return pd.Series(vals, index=dates).astype(float)


raw = {s: get_fred(s) for s in FRED}

df = pd.concat(raw, axis=1)

hy_path = RAW / "BAMLH0A0HYM2.csv"
download_text(HY_URL, hy_path)
hy = (
    pd.read_csv(hy_path, parse_dates=["observation_date"])
    .set_index("observation_date")["value"]
    .rename("BAMLH0A0HYM2")
)

sp = get_yahoo("%5EGSPC", "SP500.json").rename("SP500")
vix = get_yahoo("%5EVIX", "VIXCLS.json").rename("VIXCLS")

df = df.join([hy, sp, vix], how="outer").sort_index()
df[["CPIAUCSL", "UNRATE"]] = df[["CPIAUCSL", "UNRATE"]].ffill()
df[["DGS10", "DGS2", "BAMLH0A0HYM2", "SP500", "VIXCLS"]] = df[["DGS10", "DGS2", "BAMLH0A0HYM2", "SP500", "VIXCLS"]].ffill()

r_low = df["DGS10"].rolling("365D", min_periods=20).min()
df["R"] = (df["DGS10"] >= r_low + 0.40).fillna(False).astype(bool)

cpi_month = raw["CPIAUCSL"].dropna().resample("MS").last()
cpi_yoy = cpi_month.pct_change(12) * 100
i_month = ((cpi_yoy - cpi_yoy.shift(3)) >= 0.40).fillna(False).astype(bool)
df["I"] = i_month.reindex(df.index, method="ffill").fillna(False).astype(bool)

l_low = df["UNRATE"].rolling("365D", min_periods=3).min()
df["L"] = (df["UNRATE"] >= l_low + 0.30).fillna(False).astype(bool)

c_low = df["BAMLH0A0HYM2"].rolling("183D", min_periods=20).min()
df["C"] = (df["BAMLH0A0HYM2"] >= c_low + 0.75).fillna(False).astype(bool)

v25 = df["VIXCLS"] >= 25
df["V"] = (v25.rolling(5, min_periods=5).sum() >= 5).fillna(False).astype(bool)

sp_hi = df["SP500"].rolling(60, min_periods=20).max()
df["E"] = (df["SP500"] <= sp_hi * 0.90).fillna(False).astype(bool)

ri = df["R"] & df["I"]
weekly = ri.resample("W-FRI").last().fillna(False).astype(bool)
ew_week = weekly & weekly.shift(1, fill_value=False)
df["EARLY_WARNING"] = ew_week.reindex(df.index, method="ffill").fillna(False).astype(bool)
df["EW_ONSET"] = df["EARLY_WARNING"] & ~df["EARLY_WARNING"].shift(1, fill_value=False)

d2_low = df["DGS2"].rolling("365D", min_periods=20).min()
df["D2_BPS"] = (df["DGS2"] - d2_low) * 100
df["D2_BAND"] = pd.cut(df["D2_BPS"], [-np.inf, 40, 60, np.inf], labels=["<40", "40-60", ">=60"], right=False)
df["TIGHTENING_STATE"] = (df["EARLY_WARNING"] & (df["D2_BPS"] >= 40)).fillna(False).astype(bool)
df["TS_ONSET"] = df["TIGHTENING_STATE"] & ~df["TIGHTENING_STATE"].shift(1, fill_value=False)

credit = df["C"] & df["V"] & (df["L"] | df["E"])
growth = df["L"] & (df["E"] | df["V"]) & (df["C"] | df["R"])
df["CRISIS_CONFIRMATION"] = (credit | growth).fillna(False).astype(bool)
df["CC_ONSET"] = df["CRISIS_CONFIRMATION"] & ~df["CRISIS_CONFIRMATION"].shift(1, fill_value=False)

panel = df[[
    "R", "I", "L", "C", "V", "E", "EARLY_WARNING", "EW_ONSET",
    "D2_BPS", "D2_BAND", "TIGHTENING_STATE", "TS_ONSET",
    "CRISIS_CONFIRMATION", "CC_ONSET"
]]
panel_path = OUT / "daily_panel.csv"
panel.to_csv(panel_path, index_label="date")

try:
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT.parent.parent, text=True).strip()
except Exception:
    commit = "unknown"

retrieved = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
source_rows = []
for path, url in [
    *[(RAW / f"{s}.csv", f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={s}&cosd={START}&coed={END}") for s in FRED],
    (hy_path, HY_URL),
    (RAW / "SP500.json", "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC"),
    (RAW / "VIXCLS.json", "https://query1.finance.yahoo.com/v8/finance/chart/%5EVIX"),
]:
    source_rows.append({"file": str(path.relative_to(OUT)), "url": url, "sha256": sha256_file(path)})

manifest = {
    "fixture_id": "SC-FIX-0002",
    "version": "scope-corrected-provenance-aware-v1",
    "status": "RECONSTRUCTED_CI_GENERATED",
    "retrieved_at_utc": retrieved,
    "coverage": {"date_min": START, "date_max": END, "source_panel_rows": int(len(panel))},
    "benchmark_count": len(WINDOWS),
    "benchmark_scope": [
        {"window": n, "start": s, "end": e, "anchor": a, "kind": k}
        for n, s, e, a, k in WINDOWS
    ],
    "ttc_policy": {
        "crisis_link_max_days": 90,
        "link_requires_nonnegative_days": True,
        "link_requires_benchmark_scope": True,
        "out_of_window_confirmation_is_not_linked": True,
    },
    "source_snapshots": source_rows,
    "code_commit": commit,
    "runtime": {
        "python": platform.python_version(),
        "pandas": pd.__version__,
        "numpy": np.__version__,
        "requests": requests.__version__,
    },
    "derived_artifact": {
        "daily_panel.csv": sha256_file(panel_path),
    },
    "reproducibility_class": "reconstructed_from_frozen_source_snapshots",
    "comparison_note": "Do not treat differences vs SC-FIX-0001 as v0.2.4 improvements until fixture/provenance effects are separated.",
}

(OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(manifest, indent=2, ensure_ascii=False))
