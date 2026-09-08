#!/usr/bin/env python3
"""
Market Regime Judgment Framework v1.0, section 4.1/6.2/9 -- first exploratory backtest.

Scope: Korea (KOSPI/KOSDAQ), US (S&P 500/Russell 2000/VIX), Gold, Bitcoin
(context only), and bond-market series (UST 3M/2Y/10Y, HY OAS) from free,
no-auth public sources (FRED, Yahoo Finance chart API), following the same
fetch pattern already used by research/scripts/run_v0.2.3_daily_panel.py.

This is an EXPLORATORY run, not an OFFICIAL run under the reproducibility
gate documented in research/stress-convergence/README.md (no frozen
fixture/spec hash yet). It exists to produce this framework's first real
evidence for MARKET_REGIME_JUDGMENT_FRAMEWORK_v1.0.md section 9 (score-bucket
vs. forward-return) and to sanity-check the section 4.1/6.2 candidate
weights and cut points against actual history -- not to certify them.

Known, explicitly documented simplifications vs. the framework spec (see
framework section 12 for the follow-up work these motivate):
  - Breadth axis: no free constituent-level advance/decline data is
    available for KOSPI or the S&P 500, so Breadth is proxied by relative
    large-cap vs. small-cap performance (KOSPI vs. KOSDAQ; S&P 500 vs.
    Russell 2000), not the framework's full 5-component breadth table.
  - Risk axis: no free VIX term-structure (VIX3M) series was available, so
    the "VIX term structure" sub-component is dropped and the remaining
    Risk sub-weights are renormalized to sum to 1.
  - A single shared VIX + HY OAS credit read is used as the Risk-axis input
    for both the Korea-anchored and US-anchored regimes (no free Korea-local
    volatility index equivalent was available).
"""
import io
import math
from pathlib import Path

import numpy as np
import pandas as pd
import requests

OUT = Path("research/results/market_regime_v0.1")
OUT.mkdir(parents=True, exist_ok=True)

START = "1995-01-01"
END = pd.Timestamp.utcnow().tz_localize(None).strftime("%Y-%m-%d")
TRAILING_WINDOW = 756  # ~3 trading years, per framework section 4
MIN_PERIODS = 130      # ~6 months before a percentile score is produced
FORWARD_HORIZONS = [5, 20, 60, 120]

FRED_SERIES = {
    "DGS10": "UST10Y",
    "DGS2": "UST2Y",
    "DGS3MO": "UST3M",
    "DFII10": "REAL10Y",
    "DTWEXBGS": "DXY",
    "DCOILWTICO": "WTI",
}
HY_OAS_ARCHIVE_URL = "https://raw.githubusercontent.com/TGRADEA/gradea-fred-archive/main/BAMLH0A0HYM2.csv"

YAHOO_SERIES = {
    "%5EKS11": "KOSPI",
    "%5EKQ11": "KOSDAQ",
    "%5EGSPC": "SP500",
    "%5ERUT": "RUSSELL2000",
    "%5EVIX": "VIX",
    "%5ESOX": "SOX",
    "GC%3DF": "GOLD",
    "BTC-USD": "BTC",
    "KRW%3DX": "USDKRW",
}


def get_fred(series_id: str) -> pd.Series:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}&cosd={START}&coed={END}"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    d = pd.read_csv(io.StringIO(r.text))
    d.columns = ["date", series_id]
    d["date"] = pd.to_datetime(d["date"])
    d[series_id] = pd.to_numeric(d[series_id], errors="coerce")
    return d.set_index("date")[series_id]


def get_yahoo(symbol: str) -> pd.Series:
    p1 = int(pd.Timestamp(START, tz="UTC").timestamp())
    p2 = int((pd.Timestamp(END, tz="UTC") + pd.Timedelta(days=2)).timestamp())
    u = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        f"?period1={p1}&period2={p2}&interval=1d&events=history&includeAdjustedClose=true"
    )
    r = requests.get(u, headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
    r.raise_for_status()
    j = r.json()["chart"]["result"][0]
    dates = pd.to_datetime(j["timestamp"], unit="s", utc=True).tz_convert(None).normalize()
    vals = j["indicators"]["quote"][0]["close"]
    return pd.Series(vals, index=dates).astype(float)


def trailing_percentile(s: pd.Series, window=TRAILING_WINDOW, min_periods=MIN_PERIODS, invert=False) -> pd.Series:
    """Percentile rank of the last value within a trailing window ending at that
    date (no look-ahead), per framework section 4. invert=True means a HIGHER
    raw value should score LOWER (e.g. VIX, credit spreads, drawdown depth)."""
    x = -s if invert else s

    def f(a):
        return (a <= a[-1]).mean() * 100.0

    return x.rolling(window, min_periods=min_periods).apply(f, raw=True)


def weighted_axis(components: dict) -> pd.Series:
    """components: {name: (score_series 0-100, weight)}. Renormalizes weights
    over the components actually present (all are present here; kept generic
    in case a future run drops one)."""
    total_w = sum(w for _, w in components.values())
    out = None
    for _, (s, w) in components.items():
        term = s * (w / total_w)
        out = term if out is None else out.add(term, fill_value=np.nan)
    return out


def ma_alignment_score(price: pd.Series) -> pd.Series:
    ma20 = price.rolling(20).mean()
    ma60 = price.rolling(60).mean()
    ma200 = price.rolling(200).mean()
    full_up = (ma20 > ma60) & (ma60 > ma200)
    full_down = (ma20 < ma60) & (ma60 < ma200)
    partial_up = (ma20 > ma60) & ~full_up
    score = pd.Series(50.0, index=price.index)  # documented fallback for mixed cases
    score[full_up] = 100.0
    score[partial_up] = 60.0
    score[full_down] = 0.0
    return score


def build_trend_score(price: pd.Series) -> pd.Series:
    ret5 = price.pct_change(5)
    ret20 = price.pct_change(20)
    ret60 = price.pct_change(60)
    ret120 = price.pct_change(120)
    ma200 = price.rolling(200).mean()
    pos200 = price / ma200 - 1
    high52w = price.rolling(252, min_periods=60).max()
    drawdown = price / high52w - 1  # <= 0

    short_mom = (trailing_percentile(ret5) + trailing_percentile(ret20)) / 2
    med_mom = (trailing_percentile(ret60) + trailing_percentile(ret120)) / 2
    long_trend = trailing_percentile(pos200)
    align = ma_alignment_score(price)
    dd_score = trailing_percentile(drawdown)  # less negative (shallower) drawdown -> higher percentile -> higher score

    return weighted_axis({
        "short": (short_mom, 0.25),
        "med": (med_mom, 0.25),
        "long": (long_trend, 0.25),
        "align": (align, 0.15),
        "drawdown": (dd_score, 0.10),
    })


def build_breadth_proxy_score(large: pd.Series, small: pd.Series) -> pd.Series:
    rel20 = (small.pct_change(20)) - (large.pct_change(20))
    return trailing_percentile(rel20)


def build_risk_score(vix: pd.Series, price_for_vol: pd.Series, price_for_mdd: pd.Series, hy_oas: pd.Series) -> pd.Series:
    realized_vol = price_for_vol.pct_change().rolling(20).std() * math.sqrt(252)
    high = price_for_mdd.rolling(252, min_periods=60).max()
    mdd = price_for_mdd / high - 1

    vix_s = trailing_percentile(vix, invert=True)
    vol_s = trailing_percentile(realized_vol, invert=True)
    mdd_s = trailing_percentile(mdd)  # already signed <=0, shallower is higher
    credit_s = trailing_percentile(hy_oas, invert=True)

    return weighted_axis({
        "vix": (vix_s, 0.25 / 0.85),
        "vol": (vol_s, 0.20 / 0.85),
        "mdd": (mdd_s, 0.15 / 0.85),
        "credit": (credit_s, 0.25 / 0.85),
    })


def build_macro_score(ust10: pd.Series, ust2: pd.Series, ust3m: pd.Series, real10: pd.Series, dxy: pd.Series, hy_oas: pd.Series) -> pd.Series:
    curve_2 = ust10 - ust2
    curve_3m = ust10 - ust3m
    curve_2_s = trailing_percentile(curve_2)
    curve_3m_s = trailing_percentile(curve_3m)
    real_s = trailing_percentile(real10, invert=True)
    dxy_chg = dxy.pct_change(20)
    dxy_s = trailing_percentile(dxy_chg, invert=True)
    credit_s = trailing_percentile(hy_oas, invert=True)

    return weighted_axis({
        "curve_2y": (curve_2_s, 0.125),
        "curve_3m": (curve_3m_s, 0.125),
        "real_yield": (real_s, 0.20),
        "dollar": (dxy_s, 0.20),
        "credit": (credit_s, 0.35),
    })


def build_crossasset_score(us_eq: pd.Series, ust10: pd.Series, fx: pd.Series, fx_invert: bool, wti: pd.Series, gold: pd.Series, sox: pd.Series) -> pd.Series:
    eq_s = trailing_percentile(us_eq.pct_change(20))
    rate_s = trailing_percentile(ust10.diff(20))
    fx_s = trailing_percentile(fx.pct_change(20), invert=fx_invert)
    oil_s = trailing_percentile(wti.pct_change(20))
    gold_s = trailing_percentile(gold.pct_change(20), invert=True)
    sox_s = trailing_percentile(sox.pct_change(20))

    return weighted_axis({
        "us_eq": (eq_s, 0.30),
        "us_rate": (rate_s, 0.15),
        "fx": (fx_s, 0.15),
        "oil": (oil_s, 0.15),
        "gold": (gold_s, 0.10),
        "sox": (sox_s, 0.15),
    })


def regime_label(market_score, breadth_score, vix, hy_oas, drawdown_pct) -> pd.Series:
    """Section 6.2's boolean spec is "evaluated top-down, first matching rule
    wins" in the order R1, R2, R3, R4, R5, R6 -- so R1 has the highest
    precedence and R6 the lowest among the six masks below. Conditions are
    computed independently (not mutually exclusive by construction: e.g. a
    row can satisfy both R2 and R3 when Breadth>=50 but VIX>22), so precedence
    is enforced purely by write order: lowest-precedence label written first,
    highest-precedence label written last so it wins the overwrite."""
    ms, bs, v, hy, dd = market_score, breadth_score, vix, hy_oas, drawdown_pct
    r1 = (ms >= 80) & (bs >= 70) & (v <= 18) & (hy <= 250)
    r2 = (ms >= 60) & (ms < 80) & (bs >= 50)
    r3 = (ms >= 60) & ((bs < 50) | (v > 22))
    r4 = (ms >= 40) & (ms < 60)
    r5 = ((ms >= 20) & (ms < 40)) | ((dd < -15) & (v > 25))
    r6 = (ms < 20) | ((v > 35) & (hy > 500))

    out = pd.Series("R4", index=ms.index)  # fallback default for any unmatched row
    out[r6] = "R6"
    out[r5] = "R5"
    out[r4] = "R4"
    out[r3] = "R3"
    out[r2] = "R2"
    out[r1] = "R1"
    return out


def score_bucket_table(market_score: pd.Series, price: pd.Series, label: str) -> pd.DataFrame:
    rows = []
    buckets = [(0, 20), (20, 40), (40, 60), (60, 80), (80, 100)]
    for h in FORWARD_HORIZONS:
        fwd = price.shift(-h) / price - 1
        for lo, hi in buckets:
            upper = (market_score < hi) if hi < 100 else (market_score <= hi)
            mask = (market_score >= lo) & upper
            vals = fwd[mask].dropna()
            rows.append({
                "market": label, "horizon_days": h, "score_bucket": f"{lo}-{hi}",
                "n_obs": int(vals.shape[0]),
                "mean_fwd_return_pct": float(vals.mean() * 100) if len(vals) else math.nan,
                "median_fwd_return_pct": float(vals.median() * 100) if len(vals) else math.nan,
                "win_rate_pct": float((vals > 0).mean() * 100) if len(vals) else math.nan,
            })
    return pd.DataFrame(rows)


def regime_performance_table(regime: pd.Series, price: pd.Series, label: str, horizon=20) -> pd.DataFrame:
    fwd = price.shift(-horizon) / price - 1
    rows = []
    for r in ["R1", "R2", "R3", "R4", "R5", "R6"]:
        vals = fwd[regime == r].dropna()
        realized_vol = price.pct_change().rolling(horizon).std().reindex(vals.index)
        rows.append({
            "market": label, "regime": r, "horizon_days": horizon,
            "n_obs": int(vals.shape[0]),
            "mean_fwd_return_pct": float(vals.mean() * 100) if len(vals) else math.nan,
            "win_rate_pct": float((vals > 0).mean() * 100) if len(vals) else math.nan,
            "mean_realized_vol_ann_pct": float(realized_vol.mean() * math.sqrt(252) * 100) if len(vals) else math.nan,
            "worst_fwd_return_pct": float(vals.min() * 100) if len(vals) else math.nan,
        })
    return pd.DataFrame(rows)


def main():
    print("Downloading FRED series...")
    fred_raw = {sid: get_fred(sid) for sid in FRED_SERIES}
    fred = pd.concat({FRED_SERIES[k]: v for k, v in fred_raw.items()}, axis=1)

    print("Downloading HY OAS archive...")
    hy = requests.get(HY_OAS_ARCHIVE_URL, timeout=60)
    hy.raise_for_status()
    hy_s = pd.read_csv(io.StringIO(hy.text), parse_dates=["observation_date"]).set_index("observation_date")["value"]
    hy_s.name = "HY_OAS"

    print("Downloading Yahoo Finance series...")
    yahoo_raw = {}
    for sym, name in YAHOO_SERIES.items():
        try:
            yahoo_raw[name] = get_yahoo(sym)
        except Exception as e:
            print(f"  WARNING: failed to fetch {name} ({sym}): {e}")
    yahoo = pd.concat(yahoo_raw, axis=1)

    df = fred.join(hy_s, how="outer").join(yahoo, how="outer").sort_index()

    print("Per-series raw coverage (before ffill/dropna):")
    for col in df.columns:
        s = df[col].dropna()
        if len(s):
            print(f"  {col:12s} first={s.index.min().date()} last={s.index.max().date()} n={len(s)}")
        else:
            print(f"  {col:12s} NO DATA")

    ffill_cols = [c for c in df.columns if c not in ()]
    df[ffill_cols] = df[ffill_cols].ffill()
    required_cols = ["KOSPI", "SP500", "VIX", "HY_OAS", "UST10Y", "UST2Y", "UST3M"]
    df = df.dropna(subset=required_cols)

    print(f"Combined panel: {df.index.min().date()} to {df.index.max().date()}, {len(df)} rows")

    macro_score = build_macro_score(df["UST10Y"], df["UST2Y"], df["UST3M"], df["REAL10Y"], df["DXY"], df["HY_OAS"])
    risk_score = build_risk_score(df["VIX"], df["SP500"], df["SP500"], df["HY_OAS"])

    high52w_kospi = df["KOSPI"].rolling(252, min_periods=60).max()
    dd_kospi = (df["KOSPI"] / high52w_kospi - 1) * 100
    high52w_sp500 = df["SP500"].rolling(252, min_periods=60).max()
    dd_sp500 = (df["SP500"] / high52w_sp500 - 1) * 100

    regions = {}

    kr_trend = build_trend_score(df["KOSPI"])
    kr_breadth = build_breadth_proxy_score(df["KOSPI"], df["KOSDAQ"])
    kr_crossasset = build_crossasset_score(df["SP500"], df["UST10Y"], df["USDKRW"], True, df["WTI"], df["GOLD"], df["SOX"])
    kr_market = weighted_axis({
        "trend": (kr_trend, 0.25), "breadth": (kr_breadth, 0.20), "risk": (risk_score, 0.20),
        "macro": (macro_score, 0.20), "crossasset": (kr_crossasset, 0.15),
    })
    kr_regime = regime_label(kr_market, kr_breadth, df["VIX"], df["HY_OAS"], dd_kospi)
    regions["KOSPI"] = (kr_market, kr_breadth, kr_regime, df["KOSPI"])

    us_trend = build_trend_score(df["SP500"])
    us_breadth = build_breadth_proxy_score(df["SP500"], df["RUSSELL2000"])
    us_crossasset = build_crossasset_score(df["SP500"], df["UST10Y"], df["DXY"], True, df["WTI"], df["GOLD"], df["SOX"])
    us_market = weighted_axis({
        "trend": (us_trend, 0.25), "breadth": (us_breadth, 0.20), "risk": (risk_score, 0.20),
        "macro": (macro_score, 0.20), "crossasset": (us_crossasset, 0.15),
    })
    us_regime = regime_label(us_market, us_breadth, df["VIX"], df["HY_OAS"], dd_sp500)
    regions["SP500"] = (us_market, us_breadth, us_regime, df["SP500"])

    panel = pd.DataFrame({
        "KOSPI": df["KOSPI"], "SP500": df["SP500"], "GOLD": df["GOLD"], "BTC": df["BTC"],
        "VIX": df["VIX"], "HY_OAS": df["HY_OAS"], "UST10Y": df["UST10Y"], "UST2Y": df["UST2Y"], "UST3M": df["UST3M"],
        "Macro_Score": macro_score, "Risk_Score": risk_score,
        "KR_Trend": kr_trend, "KR_Breadth": kr_breadth, "KR_Market_Score": kr_market, "KR_Regime": kr_regime,
        "US_Trend": us_trend, "US_Breadth": us_breadth, "US_Market_Score": us_market, "US_Regime": us_regime,
    })
    panel.to_csv(OUT / "daily_panel.csv", index_label="date")

    bucket_tables = []
    regime_tables = []
    for label, (market, breadth, regime, price) in regions.items():
        bucket_tables.append(score_bucket_table(market, price, label))
        for h in FORWARD_HORIZONS:
            regime_tables.append(regime_performance_table(regime, price, label, horizon=h))

    bucket_df = pd.concat(bucket_tables, ignore_index=True)
    bucket_df.to_csv(OUT / "score_bucket_vs_forward_return.csv", index=False)
    regime_df = pd.concat(regime_tables, ignore_index=True)
    regime_df.to_csv(OUT / "regime_performance.csv", index=False)

    regime_counts = panel[["KR_Regime", "US_Regime"]].apply(lambda s: s.value_counts()).fillna(0).astype(int)
    regime_counts.to_csv(OUT / "regime_counts.csv")

    report_lines = [
        "# Market Regime v0.1 -- exploratory backtest run",
        "",
        f"Data window used: {df.index.min().date()} to {df.index.max().date()} ({len(df)} trading days).",
        "",
        "Status: EXPLORATORY. Not an OFFICIAL run under the stress-convergence-style",
        "reproducibility gate (no frozen fixture/spec hash). Produced to give this",
        "framework its first real section 9 evidence and sanity-check the section 4.1/6.2",
        "candidate weights and cut points -- not to certify them. See the script's",
        "module docstring for the documented simplifications (breadth proxy, dropped",
        "VIX term structure, shared VIX/HY-OAS risk read across both regions).",
        "",
        "## Score-bucket vs. forward-return (section 9)",
        "",
        bucket_df.to_markdown(index=False),
        "",
        "## Regime vs. realized performance (section 9)",
        "",
        regime_df.to_markdown(index=False),
        "",
        "## Regime day-count distribution",
        "",
        regime_counts.to_markdown(),
        "",
    ]
    (OUT / "report.md").write_text("\n".join(report_lines), encoding="utf-8")

    print("=== SCORE BUCKET VS FORWARD RETURN ===")
    print(bucket_df.to_string(index=False))
    print("=== REGIME PERFORMANCE ===")
    print(regime_df.to_string(index=False))
    print("=== REGIME COUNTS ===")
    print(regime_counts.to_string())


if __name__ == "__main__":
    main()
