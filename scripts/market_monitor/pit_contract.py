"""Point-in-time provenance contract for historical research artifacts.

The contract distinguishes an executable vendor-history proxy from a
promotion-grade archival PIT dataset. It does not manufacture PIT status from
timestamps alone.
"""
from __future__ import annotations

from typing import Any

PROXY = "VENDOR_HISTORY_PROXY"
STRICT = "STRICT_PIT_ARCHIVAL"
ALLOWED_VINTAGE_POLICIES = {"AS_PUBLISHED", "ACTION_AWARE"}


def validate_pit_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []

    pit_status = manifest.get("pit_status")
    if pit_status == STRICT:
        if not bool(manifest.get("pit_archival_revisions")):
            blockers.append("pit_archival_revisions must be true")
        policy = manifest.get("price_vintage_policy")
        if policy not in ALLOWED_VINTAGE_POLICIES:
            blockers.append("price_vintage_policy must be AS_PUBLISHED or ACTION_AWARE")
        if policy == "ACTION_AWARE" and manifest.get("corporate_action_ledger_status") != "ARCHIVAL_GREEN":
            blockers.append("ACTION_AWARE requires corporate_action_ledger_status=ARCHIVAL_GREEN")
        if not manifest.get("source_version"):
            blockers.append("source_version is required")
        if not manifest.get("artifact_sha256"):
            blockers.append("artifact_sha256 is required")
    elif pit_status == PROXY:
        blockers.append("vendor history is not archival PIT")
    else:
        blockers.append("unknown or missing pit_status")

    return {
        "status": "GREEN" if not blockers else "NOT_GREEN",
        "pit_status": pit_status,
        "strict_pit": pit_status == STRICT and not blockers,
        "blockers": blockers,
    }
