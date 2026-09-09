#!/usr/bin/env python3
"""KRX EOD + Naver investor-flow/valuation + sector 3-stage factor pipeline
(data completeness -> raw factor -> normalized factor), for the 10-ticker
universe agreed with the user on 2026-09-08/09.

Data source history (see git log for the full story):
  - EOD OHLCV: KRX public data via `pykrx` (works anonymously, no login).
  - Investor-type net-buy flow and PER/PBR/EPS/BPS/DIV: originally attempted
    via pykrx's KRX-hosted endpoints, but as of pykrx 1.2.8 those specific
    endpoints (and index/sector-index endpoints) require a logged-in KRX
    session (KRX_ID/KRX_PW). KRX itself moved to a member-only "Data
    Marketplace" on 2025-12-27 with Naver/Kakao social login as the
    promoted signup path, and pykrx has an open, unresolved compatibility
    issue for that change (github.com/sharebook-kr/pykrx/issues/244) as of
    this writing. Rather than block on that, this script sources
    investor-flow and valuation data directly from Naver Finance
    (finance.naver.com), an unrelated site with no such login gate.
  - Sector benchmark: rather than resolving a separate KRX sector index
    (also login-gated), this script reuses KODEX 반도체 (091160), which is
    already in the 10-ticker universe, as the semiconductor-sector proxy.
    The KOSPI reference trading-day calendar is likewise derived from
    KODEX 200 (069500)'s own OHLCV instead of a separate KOSPI index call.
  - OpenDART (financial-statement-level fundamentals: revenue, margins,
    etc.) is NOT included yet -- it requires a user-issued API key
    (opendart.fss.or.kr) that this session cannot obtain itself. See the
    "DART (not yet wired up)" note near the end of this script.

Three stages, one CSV each, all indexed by ticker:

  1. data_completeness.csv  - per ticker/field, expected vs actual trading
     days in the lookback window, completeness %, and null counts. This
     stage's job is to surface gaps, not paper over them -- per this
     project's evidence discipline, a missing value is reported as
     missing, never silently imputed.
  2. raw_factors.csv        - momentum, volatility, drawdown, investor-flow
     sums, and valuation ratios, computed as of the most recent trading
     day in the window.
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

import io
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import requests

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
MARKET_REFERENCE_TICKER = "069500"  # KODEX 200 stands in for a KOSPI trading-day calendar
SECTOR_REFERENCE_TICKER = "091160"  # KODEX 반도체 stands in for a semiconductor sector index

LOOKBACK_DAYS = 400  # calendar days back, to comfortably cover 252 trading days for 52w-high
END = datetime.today()
START = END - timedelta(days=LOOKBACK_DAYS)
FROMDATE = START.strftime("%Y%m%d")
TODATE = END.strftime("%Y%m%d")

NAVER_FLOW_PAGES = 7  # ~10 rows/page => up to ~70 trading days of investor flow
NAVER_HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
REQUEST_DELAY_SEC = 0.3  # be a polite scraper


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def fetch_naver_investor_flow(code: str) -> pd.DataFrame:
    """Scrapes finance.naver.com/item/frgn.naver for daily 기관/외국인 net
    trading volume (share counts, not KRW value -- see column names).
    Naver does not publish a direct 개인(individual) net-buy figure on this
    page; a residual approximation (-(기관+외국인)) is computed separately
    downstream and explicitly labeled as an estimate, not a measured value.
    """
    frames = []
    for page in range(1, NAVER_FLOW_PAGES + 1):
        url = f"https://finance.naver.com/item/frgn.naver?code={code}&page={page}"
        try:
            resp = requests.get(url, headers=NAVER_HEADERS, timeout=15)
            resp.encoding = "euc-kr"
            tables = pd.read_html(io.StringIO(resp.text))
        except Exception as exc:  # noqa: BLE001
            log(f"ERROR Naver investor-flow fetch failed for {code} page {page}: {type(exc).__name__}: {exc}")
            break
        time.sleep(REQUEST_DELAY_SEC)

        data_table = None
        for t in tables:
            cols = [str(c) for c in t.columns]
            if any("날짜" in c for c in cols) and any("기관" in c for c in cols):
                data_table = t
                break
        if data_table is None:
            log(f"WARN no matching investor-flow table found for {code} page {page}; table shapes={[t.shape for t in tables]}")
            break

        data_table = data_table.dropna(how="all")
        data_table = data_table[data_table.iloc[:, 0].astype(str).str.match(r"^\d{4}\.\d{2}\.\d{2}$", na=False)]
        if data_table.empty:
            break
        frames.append(data_table)

    if not frames:
        return pd.DataFrame()

    df = pd.concat(frames, ignore_index=True)
    df.columns = [str(c) for c in df.columns]
    date_col = next(c for c in df.columns if "날짜" in c)
    close_col = next((c for c in df.columns if "종가" in c), None)
    inst_col = next((c for c in df.columns if "기관" in c), None)
    frgn_col = next((c for c in df.columns if c.startswith("외국인") and "보유" not in c), None)

    df["date"] = pd.to_datetime(df[date_col], format="%Y.%m.%d")
    for c in [close_col, inst_col, frgn_col]:
        if c is not None:
            df[c] = pd.to_numeric(df[c].astype(str).str.replace(",", "", regex=False), errors="coerce")

    out = pd.DataFrame({"date": df["date"]})
    out["close"] = df[close_col] if close_col else np.nan
    out["inst_net_shares"] = df[inst_col] if inst_col else np.nan
    out["frgn_net_shares"] = df[frgn_col] if frgn_col else np.nan
    out = out.dropna(subset=["date"]).drop_duplicates(subset=["date"]).set_index("date").sort_index()
    return out


def fetch_naver_valuation(code: str) -> dict:
    """Scrapes finance.naver.com/item/main.naver for current PER/PBR/EPS/BPS
    and dividend yield. These are point-in-time snapshots (Naver's page
    shows the latest value, not a history), unlike the OHLCV/flow series."""
    url = f"https://finance.naver.com/item/main.naver?code={code}"
    result = {"per": np.nan, "pbr": np.nan, "eps": np.nan, "bps": np.nan, "div": np.nan}
    try:
        resp = requests.get(url, headers=NAVER_HEADERS, timeout=15)
        resp.encoding = "euc-kr"
        html = resp.text
    except Exception as exc:  # noqa: BLE001
        log(f"ERROR Naver valuation fetch failed for {code}: {type(exc).__name__}: {exc}")
        return result
    time.sleep(REQUEST_DELAY_SEC)

    def find_by_element_id(elem_id: str) -> float:
        # Naver's main.naver page renders these specific per-share metrics
        # inside elements with fixed, documented DOM ids (id="_per",
        # id="_eps", id="_pbr", id="_bps") -- anchoring on the id is far
        # more precise than matching the visible label text, which the
        # first live CI run (2026-09-09) showed picks up unrelated numbers
        # elsewhere on the page (e.g. legend/help text), producing
        # identical bogus values -- PBR=4.0 -- across every ticker.
        m = re.search(rf'id="{elem_id}"[^>]*>\s*([\-\d,]+\.?\d*)', html)
        if not m:
            return np.nan
        try:
            return float(m.group(1).replace(",", ""))
        except ValueError:
            return np.nan

    result["per"] = find_by_element_id("_per")
    result["eps"] = find_by_element_id("_eps")
    result["pbr"] = find_by_element_id("_pbr")
    result["bps"] = find_by_element_id("_bps")

    # No equally specific documented id is used here for dividend yield;
    # this remains a lower-confidence label-proximity match and may be
    # wrong or missing -- treated as NaN rather than guessed further if
    # it doesn't match cleanly.
    div_match = re.search(r"배당수익률[^\d\-]{0,40}?(-?[\d,]+\.?\d*)\s*(?:</[a-z]+>\s*)*%", html)
    if div_match:
        try:
            result["div"] = float(div_match.group(1).replace(",", ""))
        except ValueError:
            result["div"] = np.nan

    if all(np.isnan(v) for v in result.values()):
        log(f"WARN could not extract any valuation metric for {code} from Naver page -- id anchors may not match the live HTML structure")
    return result


def fetch_ticker_data(code: str) -> dict:
    result: dict = {"code": code, "name": TICKERS[code], "is_etf": code in ETF_TICKERS}

    try:
        ohlcv = stock.get_market_ohlcv(FROMDATE, TODATE, code)
        result["ohlcv"] = ohlcv
    except Exception as exc:  # noqa: BLE001
        log(f"ERROR OHLCV fetch failed for {code} ({TICKERS[code]}): {type(exc).__name__}: {exc}")
        result["ohlcv"] = pd.DataFrame()

    result["flow"] = fetch_naver_investor_flow(code)

    if code not in ETF_TICKERS:
        result["valuation"] = fetch_naver_valuation(code)
    else:
        result["valuation"] = {"per": np.nan, "pbr": np.nan, "eps": np.nan, "bps": np.nan, "div": np.nan}

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
    krx_login_configured = bool(os.getenv("KRX_ID") and os.getenv("KRX_PW"))
    dart_key_configured = bool(os.getenv("DART_API_KEY"))
    log(f"Window: {FROMDATE} - {TODATE} ({LOOKBACK_DAYS} calendar days)")
    log(
        f"KRX_ID/KRX_PW configured: {krx_login_configured} -- no longer needed by this "
        "script (investor-flow/valuation now sourced from Naver Finance instead of "
        "pykrx's KRX-login-gated endpoints); logged for visibility only."
    )
    log(
        f"DART_API_KEY configured: {dart_key_configured} -- presence check only "
        "(value is never logged); this run does not yet call OpenDART even if "
        "the key is present -- that stage is still unbuilt, see the 'DART (not "
        "yet wired up)' note near the end of this script."
    )

    per_ticker = {code: fetch_ticker_data(code) for code in TICKERS}

    reference_days = len(per_ticker[MARKET_REFERENCE_TICKER]["ohlcv"])
    log(f"Reference trading days from {TICKERS[MARKET_REFERENCE_TICKER]} ({MARKET_REFERENCE_TICKER}) OHLCV: {reference_days}")

    sector_ohlcv = per_ticker[SECTOR_REFERENCE_TICKER]["ohlcv"]
    sector_ret_60 = None
    if not sector_ohlcv.empty and "종가" in sector_ohlcv.columns and len(sector_ohlcv) > 60:
        sector_ret_60 = float(sector_ohlcv["종가"].iloc[-1] / sector_ohlcv["종가"].iloc[-61] - 1.0)

    # ---- Stage 1: data completeness ----
    completeness_rows = []
    for code, d in per_ticker.items():
        completeness_rows.append(completeness_row(code, d["name"], "ohlcv", d["ohlcv"], reference_days))
        completeness_rows.append(completeness_row(code, d["name"], "investor_flow", d["flow"], reference_days))
        val = d["valuation"]
        val_rows = 0 if all(pd.isna(v) for v in val.values()) else 1
        completeness_rows.append(
            {
                "ticker": code, "name": d["name"], "field": "valuation",
                "expected_trading_days": 1, "actual_rows": val_rows,
                "completeness_pct": (100.0 if val_rows else 0.0) if not d["is_etf"] else None,
                "null_cell_count": sum(1 for v in val.values() if pd.isna(v)) if not d["is_etf"] else None,
                "first_date": None, "last_date": None,
            }
        )
    completeness_df = pd.DataFrame(completeness_rows)
    completeness_df.to_csv(OUT / "data_completeness.csv", index=False)

    # ---- Stage 2: raw factors ----
    raw_rows = []
    for code, d in per_ticker.items():
        ohlcv = d["ohlcv"]
        flow = d["flow"]
        valuation = d["valuation"]
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
            if sector_ret_60 is not None and n > 60 and not np.isnan(row.get("mom_60", np.nan)):
                row["sector_rel_mom_60"] = float(row["mom_60"] - sector_ret_60)
            else:
                row["sector_rel_mom_60"] = np.nan
        else:
            for k in ["last_close", "last_date", "mom_20", "mom_60", "mom_120", "vol_60", "drawdown_from_52w_high", "sector_rel_mom_60"]:
                row[k] = np.nan

        if not flow.empty:
            inst_est_krw = (flow["inst_net_shares"] * flow["close"]).dropna()
            frgn_est_krw = (flow["frgn_net_shares"] * flow["close"]).dropna()
            row["flow_기관_20d_est_krw"] = float(inst_est_krw.iloc[-20:].sum()) if len(inst_est_krw) else np.nan
            row["flow_외국인_20d_est_krw"] = float(frgn_est_krw.iloc[-20:].sum()) if len(frgn_est_krw) else np.nan
            if not np.isnan(row["flow_기관_20d_est_krw"]) and not np.isnan(row["flow_외국인_20d_est_krw"]):
                row["flow_개인_20d_est_krw_residual"] = -(row["flow_기관_20d_est_krw"] + row["flow_외국인_20d_est_krw"])
            else:
                row["flow_개인_20d_est_krw_residual"] = np.nan
        else:
            row["flow_기관_20d_est_krw"] = np.nan
            row["flow_외국인_20d_est_krw"] = np.nan
            row["flow_개인_20d_est_krw_residual"] = np.nan

        for k, v in valuation.items():
            row[k] = v

        raw_rows.append(row)

    raw_df = pd.DataFrame(raw_rows).set_index("ticker")
    raw_df.to_csv(OUT / "raw_factors.csv")

    # ---- Stage 3: cross-sectional normalized factors (percentile rank 0-100) ----
    factor_cols = [
        "mom_20", "mom_60", "mom_120", "vol_60", "drawdown_from_52w_high",
        "sector_rel_mom_60", "flow_기관_20d_est_krw", "flow_외국인_20d_est_krw",
        "flow_개인_20d_est_krw_residual", "per", "pbr", "div",
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
        "reference_trading_days": reference_days,
        "market_reference_ticker": MARKET_REFERENCE_TICKER,
        "sector_reference_ticker": SECTOR_REFERENCE_TICKER,
        "investor_flow_source": "Naver Finance (finance.naver.com/item/frgn.naver), share-count based, KRW estimated as shares x close",
        "valuation_source": "Naver Finance (finance.naver.com/item/main.naver), point-in-time snapshot",
        "tickers": TICKERS,
        "etf_tickers": sorted(ETF_TICKERS),
        "note": (
            "Stage 1-3 pipeline (data completeness -> raw factor -> "
            "normalized factor). OHLCV from KRX via pykrx; investor-flow "
            "and valuation from Naver Finance (KRX's own login-gated "
            "endpoints are not used). OpenDART financial-statement "
            "fundamentals not yet wired up (requires user-issued "
            "DART_API_KEY). Research pipeline only, not a live trading "
            "signal."
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
