from __future__ import annotations

from pathlib import Path

import pandas as pd

from .completeness import check_stock_snapshot
from .factors import build_raw_factors, normalize_point_in_time

UNIVERSE = {
    "005930": "삼성전자",
    "000660": "SK하이닉스",
    "006400": "삼성SDI",
    "105560": "KB금융",
    "005380": "현대차",
    "000810": "삼성화재",
    "096770": "SK이노베이션",
    "034020": "두산에너빌리티",
    "035420": "NAVER",
    "207940": "삼성바이오로직스",
}

REQUIRED_EOD = ["ticker", "as_of", "open", "high", "low", "close", "volume"]
REQUIRED_FLOW = ["ticker", "as_of", "foreign_net", "institution_net"]


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def build_factor_dataset(raw_dir: str | Path, out_dir: str | Path) -> dict:
    raw_dir, out_dir = Path(raw_dir), Path(out_dir)
    eod = _read_csv(raw_dir / "krx_eod.csv")
    flow = _read_csv(raw_dir / "krx_flow.csv")
    sector = _read_csv(raw_dir / "krx_sector.csv")
    financials = _read_csv(raw_dir / "opendart_financials.csv")

    report_eod = check_stock_snapshot(eod, UNIVERSE, REQUIRED_EOD)
    report_flow = check_stock_snapshot(flow, UNIVERSE, REQUIRED_FLOW)
    if report_eod.status != "GREEN" or report_flow.status != "GREEN":
        raise RuntimeError({"eod": report_eod.__dict__, "flow": report_flow.__dict__})

    raw = build_raw_factors(eod, flow, sector, financials)
    factor_cols = [c for c in raw.columns if c.startswith(("return_", "ma_distance_", "turnover", "volatility_", "drawdown_", "foreign_net", "institution_net", "sector_", "revenue_growth", "op_income_growth", "roe", "debt_ratio", "per", "pbr"))]
    normalized = normalize_point_in_time(raw, factor_cols, lower_is_better={"volatility_20d", "debt_ratio", "per", "pbr"})

    out_dir.mkdir(parents=True, exist_ok=True)
    raw.to_csv(out_dir / "raw_factors.csv", index=False, encoding="utf-8-sig")
    normalized.to_csv(out_dir / "normalized_factors.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame([{**report_eod.__dict__, "dataset": "krx_eod"}, {**report_flow.__dict__, "dataset": "krx_flow"}]).to_json(out_dir / "data_completeness.json", orient="records", force_ascii=False, indent=2)
    return {"eod": report_eod, "flow": report_flow, "rows": len(normalized)}
