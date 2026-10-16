#!/usr/bin/env python3
"""Dry Powder deployment ladder backtest (Allocation Rule v0.1 §7).

Question: a tranche of cash is to be moved into broad US equity. Which
deployment policy gives the best trade-off between terminal wealth, path
drawdown and the risk of never deploying?

Data: Shiller monthly S&P 500 (datasets/s-and-p-500 on GitHub), stored in
research/deployment-ladder/data. Prices are monthly averages of daily closes,
so drawdowns are shallower than on daily closes.

Conventions (no look-ahead):
- the signal at month t uses data up to and including month t;
- a buy decided at month t is executed at month t+1's price;
- the tranche starts as 100% cash at t0 and is evaluated at t0 + HORIZON.

This is research evidence, not a live trading rule.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "research/deployment-ladder/data/sp500_shiller_monthly_to_2026-09.csv"
OUT = ROOT / "research/deployment-ladder/results"

HORIZON = 36
HIGH_WINDOW = 12
FIRST_START = "1900-01-01"

# Cumulative fraction of the tranche deployed once the trailing-12M drawdown
# has touched each level. Stage 0 deploys at t0. Allocation Rule v0.1 §7 lists
# 20/20/25/25/30 (= 120%); normalized here to five equal stages.
LADDER = [(0.0, 0.20), (-0.10, 0.40), (-0.15, 0.60), (-0.20, 0.80), (-0.30, 1.00)]


def load(path: Path) -> pd.DataFrame:
    d = pd.read_csv(path, parse_dates=["Date"]).set_index("Date")
    price = d["SP500"].astype(float)
    div = d["Dividend"].replace(0.0, np.nan)
    # Dividends stop after mid-2023: carry the last observed yield forward.
    yld = (div / price).ffill()
    rate = d["Long Interest Rate"].replace(0.0, np.nan).ffill() / 100.0
    out = pd.DataFrame({"price": price})
    out["ret"] = (price + yld * price / 12.0) / price.shift(1) - 1.0
    out["cash_long"] = rate.shift(1) / 12.0
    out["cash_zero"] = 0.0
    out["dd"] = price / price.rolling(HIGH_WINDOW, min_periods=HIGH_WINDOW).max() - 1.0
    out["up"] = price > price.shift(1)
    return out


def ladder_fraction(min_dd: float, scale: float = 1.0) -> float:
    frac = 0.0
    for level, cum in LADDER:
        if min_dd <= level * scale:
            frac = cum
    return frac


def target_path(policy: str, dd: np.ndarray, up: np.ndarray) -> np.ndarray:
    """Cumulative deployed fraction decided at the end of each month 0..H-1."""
    h = len(dd)
    tgt = np.zeros(h)
    min_dd = 0.0
    stab_frac = 0.0
    # Optional "@<scale>" suffix multiplies every ladder level (sensitivity).
    policy, _, scale_s = policy.partition("@")
    scale = float(scale_s) if scale_s else 1.0
    for k in range(h):
        min_dd = min(min_dd, dd[k])
        raw = ladder_fraction(min_dd, scale)
        # Stabilized ladder: a touched stage only fires in an up month.
        if k == 0 or up[k]:
            stab_frac = max(stab_frac, raw)
        if policy == "LUMP":
            tgt[k] = 1.0
        elif policy.startswith("DCA"):
            n = int(policy[3:])
            tgt[k] = min(1.0, (k + 1) / n)
        elif policy == "LADDER":
            tgt[k] = raw
        elif policy == "LADDER_STAB":
            tgt[k] = stab_frac
        elif policy.startswith("HYBRID"):
            # HYBRID12 / HYBRID24 / HYBRID12_STAB: time floor + ladder.
            name, _, stab = policy.partition("_")
            n = int(name[6:])
            floor = min(1.0, (k + 1) / n)
            tgt[k] = max(floor, stab_frac if stab else raw)
        else:
            raise ValueError(policy)
    return np.maximum.accumulate(tgt)


def simulate(df: pd.DataFrame, i0: int, policy: str, cash_col: str) -> dict:
    sl = df.iloc[i0 : i0 + HORIZON + 1]
    tgt = target_path(policy, sl["dd"].to_numpy()[:HORIZON], sl["up"].to_numpy()[:HORIZON])
    ret = sl["ret"].to_numpy()
    rc = sl[cash_col].to_numpy()
    cash, eq, deployed = 1.0, 0.0, 0.0
    wealth = [1.0]
    for k in range(1, HORIZON + 1):
        # Decision at k-1 executes at month k: buy first, then month-k return.
        buy = min(cash, tgt[k - 1] - deployed) if tgt[k - 1] > deployed else 0.0
        cash -= buy
        eq += buy
        deployed += buy
        eq *= 1.0 + ret[k]
        cash *= 1.0 + rc[k]
        wealth.append(cash + eq)
    w = np.array(wealth)
    mdd = float((w / np.maximum.accumulate(w) - 1.0).min())
    full = np.argmax(tgt >= 0.999) + 1 if (tgt >= 0.999).any() else np.nan
    return {"terminal": w[-1], "mdd": mdd, "undeployed": 1.0 - deployed, "months_to_full": full}


POLICIES = [
    "LUMP",
    "DCA6",
    "DCA12",
    "LADDER",
    "LADDER_STAB",
    "HYBRID6_STAB",
    "HYBRID12",
    "HYBRID24",
    "HYBRID12_STAB",
    "HYBRID12_STAB@0.75",
    "HYBRID12_STAB@1.25",
]


def run(df: pd.DataFrame, cash_col: str) -> pd.DataFrame:
    starts = [
        i
        for i in range(len(df) - HORIZON)
        if df.index[i] >= pd.Timestamp(FIRST_START) and not np.isnan(df["dd"].iloc[i])
    ]
    rows = []
    for i in starts:
        for p in POLICIES:
            r = simulate(df, i, p, cash_col)
            r.update(start=df.index[i], policy=p, start_dd=df["dd"].iloc[i])
            rows.append(r)
    res = pd.DataFrame(rows)
    lump = res[res.policy == "LUMP"].set_index("start")["terminal"]
    res["rel_lump"] = res["terminal"] / res["start"].map(lump) - 1.0
    return res


def summarize(res: pd.DataFrame) -> pd.DataFrame:
    g = res.groupby("policy", sort=False)
    s = pd.DataFrame(
        {
            "n_starts": g.size(),
            "terminal_median": g["terminal"].median(),
            "terminal_p05": g["terminal"].quantile(0.05),
            "rel_lump_median": g["rel_lump"].median(),
            "rel_lump_p05": g["rel_lump"].quantile(0.05),
            "rel_lump_p95": g["rel_lump"].quantile(0.95),
            "beats_lump": g["rel_lump"].apply(lambda x: float((x > 0).mean())),
            "mdd_median": g["mdd"].median(),
            "mdd_p05": g["mdd"].quantile(0.05),
            "undeployed_mean": g["undeployed"].mean(),
            "undeployed_gt50": g["undeployed"].apply(lambda x: float((x > 0.5).mean())),
        }
    )
    return s.round(4)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", type=Path, default=DATA)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    df = load(args.data)

    report: dict[str, dict] = {}
    for cash_col in ["cash_zero", "cash_long"]:
        res = run(df, cash_col)
        cuts = {
            "all": res,
            "start_near_high(dd>-5%)": res[res.start_dd > -0.05],
            "start_in_correction(dd<=-10%)": res[res.start_dd <= -0.10],
            "1900-1949": res[res.start < "1950-01-01"],
            "1950-1999": res[(res.start >= "1950-01-01") & (res.start < "2000-01-01")],
            "2000-2023": res[res.start >= "2000-01-01"],
        }
        for name, sub in cuts.items():
            s = summarize(sub)
            key = f"{cash_col}|{name}"
            report[key] = s.to_dict(orient="index")
            print(f"\n=== cash={cash_col} | {name} ===")
            print(s.to_string())
        res.to_csv(args.out / f"starts_{cash_col}.csv", index=False)

    (args.out / "summary.json").write_text(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
