from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

BUY_ALLOWED = False
REQUIRED_COLUMNS = {
    "decision_timestamp",
    "available_at",
    "permission_status",
    "market_gate",
    "confirmed_regime",
    "buy_allowed",
}
VALID_STATUS = {"PASS", "BLOCKED", "DATA_NOT_READY"}
VALID_GATES = {"GREEN", "YELLOW", "RED", "DATA_NOT_READY"}
VALID_REGIMES = {"R1", "R2", "R3", "R4", "R5", "R6", "DATA_NOT_READY"}


class PermissionDataNotReady(ValueError):
    pass


@dataclass(frozen=True)
class PermissionOverlayResult:
    status: str
    rows: int
    matched_rows: int
    eligible_rows: int
    regime_coverage: float
    buy_allowed: bool
    blocker_codes: tuple[str, ...]


def _utc(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, utc=True, errors="coerce")


def validate_permission_history(frame: pd.DataFrame) -> PermissionOverlayResult:
    missing = sorted(REQUIRED_COLUMNS - set(frame.columns))
    if missing:
        raise PermissionDataNotReady("missing_columns:" + ",".join(missing))

    df = frame.copy()
    for col in ("decision_timestamp", "available_at"):
        df[col] = _utc(df[col])
        if df[col].isna().any():
            raise PermissionDataNotReady("invalid_timestamp:" + col)

    if df.duplicated(["decision_timestamp"]).any():
        raise PermissionDataNotReady("duplicate_decision_timestamp")

    if (df["available_at"] < df["decision_timestamp"]).any():
        raise PermissionDataNotReady("available_before_decision")

    if (df["available_at"] > pd.Timestamp.now(tz="UTC")).any():
        raise PermissionDataNotReady("future_available_at")

    if not df["permission_status"].isin(VALID_STATUS).all():
        raise PermissionDataNotReady("invalid_permission_status")
    if not df["market_gate"].isin(VALID_GATES).all():
        raise PermissionDataNotReady("invalid_market_gate")
    if not df["confirmed_regime"].isin(VALID_REGIMES).all():
        raise PermissionDataNotReady("invalid_confirmed_regime")

    if df["buy_allowed"].astype(bool).any():
        raise PermissionDataNotReady("buy_allowed_must_remain_false")

    matched = int(df["confirmed_regime"].notna().sum())
    eligible = int(
        (
            (df["permission_status"] == "PASS")
            & df["confirmed_regime"].isin({"R1", "R2", "R3", "R4", "R5"})
            & (df["market_gate"] != "RED")
        ).sum()
    )
    coverage = float(matched / len(df)) if len(df) else 0.0
    blockers = sorted(
        {
            str(code)
            for codes in df.get("blocker_codes", pd.Series(dtype=object)).dropna()
            for code in str(codes).split("|")
            if code
        }
    )
    return PermissionOverlayResult(
        status="PASS",
        rows=int(len(df)),
        matched_rows=matched,
        eligible_rows=eligible,
        regime_coverage=coverage,
        buy_allowed=BUY_ALLOWED,
        blocker_codes=tuple(blockers),
    )


def attach_permission_overlay(
    signals: pd.DataFrame,
    permission_history: pd.DataFrame | None,
) -> tuple[pd.DataFrame, PermissionOverlayResult]:
    out = signals.copy()
    if permission_history is None:
        out["permission_status"] = "DATA_NOT_READY"
        out["permission_market_gate"] = "DATA_NOT_READY"
        out["confirmed_regime"] = "DATA_NOT_READY"
        out["permission_available_at"] = pd.NaT
        out["permission_match"] = False
        return out, PermissionOverlayResult(
            status="DATA_NOT_READY",
            rows=0,
            matched_rows=0,
            eligible_rows=0,
            regime_coverage=0.0,
            buy_allowed=BUY_ALLOWED,
            blocker_codes=("PERMISSION_HISTORY_MISSING",),
        )

    checked = validate_permission_history(permission_history)
    p = permission_history.copy()
    p["decision_timestamp"] = _utc(p["decision_timestamp"])
    p["available_at"] = _utc(p["available_at"])
    p = p.sort_values("available_at").reset_index(drop=True)

    s = out.sort_values("timestamp").copy()
    s["timestamp"] = _utc(s["timestamp"])
    merged = pd.merge_asof(
        s,
        p[
            [
                "decision_timestamp",
                "available_at",
                "permission_status",
                "market_gate",
                "confirmed_regime",
            ]
        ].rename(columns={"available_at": "permission_available_at"}),
        left_on="timestamp",
        right_on="permission_available_at",
        direction="backward",
        allow_exact_matches=True,
    )
    merged["permission_match"] = merged["permission_status"].notna()
    merged["permission_status"] = merged["permission_status"].fillna("DATA_NOT_READY")
    merged["permission_market_gate"] = merged["market_gate"].fillna("DATA_NOT_READY")
    merged["confirmed_regime"] = merged["confirmed_regime"].fillna("DATA_NOT_READY")
    merged = merged.sort_index()

    matched = int(merged["permission_match"].sum())
    eligible = int(
        (
            merged["permission_match"]
            & (merged["permission_status"] == "PASS")
            & merged["confirmed_regime"].isin({"R1", "R2", "R3", "R4", "R5"})
            & (merged["permission_market_gate"] != "RED")
        ).sum()
    )
    coverage = float(matched / len(merged)) if len(merged) else 0.0
    result = PermissionOverlayResult(
        status=checked.status,
        rows=checked.rows,
        matched_rows=matched,
        eligible_rows=eligible,
        regime_coverage=coverage,
        buy_allowed=BUY_ALLOWED,
        blocker_codes=checked.blocker_codes,
    )
    return merged, result
