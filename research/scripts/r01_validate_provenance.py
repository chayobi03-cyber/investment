"""Fail-closed R01 provenance validator.

Usage:
    python research/scripts/r01_validate_provenance.py docs/market/fixtures/r01/reb_house_price_2025-07_capture_manifest.yaml

The validator never promotes a source. It only reports whether the manifest
contains the mandatory evidence required by the R01 contract.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Any

import yaml


REQUIRED_FOR_PRIMARY = (
    "official_source",
    "observation_period",
    "publication",
    "availability",
    "revision",
    "raw_capture",
    "pit",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_manifest(manifest: dict[str, Any], base_dir: Path) -> dict[str, Any]:
    blockers: list[str] = []
    raw = manifest.get("raw_capture", {}) or {}
    publication = manifest.get("publication", {}) or {}
    availability = manifest.get("availability", {}) or {}
    revision = manifest.get("revision", {}) or {}
    pit = manifest.get("pit", {}) or {}

    if not manifest.get("source_id"):
        blockers.append("missing source_id")
    if not manifest.get("observation_period"):
        blockers.append("missing observation_period")
    if not publication.get("official_release_page"):
        blockers.append("missing official release page")
    if publication.get("actual_publication_date") is None:
        blockers.append("missing actual publication date")
    if availability.get("available_at") is None:
        blockers.append("missing available_at")
    if not raw.get("raw_capture_verified"):
        blockers.append("raw_capture_verified is false")
    if not raw.get("raw_sha256"):
        blockers.append("raw_sha256 missing")
    if raw.get("content_type") != "application/pdf":
        blockers.append("unexpected MIME type")
    if revision.get("status") in (None, "NOT_VERIFIED"):
        blockers.append("revision/vintage policy not verified")
    if not pit.get("provenance_test_passed"):
        blockers.append("PIT provenance test not passed")

    expected_hash = raw.get("raw_sha256")
    storage_path = raw.get("storage_path")
    observed_hash = None
    if storage_path:
        target = (base_dir / storage_path).resolve()
        if target.exists() and target.is_file():
            observed_hash = sha256_file(target)
            if expected_hash and observed_hash != expected_hash:
                blockers.append("raw_sha256 does not match stored artifact")
        else:
            blockers.append("declared storage_path does not exist")

    primary_verified = not blockers
    return {
        "source_id": manifest.get("source_id"),
        "status": "PRIMARY_VERIFIED" if primary_verified else "PROVISIONAL",
        "primary_verified": primary_verified,
        "blockers": blockers,
        "expected_sha256": expected_hash,
        "observed_sha256": observed_hash,
        "methodology": manifest.get("methodology", {}),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()

    manifest_path = args.manifest.resolve()
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = yaml.safe_load(handle) or {}

    result = validate_manifest(manifest, Path.cwd())

    print(yaml.safe_dump(result, allow_unicode=True, sort_keys=False).rstrip())
    return 0 if result["primary_verified"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
