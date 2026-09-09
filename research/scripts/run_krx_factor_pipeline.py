#!/usr/bin/env python3
"""KRX EOD + 수급 + 섹터 3-stage factor pipeline (data completeness -> raw
factor -> normalized factor), for the 10-ticker universe agreed with the
user on 2026-09-08/09.

Scope note: OpenDART (financial-statement-level fundamentals: revenue,
margins, etc.) is NOT included yet -- it requires a user-issued API key
(opendart.fss.or.kr) that this session cannot obtain itself. This script
uses only KRX's own public data (via the `pykrx` library, no API key
required), which already includes per-ticker PER/PBR/EPS/BPS/DIV -- a
usable basic valuation factor without DART. A DART-based deeper
fundamentals layer can be added once DART_API_KEY exists as a repo
secret; see the "DART (not yet wired up)" section at the bottom.

Three stages, one CSV each, all indexed by ticker:

  1. data_completeness.csv  - per ticker/field, expected vs actual trading
     days in the lookback window, completeness %, and null counts. This
     stage's job is to surface gaps, not paper over them -- per this
     project's evidence discipline, a missing value is reported as
     missing, never silently imputed.
  2. raw_factors.csv        - momentum, volatility, drawdown, investor-flow
     sums, and KRX-published valuation ratios, computed as of the most
     recent trading day in the window.
  3. normalized_factors.csv - each raw factor converted to a cross-sectional
     percentile rank (0-100) within this 10-ticker universe. These
     percentile columns are the intended future inputs to the per-asset
     Buy Intensity / Risk Score framework
     (docs/governance/PER_ASSET_BUY_INTENSITY_RISK_SCORE_FRAMEWORK_v0.1.md)
     -- this script does NOT itself compute Buy Intensity or Risk Score;
     that synthesis step (which factor feeds which of the two scores, with
     what sign and weight) is deliberately left as a separate, explicit
     decision, not implied by running this pipeline.

Research pipeline only, not a live trading signal.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

try:
    from pykrx import stock
except ImportError as exc:  # pragma: no cover
    raise SystemExit(f"missing dependency: {exc}. Install with `pip install pykrx`.")

ROOT = Path(__file__).resolve().parents[1].parent
OUT = ROOT / "research/results/krx_factor_pipeline"
OUT.mkdir(parents=True, exist_ok=True)

TICKERS = {
    "005930": "삼성전자",
    "000660": "SK하이닉스",
    "042700": "한미반도체",
    "039030": "이오테크닉스",
    "357780": "솔브레인",
    "064760": "티씨케이",
    "014680": "한솔케미칼",
    "240810": "원익IPS",
    "069500": "KODEX 200",
    "091160": "KODEX 반도체",
}
# ETFs don't have meaningful per-share PER/PBR/EPS/BPS/DIV or investor-flow
# semantics identical to common stock -- flagged explicitly, not silently
# treated the same as the eight operating companies.
ETF_TICKERS = {"069500", "091160"}

LOOKBACK_DAYS = 400  # calendar days back, to comfortably cover 252 trading days for 52w-high
END = datetime.today()
START = END - timedelta(days=LOOKBACK_DAYS)
FROMDATE = START.strftime("%Y%m%d")
TODATE = END.strftime("%Y%m%d")

INVESTOR_COLUMNS_WANTED = ["기관합계", "외국인합계", "개인"]


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def find_sector_index_code(name_substring: str) -> tuple[str, str] | None:
    """Search KRX-published index codes for one whose name contains
    `name_substring` (e.g. '반도체'). Returns (code, full_name) or None.
    Markets are tried in order; the first match wins and is logged so the
    exact index used is auditable, not hardcoded from memory."""
    for market in ["KRX", "KOSPI", "KOSDAQ", "테마"]:
        try:
            codes = stock.get_index_ticker_list(market=market)
        except Exception as exc:  # noqa: BLE001
            log(f"WARN get_index_ticker_list(market={market}) failed: {type(exc).__name__}: {exc}")
            continue
        for code in codes:
            try:
                name = stock.get_index_ticker_name(code)
            except Exception:  # noqa: BLE001
                continue
            if name_substring in name:
                return code, name
    return None


def fetch_ticker_data(code: str) -> dict:
    result: dict = {"code": code, "name": TICKERS[code], "is_etf": code in ETF_TICKERS}

    try:
        ohlcv = stock.get_market_ohlcv(FROMDATE, TODATE, code)
        result["ohlcv"] = ohlcv
    except Exception as exc:  # noqa: BLE001
        log(f"ERROR OHLCV fetch failed for {code} ({TICKERS[code]}): {type(exc).__name__}: {exc}")
        result["ohlcv"] = pd.DataFrame()

    try:
        flow = stock.get_market_trading_value_by_date(FROMDATE, TODATE, code, on="순매수")
        result["flow"] = flow
    except Exception as exc:  # noqa: BLE001
        log(f"ERROR investor-flow fetch failed for {code} ({TICKERS[code]}): {type(exc).__name__}: {exc}")
        result["flow"] = pd.DataFrame()

    if code not in ETF_TICKERS:
        try:
            fundamental = stock.get_market_fundamental(FROMDATE, TODATE, code)
            result["fundamental"] = fundamental
        except Exception as exc:  # noqa: BLE001
            log(f"ERROR fundamental fetch failed for {code} ({TICKERS[code]}): {type(exc).__name__}: {exc}")
            result["fundamental"] = pd.DataFrame()
    else:
        result["fundamental"] = pd.DataFrame()

    return result


def completeness_row(code: str, name: str, field: str, df: pd.DataFrame, reference_days: int) -> dict:
    actual = int(len(df))
    pct = float(actual / reference_days * 100.0) if reference_days else float("nan")
    null_count = int(df.isna().sum().sum()) if not df.empty else None
    return {
        "ticker": code,
        "name": name,
        "field": field,
        "expected_trading_days": reference_days,
        "actual_rows": actual,
        "completeness_pct": round(pct, 1),
        "null_cell_count": null_count,
        "first_date": (df.index.min().date().isoformat() if not df.empty else None),
        "last_date": (df.index.max().date().isoformat() if not df.empty else None),
    }


def main() -> int:
    import os

    krx_login_configured = bool(os.getenv("KRX_ID") and os.getenv("KRX_PW"))
    dart_key_configured = bool(os.getenv("DART_API_KEY"))
    log(f"Window: {FROMDATE} - {TODATE} ({LOOKBACK_DAYS} calendar days)")
    log(
        f"KRX_ID/KRX_PW configured: {krx_login_configured} -- as of pykrx 1.2.8, "
        "investor-flow (get_market_trading_value_by_date), fundamental "
        "(get_market_fundamental), and index/sector data all require a "
        "logged-in KRX session; without KRX_ID/KRX_PW they return empty "
        "data, not partial data."
    )
    log(
        f"DART_API_KEY configured: {dart_key_configured} -- presence check only "
        "(value is never logged); this run does not yet call OpenDART even if "
        "the key is present -- that stage is still unbuilt, see the 'DART (not "
        "yet wired up)' note near the end of this script."
    )

    # Reference trading-day calendar from KOSPI index itself.
    # name_display=False avoids an internal get_index_ticker_name() lookup
    # that depends on a separate KRX "index master info" endpoint -- that
    # lookup is not needed just to read the OHLCV series and, in the first
    # run of this script (2026-09-09), crashed with KeyError: '지수명'
    # even though the OHLCV fetch itself had already succeeded.
    try:
        kospi = stock.get_index_ohlcv(FROMDATE, TODATE, "1001", name_display=False)  # 1001 = KOSPI composite
        reference_days = len(kospi)
        log(f"Reference trading days from KOSPI (code 1001): {reference_days}")
    except Exception as exc:  # noqa: BLE001
        log(f"ERROR could not fetch KOSPI reference calendar: {type(exc).__name__}: {exc}")
        kospi = pd.DataFrame()
        reference_days = 0

    sector_match = find_sector_index_code("반도체")
    if sector_match:
        sector_code, sector_name = sector_match
        log(f"Resolved sector index: {sector_code} = {sector_name}")
        try:
            sector_idx = stock.get_index_ohlcv(FROMDATE, TODATE, sector_code, name_display=False)
        except Exception as exc:  # noqa: BLE001
            log(f"ERROR sector index OHLCV fetch failed: {type(exc).__name__}: {exc}")
            sector_idx = pd.DataFrame()
    else:
        log(
            "WARN no '반도체' sector index resolved via get_index_ticker_list/name search "
            "-- this depends on KRX's index-master-info endpoint, which may itself require "
            "KRX_ID/KRX_PW; re-test once those are configured before assuming this is broken."
        )
        sector_idx = pd.DataFrame()
        sector_name = None

    per_ticker = {code: fetch_ticker_data(code) for code in TICKERS}

    # ---- Stage 1: data completeness ----
    completeness_rows = []
    for code, d in per_ticker.items():
        completeness_rows.append(completeness_row(code, d["name"], "ohlcv", d["ohlcv"], reference_days))
        completeness_rows.append(completeness_row(code, d["name"], "investor_flow", d["flow"], reference_days))
        if not d["is_etf"]:
            completeness_rows.append(completeness_row(code, d["name"], "fundamental", d["fundamental"], reference_days))
        else:
            completeness_rows.append(
                {
                    "ticker": code, "name": d["name"], "field": "fundamental",
                    "expected_trading_days": reference_days, "actual_rows": 0,
                    "completeness_pct": None, "null_cell_count": None,
                    "first_date": None, "last_date": None,
                }
            )
    completeness_rows.append(
        completeness_row("SECTOR", sector_name or "반도체(unresolved)", "sector_index", sector_idx, reference_days)
    )
    completeness_df = pd.DataFrame(completeness_rows)
    completeness_df.to_csv(OUT / "data_completeness.csv", index=False)

    # ---- Stage 2: raw factors ----
    sector_ret_60 = None
    if not sector_idx.empty and len(sector_idx) > 60:
        sector_ret_60 = float(sector_idx["종가"].iloc[-1] / sector_idx["종가"].iloc[-61] - 1.0)

    raw_rows = []
    for code, d in per_ticker.items():
        ohlcv = d["ohlcv"]
        flow = d["flow"]
        fundamental = d["fundamental"]
        row = {"ticker": code, "name": d["name"], "is_etf": d["is_etf"]}

        if not ohlcv.empty and "종가" in ohlcv.columns:
            close = ohlcv["종가"].astype(float)
            n = len(close)
            row["last_close"] = float(close.iloc[-1])
            row["last_date"] = close.index[-1].date().isoformat()
            for window, label in [(20, "mom_20"), (60, "mom_60"), (120, "mom_120")]:
                row[label] = float(close.iloc[-1] / close.iloc[-1 - window] - 1.0) if n > window else np.nan
            if n > 60:
                daily_ret = close.pct_change().dropna()
                row["vol_60"] = float(daily_ret.iloc[-60:].std() * np.sqrt(252))
            else:
                row["vol_60"] = np.nan
            roll_high = close.rolling(min(n, 252), min_periods=1).max()
            row["drawdown_from_52w_high"] = float(close.iloc[-1] / roll_high.iloc[-1] - 1.0)
            if sector_ret_60 is not None and n > 60:
                row["sector_rel_mom_60"] = float(row["mom_60"] - sector_ret_60) if not np.isnan(row.get("mom_60", np.nan)) else np.nan
            else:
                row["sector_rel_mom_60"] = np.nan
        else:
            for k in ["last_close", "last_date", "mom_20", "mom_60", "mom_120", "vol_60", "drawdown_from_52w_high", "sector_rel_mom_60"]:
                row[k] = np.nan

        if not flow.empty:
            available_cols = [c for c in INVESTOR_COLUMNS_WANTED if c in flow.columns]
            for col in available_cols:
                series = flow[col].astype(float)
                row[f"flow_{col}_20d_krw"] = float(series.iloc[-20:].sum()) if len(series) >= 1 else np.nan
            for col in INVESTOR_COLUMNS_WANTED:
                if col not in available_cols:
                    row[f"flow_{col}_20d_krw"] = np.nan
                    log(f"WARN investor column '{col}' not present for {code} ({d['name']}); available={list(flow.columns)}")
        else:
            for col in INVESTOR_COLUMNS_WANTED:
                row[f"flow_{col}_20d_krw"] = np.nan

        if not fundamental.empty:
            last_fund = fundamental.iloc[-1]
            for col in ["PER", "PBR", "DIV", "EPS", "BPS"]:
                row[col.lower()] = float(last_fund[col]) if col in fundamental.columns else np.nan
        else:
            for col in ["per", "pbr", "div", "eps", "bps"]:
                row[col] = np.nan

        raw_rows.append(row)

    raw_df = pd.DataFrame(raw_rows).set_index("ticker")
    raw_df.to_csv(OUT / "raw_factors.csv")

    # ---- Stage 3: cross-sectional normalized factors (percentile rank 0-100) ----
    factor_cols = [
        "mom_20", "mom_60", "mom_120", "vol_60", "drawdown_from_52w_high",
        "sector_rel_mom_60", "flow_기관합계_20d_krw", "flow_외국인합계_20d_krw",
        "flow_개인_20d_krw", "per", "pbr", "div",
    ]
    norm_df = raw_df[["name", "is_etf"]].copy()
    for col in factor_cols:
        if col not in raw_df.columns:
            continue
        valid = raw_df[col].dropna()
        if len(valid) < 2:
            norm_df[f"{col}_pctile"] = np.nan
            continue
        norm_df[f"{col}_pctile"] = raw_df[col].rank(pct=True, na_option="keep") * 100.0

    norm_df.to_csv(OUT / "normalized_factors.csv")

    metrics = {
        "run_date": END.date().isoformat(),
        "window_start": FROMDATE,
        "window_end": TODATE,
        "krx_login_configured": krx_login_configured,
        "dart_key_configured": dart_key_configured,
        "reference_trading_days_kospi": reference_days,
        "sector_index_resolved": sector_name,
        "tickers": TICKERS,
        "etf_tickers": sorted(ETF_TICKERS),
        "note": (
            "Stage 1-3 pipeline (data completeness -> raw factor -> "
            "normalized factor) using KRX public data via pykrx only. "
            "OpenDART financial-statement fundamentals not yet wired up "
            "(requires user-issued DART_API_KEY). Research pipeline only, "
            "not a live trading signal."
        ),
    }
    (OUT / "run_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("=== DATA COMPLETENESS ===")
    print(completeness_df.to_string(index=False))
    print("\n=== RAW FACTORS ===")
    print(raw_df.to_string())
    print("\n=== NORMALIZED FACTORS (percentile 0-100) ===")
    print(norm_df.to_string())

    # ---- DART (not yet wired up) ----
    # Once DART_API_KEY exists as a GitHub Actions secret, a follow-up
    # stage should fetch per-ticker financial statements (revenue, gross
    # margin, operating income, etc.) via OpenDART's fnlttSinglAcntAll.json
    # endpoint (needs each ticker's DART corp_code, obtained once from
    # corpCode.xml), append them as additional raw factors, and extend
    # Stage 3's percentile normalization to cover them. Not implemented
    # in this run.

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
