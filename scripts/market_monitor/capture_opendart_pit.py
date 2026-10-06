#!/usr/bin/env python3
"""Capture OpenDART filing history and immutable filing artifacts.

The collector deliberately downloads every regular-report filing returned by
OpenDART (including corrections) for the requested period. Each filing is
keyed by rcept_no and stored with its raw response hash and capture timestamp.

This is a capture layer only. A captured filing is not automatically a
promotion-grade PIT fact; downstream selection must use filing availability
time and a complete correction lineage.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen


BASE = "https://opendart.fss.or.kr/api"
DISCLOSURE_LIST = f"{BASE}/list.json"
XBRL_FILE = f"{BASE}/fnlttXbrl.xml"


class OpenDartCaptureError(RuntimeError):
    pass


def _json_get(url: str, params: dict[str, str]) -> dict[str, Any]:
    query = urlencode(params)
    request = Request(f"{url}?{query}", headers={"User-Agent": "investment-pit-capture/1.0"})
    with urlopen(request, timeout=30) as response:
        payload = response.read()
    try:
        return json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise OpenDartCaptureError(f"invalid JSON response from {url}") from exc


def _binary_get(url: str, params: dict[str, str]) -> bytes:
    query = urlencode(params)
    request = Request(f"{url}?{query}", headers={"User-Agent": "investment-pit-capture/1.0"})
    with urlopen(request, timeout=60) as response:
        return response.read()


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def capture_disclosures(
    *,
    crtfc_key: str,
    corp_code: str,
    start_date: str,
    end_date: str,
    output_dir: Path,
    download_xbrl: bool = True,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    base_params = {
        "crtfc_key": crtfc_key,
        "corp_code": corp_code,
        "bgn_de": start_date,
        "end_de": end_date,
        # N is required here: corrected filings must not be silently removed.
        "last_reprt_at": "N",
        "pblntf_ty": "A",
        "sort": "date",
        "sort_mth": "asc",
        "page_no": "1",
        "page_count": "100",
    }

    first = _json_get(DISCLOSURE_LIST, base_params)
    if str(first.get("status")) != "000":
        raise OpenDartCaptureError(
            f"OpenDART disclosure search failed: {first.get('status')} {first.get('message')}"
        )

    total_page = int(first.get("total_page") or 1)
    filings: list[dict[str, Any]] = []
    for page in range(1, total_page + 1):
        params = dict(base_params)
        params["page_no"] = str(page)
        payload = first if page == 1 else _json_get(DISCLOSURE_LIST, params)
        filings.extend(payload.get("list") or [])

    manifest = {
        "schema_version": "opendart-capture-v1",
        "source": "OpenDART",
        "source_id": "opendart-api",
        "corp_code": corp_code,
        "start_date": start_date,
        "end_date": end_date,
        "last_reprt_at": "N",
        "captured_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "filing_count": len(filings),
        "filings": [],
    }

    (output_dir / "disclosure_search_raw.json").write_text(
        json.dumps(
            {"source": "OpenDART", "response": first},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    for filing in filings:
        rcept_no = str(filing.get("rcept_no") or "").strip()
        if not rcept_no:
            raise OpenDartCaptureError("disclosure row without rcept_no")
        record = {
            "rcept_no": rcept_no,
            "corp_code": str(filing.get("corp_code") or corp_code),
            "corp_name": filing.get("corp_name"),
            "stock_code": filing.get("stock_code"),
            "report_nm": filing.get("report_nm"),
            "rcept_dt": filing.get("rcept_dt"),
            "source": "OpenDART",
            "availability_status": "FILING_RECEIVED",
        }

        if download_xbrl:
            raw = _binary_get(
                XBRL_FILE,
                {"crtfc_key": crtfc_key, "rcept_no": rcept_no},
            )
            xbrl_name = f"{rcept_no}.xbrl.zip"
            (output_dir / xbrl_name).write_bytes(raw)
            record["artifact"] = xbrl_name
            record["artifact_sha256"] = _sha256(raw)
            record["artifact_bytes"] = len(raw)

        manifest["filings"].append(record)

    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corp-code", required=True)
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--end-date", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--no-xbrl", action="store_true")
    args = parser.parse_args()

    key = os.environ.get("OPENDART_API_KEY", "").strip()
    if not key:
        print(json.dumps({
            "status": "DATA_NOT_READY",
            "reason": "OPENDART_API_KEY is not configured",
        }, ensure_ascii=False))
        return 2

    try:
        manifest = capture_disclosures(
            crtfc_key=key,
            corp_code=args.corp_code,
            start_date=args.start_date,
            end_date=args.end_date,
            output_dir=args.output,
            download_xbrl=not args.no_xbrl,
        )
    except OpenDartCaptureError as exc:
        print(json.dumps({"status": "DATA_NOT_READY", "reason": str(exc)}, ensure_ascii=False))
        return 2

    manifest["status"] = "CAPTURE_OK"
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
