from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import pandas as pd


CANDIDATE_STATES = frozenset({"B2", "B3", "B4"})
SIGNAL_TYPES = frozenset({"BREAKOUT", "PULLBACK"})
REGIMES = frozenset({"R1", "R2", "R3", "R4", "R5", "R6"})


@dataclass(frozen=True)
class DecompositionSpec:
    """Immutable grouping contract for signal decomposition."""

    entry_states: frozenset[str] = CANDIDATE_STATES
    group_dimensions: tuple[str, ...] = (
        "confirmed_regime",
        "entry_state",
        "signal_type",
        "zone",
    )


class SignalDecompositionAgent:
    """Deterministic research agent; labels signals without changing thresholds."""

    name = "signal_decomposition"

    def __init__(self, spec: DecompositionSpec | None = None) -> None:
        self.spec = spec or DecompositionSpec()

    def apply(
        self,
        frame: pd.DataFrame,
        *,
        regime_preference: Sequence[str] = ("confirmed_regime", "raw_regime"),
    ) -> pd.DataFrame:
        required = {"entry_state", "breakout", "zone"}
        missing = sorted(required - set(frame.columns))
        if missing:
            raise ValueError("DECOMPOSITION_MISSING_COLUMNS:" + ",".join(missing))

        out = frame.copy()
        out["signal_type"] = out["breakout"].fillna(False).map(
            lambda value: "BREAKOUT" if bool(value) else "PULLBACK"
        )

        regime_column = next(
            (
                column
                for column in regime_preference
                if column in out.columns
                and out[column].astype(str).isin(REGIMES).any()
            ),
            None,
        )
        if regime_column is None:
            out["decomposition_regime"] = "DATA_NOT_READY"
        else:
            out["decomposition_regime"] = (
                out[regime_column]
                .astype(str)
                .where(out[regime_column].astype(str).isin(REGIMES), "DATA_NOT_READY")
            )

        out["decomposition_key"] = (
            out["decomposition_regime"].astype(str)
            + "|"
            + out["entry_state"].astype(str)
            + "|"
            + out["signal_type"].astype(str)
            + "|"
            + out["zone"].astype(str)
        )
        return out

    def summarize(
        self,
        frame: pd.DataFrame,
        *,
        group_dimensions: Iterable[str] | None = None,
    ) -> pd.DataFrame:
        dims = tuple(group_dimensions or self.spec.group_dimensions)
        missing = sorted(set(dims) - set(frame.columns))
        if missing:
            raise ValueError("DECOMPOSITION_GROUP_COLUMNS:" + ",".join(missing))
        if frame.empty:
            return pd.DataFrame(columns=[*dims, "events"])

        grouped = (
            frame.groupby(list(dims), dropna=False, sort=True)
            .size()
            .reset_index(name="events")
        )
        return grouped

    def candidate_only(self, frame: pd.DataFrame) -> pd.DataFrame:
        if "entry_state" not in frame.columns:
            raise ValueError("DECOMPOSITION_MISSING_COLUMNS:entry_state")
        return frame[frame["entry_state"].isin(self.spec.entry_states)].copy()
