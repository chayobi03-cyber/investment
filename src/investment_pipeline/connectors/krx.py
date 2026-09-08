from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests


class KRXClient:
    """Authorized KRX Open API client.

    KRX endpoint/path names are configuration-driven because the approved service
    product and payload contract depend on the user's KRX API application.
    No undocumented web endpoint is hard-coded here.
    """

    def __init__(self, base_url: str | None = None, api_key: str | None = None, timeout: int = 30):
        self.base_url = (base_url or os.getenv("KRX_API_BASE_URL", "")).rstrip("/")
        self.api_key = api_key or os.getenv("KRX_API_KEY")
        self.timeout = timeout
        if not self.base_url:
            raise ValueError("KRX_API_BASE_URL is required")
        if not self.api_key:
            raise ValueError("KRX_API_KEY is required")

    def get_json(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        p = dict(params or {})
        p.setdefault("api_key", self.api_key)
        r = requests.get(f"{self.base_url}/{path.lstrip('/')}", params=p, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        if not isinstance(data, dict):
            raise TypeError("KRX API response must be an object")
        return data

    def fetch_dataset(self, path: str, params: dict[str, Any], output: Path) -> Path:
        data = self.get_json(path, params)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(__import__("json").dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return output


def require_env() -> None:
    for name in ("KRX_API_BASE_URL", "KRX_API_KEY"):
        if not os.getenv(name):
            raise RuntimeError(f"Missing required environment variable: {name}")
