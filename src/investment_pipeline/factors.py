from __future__ import annotations

import pandas as pd


def _pct_rank(history: pd.Series, value: float) -> float | None:
    h = pd.to_numeric(history, errors="coerce").dropna()
    if pd.isna(value) or h.empty:
        return None
    return float((h <= value).mean() * 100.0)


def normalize_point_in_time(factors: pd.DataFrame, factor_columns: list[str], as_of_col: str = "as_of", lower_is_better: set[str] | None = None) -> pd.DataFrame:
    lower_is_better = lower_is_better or set()
    out = factors.copy()
    out[as_of_col] = pd.to_datetime(out[as_of_col], utc=True)
    for col in factor_columns:
        scores = []
        for _, row in out.iterrows():
            history = out.loc[out[as_of_col] <= row[as_of_col], col]
            score = _pct_rank(history, row[col])
            if score is not None and col in lower_is_better:
                score = 100.0 - score
            scores.append(score)
        out[f"{col}_score"] = scores
    return out


def build_raw_factors(eod: pd.DataFrame, flow: pd.DataFrame, sector: pd.DataFrame, financials: pd.DataFrame) -> pd.DataFrame:
    df = eod.copy()
    df["as_of"] = pd.to_datetime(df["as_of"], utc=True)
    df = df.sort_values(["ticker", "as_of"])
    g = df.groupby("ticker", group_keys=False)
    for n in (5, 20, 60, 120):
        df[f"return_{n}d"] = g["close"].pct_change(n)
    for n in (20, 60, 120):
        ma = g["close"].transform(lambda s: s.rolling(n, min_periods=n).mean())
        df[f"ma_distance_{n}d"] = df["close"] / ma - 1.0
    df["turnover"] = df["close"] * df["volume"]
    df["volatility_20d"] = g["close"].transform(lambda s: s.pct_change().rolling(20, min_periods=20).std())
    df["drawdown_120d"] = g["close"].transform(lambda s: s / s.rolling(120, min_periods=120).max() - 1.0)

    if not flow.empty:
        f = flow.copy()
        f["as_of"] = pd.to_datetime(f["as_of"], utc=True)
        df = df.merge(f[["ticker", "as_of", "foreign_net", "institution_net"]], on=["ticker", "as_of"], how="left")
        for col in ("foreign_net", "institution_net"):
            df[f"{col}_20d"] = df.groupby("ticker")[col].transform(lambda s: s.rolling(20, min_periods=20).sum())

    if not sector.empty:
        s = sector.copy()
        s["as_of"] = pd.to_datetime(s["as_of"], utc=True)
        df = df.merge(s[["ticker", "as_of", "sector_code", "sector_return_20d", "sector_return_60d", "sector_breadth"]], on=["ticker", "as_of"], how="left")

    if not financials.empty:
        fin = financials.copy()
        fin["available_at"] = pd.to_datetime(fin["available_at"], utc=True)
        # Point-in-time join: latest financial fact whose availability timestamp is <= the market observation.
        df = pd.merge_asof(
            df.sort_values(["ticker", "as_of"]),
            fin.sort_values(["ticker", "available_at"]),
            left_on="as_of", right_on="available_at", by="ticker", direction="backward", suffixes=("", "_fin")
        )
    return df
