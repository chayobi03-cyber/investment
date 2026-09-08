from __future__ import annotations

import os
from datetime import date
from pathlib import Path

import pandas as pd
import requests


BASE = "https://opendart.fss.or.kr/api"


class OpenDARTClient:
    def __init__(self, api_key: str | None = None, timeout: int = 30):
        self.api_key = api_key or os.getenv("OPENDART_API_KEY")
        self.timeout = timeout
        if not self.api_key:
            raise ValueError("OPENDART_API_KEY is required")

    def _get(self, endpoint: str, params: dict) -> dict:
        p = {"crtfc_key": self.api_key, **params}
        r = requests.get(f"{BASE}/{endpoint}.json", params=p, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        if data.get("status") != "000":
            raise RuntimeError(f"OpenDART error {data.get('status')}: {data.get('message')}")
        return data

    def company(self, corp_code: str) -> dict:
        return self._get("company", {"corp_code": corp_code})

    def disclosures(self, bgn_de: date, end_de: date, corp_code: str | None = None) -> dict:
        params = {"bgn_de": bgn_de.strftime("%Y%m%d"), "end_de": end_de.strftime("%Y%m%d"), "page_no": 1, "page_count": 100}
        if corp_code:
            params["corp_code"] = corp_code
        return self._get("list", params)

    def full_financials(self, corp_code: str, bsns_year: int, reprt_code: str = "11011") -> pd.DataFrame:
        data = self._get("fnlttSinglAcntAll", {"corp_code": corp_code, "bsns_year": str(bsns_year), "reprt_code": reprt_code, "fs_div": "CFS"})
        rows = data.get("list", [])
        return pd.DataFrame(rows)

    def save_financials(self, corp_code: str, bsns_year: int, output: Path) -> Path:
        df = self.full_financials(corp_code, bsns_year)
        output.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output, index=False, encoding="utf-8-sig")
        return output


def require_env() -> None:
    if not os.getenv("OPENDART_API_KEY"):
        raise RuntimeError("Missing required environment variable: OPENDART_API_KEY")
