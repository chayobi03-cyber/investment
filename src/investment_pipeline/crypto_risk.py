from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, Mapping

DEFAULT_WEIGHTS: dict[str, float] = {
    "trend": 0.20,
    "flow_institutional": 0.20,
    "macro_liquidity": 0.20,
    "breadth_relative_strength": 0.15,
    "derivatives": 0.10,
    "volatility_risk": 0.10,
    "regulation_market_structure": 0.05,
}

REGIMES: tuple[tuple[str, float, float], ...] = (
    ("R1", 75.0, 100.0),
    ("R2", 60.0, 75.0),
    ("R3", 50.0, 60.0),
    ("R4", 40.0, 50.0),
    ("R5", 25.0, 40.0),
    ("R6", 0.0, 25.0),
)

BUY_ALLOWED = False

EXPOSURE_MULTIPLIER: dict[str, float] = {
    "B0": 0.0,
    "B1": 0.0,
    "B2": 0.20,
    "B3": 0.60,
    "B4": 1.00,
}


class DataNotReady(ValueError):
    pass


@dataclass(frozen=True)
class CryptoDecision:
    market_score: float | None
    market_gate: str
    raw_regime: str | None
    confirmed_regime: str | None
    buy_state: str
    exposure_multiplier: float
    reason_codes: tuple[str, ...]
    permission_status: str
    buy_allowed: bool


@dataclass(frozen=True)
class CryptoObservation:
    axis_scores: Mapping[str, float]
    opportunity_score: float | None
    data_ready: bool
    price_in_interest_zone: bool = False
    extreme_dislocation: bool = False
    trend_stabilizing: bool = False
    persistence_ok: bool = False
    leadership_state: str = "neutral"
    fundamental_intact: bool = False
    macro_shock_active: bool = False
    derivatives_hard_block: bool = False
    severe_systemic_stress: bool = False
    worsening_shock_clusters: FrozenSet[str] = frozenset()
    stabilization_clusters: FrozenSet[str] = frozenset()
    asymmetric_payoff_ok: bool = False
    geopolitical_transmission_worsening: bool = False
    asset_structural_break: bool = False


def _validate_score(value: float) -> float:
    value = float(value)
    if not 0.0 <= value <= 100.0:
        raise DataNotReady(f"score_out_of_range:{value}")
    return value


def compute_market_score(
    axis_scores: Mapping[str, float],
    weights: Mapping[str, float] | None = None,
) -> float:
    w = dict(weights or DEFAULT_WEIGHTS)
    if set(w) != set(DEFAULT_WEIGHTS):
        raise DataNotReady("invalid_axis_set")
    if abs(sum(w.values()) - 1.0) > 1e-9:
        raise DataNotReady("weights_must_sum_to_1")
    missing = sorted(set(w) - set(axis_scores))
    if missing:
        raise DataNotReady("missing_axes:" + ",".join(missing))
    return round(sum(_validate_score(axis_scores[k]) * w[k] for k in w), 4)


def market_gate_from_score(score: float) -> str:
    score = _validate_score(score)
    if score >= 70.0:
        return "GREEN"
    if score >= 55.0:
        return "YELLOW"
    return "RED"


def regime_from_score(score: float) -> str:
    score = _validate_score(score)
    for regime, low, high in REGIMES:
        if low <= score < high or (regime == "R1" and score == high):
            return regime
    raise DataNotReady("regime_unresolved")


def confirm_regime(
    raw_regime: str,
    *,
    severe_systemic_stress: bool,
    worsening_shock_clusters: FrozenSet[str],
) -> str:
    if severe_systemic_stress or len(worsening_shock_clusters) >= 2:
        return "R6"
    return raw_regime


def derive_buy_state(
    obs: CryptoObservation,
    *,
    market_gate: str,
) -> tuple[str, tuple[str, ...]]:
    reasons: list[str] = []

    if not obs.data_ready:
        return "B0", ("DATA_NOT_READY",)

    if obs.severe_systemic_stress:
        reasons.append("SEVERE_SYSTEMIC_STRESS")
    if len(obs.worsening_shock_clusters) >= 2:
        reasons.append("MULTI_SHOCK")
    if obs.asset_structural_break:
        reasons.append("ASSET_STRUCTURAL_BREAK")
    if obs.macro_shock_active:
        reasons.append("MACRO_HARD_BLOCK")
    if obs.derivatives_hard_block:
        reasons.append("DERIVATIVES_HARD_BLOCK")
    if reasons:
        return "B0", tuple(reasons)

    if market_gate == "RED":
        return "B0", ("MARKET_GATE_RED",)

    if not obs.price_in_interest_zone:
        return "B0", ("PRICE_ZONE_NOT_REACHED",)

    if not obs.trend_stabilizing or len(obs.stabilization_clusters) < 1:
        return "B1", ("CONFIRMATION_INSUFFICIENT",)

    if market_gate == "YELLOW":
        return "B2", ("MARKET_GATE_YELLOW_CAP",)

    if not (
        obs.persistence_ok
        and obs.leadership_state != "deteriorating"
        and obs.fundamental_intact
    ):
        return "B2", ("SCOUT_ONLY",)

    b4_ok = (
        obs.extreme_dislocation
        and obs.asymmetric_payoff_ok
        and len(obs.stabilization_clusters) >= 2
        and not obs.geopolitical_transmission_worsening
    )
    if b4_ok:
        return "B4", ("EXTREME_DISLOCATION", "MULTI_CLUSTER_CONFIRMATION")

    return "B3", ("PERSISTENT_STABILIZATION", "FUNDAMENTAL_STATE_INTACT")


def evaluate(obs: CryptoObservation) -> CryptoDecision:
    if not obs.data_ready:
        return CryptoDecision(
            market_score=None,
            market_gate="DATA_NOT_READY",
            raw_regime=None,
            confirmed_regime=None,
            buy_state="B0",
            exposure_multiplier=0.0,
            reason_codes=("DATA_NOT_READY",),
            permission_status="BLOCKED",
            buy_allowed=BUY_ALLOWED,
        )

    try:
        market_score = compute_market_score(obs.axis_scores)
    except DataNotReady as exc:
        return CryptoDecision(
            market_score=None,
            market_gate="DATA_NOT_READY",
            raw_regime=None,
            confirmed_regime=None,
            buy_state="B0",
            exposure_multiplier=0.0,
            reason_codes=(str(exc),),
            permission_status="BLOCKED",
            buy_allowed=BUY_ALLOWED,
        )

    raw_regime = regime_from_score(market_score)
    confirmed_regime = confirm_regime(
        raw_regime,
        severe_systemic_stress=obs.severe_systemic_stress,
        worsening_shock_clusters=obs.worsening_shock_clusters,
    )
    gate = "RED" if confirmed_regime == "R6" else market_gate_from_score(market_score)
    buy_state, state_reasons = derive_buy_state(obs, market_gate=gate)
    permission = "BLOCKED" if buy_state == "B0" else "RESEARCH_ONLY"

    return CryptoDecision(
        market_score=market_score,
        market_gate=gate,
        raw_regime=raw_regime,
        confirmed_regime=confirmed_regime,
        buy_state=buy_state,
        exposure_multiplier=EXPOSURE_MULTIPLIER[buy_state],
        reason_codes=state_reasons,
        permission_status=permission,
        buy_allowed=BUY_ALLOWED,
    )
