import unittest

from src.investment_pipeline.crypto_risk import (
    CryptoObservation,
    compute_market_score,
    confirm_regime,
    evaluate,
    market_gate_from_score,
    regime_from_score,
)

BASE = {
    "trend": 80,
    "flow_institutional": 70,
    "macro_liquidity": 70,
    "breadth_relative_strength": 65,
    "derivatives": 55,
    "volatility_risk": 60,
    "regulation_market_structure": 70,
}


class CryptoRiskEngineTests(unittest.TestCase):
    def test_weighted_market_score_v02(self):
        score = compute_market_score(BASE)
        self.assertAlmostEqual(score, 68.75)

    def test_gate_boundaries(self):
        self.assertEqual(market_gate_from_score(70), "GREEN")
        self.assertEqual(market_gate_from_score(55), "YELLOW")
        self.assertEqual(market_gate_from_score(54.999), "RED")

    def test_missing_axis_is_fail_closed(self):
        data = dict(BASE)
        del data["flow_institutional"]
        result = evaluate(
            CryptoObservation(axis_scores=data, opportunity_score=70, data_ready=True)
        )
        self.assertEqual(result.buy_state, "B0")
        self.assertEqual(result.permission_status, "BLOCKED")
        self.assertFalse(result.buy_allowed)
        self.assertTrue(result.reason_codes[0].startswith("missing_axes"))

    def test_regime_boundaries(self):
        self.assertEqual(regime_from_score(75), "R1")
        self.assertEqual(regime_from_score(60), "R2")
        self.assertEqual(regime_from_score(50), "R3")
        self.assertEqual(regime_from_score(40), "R4")
        self.assertEqual(regime_from_score(25), "R5")
        self.assertEqual(regime_from_score(0), "R6")

    def test_multi_shock_forces_r6(self):
        self.assertEqual(
            confirm_regime(
                "R2",
                severe_systemic_stress=False,
                worsening_shock_clusters=frozenset({"rates", "fx"}),
            ),
            "R6",
        )

    def test_yellow_gate_caps_active_buy(self):
        yellow_axes = {**BASE, "trend": 90, "flow_institutional": 90, "macro_liquidity": 30}
        result = evaluate(
            CryptoObservation(
                axis_scores=yellow_axes,
                opportunity_score=85,
                data_ready=True,
                price_in_interest_zone=True,
                trend_stabilizing=True,
                stabilization_clusters=frozenset({"rates"}),
                persistence_ok=True,
                leadership_state="improving",
                fundamental_intact=True,
            )
        )
        self.assertEqual(result.buy_state, "B2")
        self.assertEqual(result.market_gate, "YELLOW")

    def test_b3_requires_green_market_gate_and_persistence(self):
        axes = {k: 90 for k in BASE}
        result = evaluate(
            CryptoObservation(
                axis_scores=axes,
                opportunity_score=75,
                data_ready=True,
                price_in_interest_zone=True,
                trend_stabilizing=True,
                stabilization_clusters=frozenset({"rates"}),
                persistence_ok=True,
                leadership_state="improving",
                fundamental_intact=True,
            )
        )
        self.assertEqual(result.buy_state, "B3")
        self.assertEqual(result.market_gate, "GREEN")
        self.assertEqual(result.exposure_multiplier, 0.60)

    def test_b4_requires_two_confirmations_and_extreme_dislocation(self):
        axes = {k: 90 for k in BASE}
        result = evaluate(
            CryptoObservation(
                axis_scores=axes,
                opportunity_score=85,
                data_ready=True,
                price_in_interest_zone=True,
                extreme_dislocation=True,
                trend_stabilizing=True,
                persistence_ok=True,
                leadership_state="improving",
                fundamental_intact=True,
                stabilization_clusters=frozenset({"rates", "credit"}),
                asymmetric_payoff_ok=True,
            )
        )
        self.assertEqual(result.buy_state, "B4")
        self.assertEqual(result.exposure_multiplier, 1.0)

    def test_hard_macro_or_derivatives_block(self):
        axes = {k: 90 for k in BASE}
        result = evaluate(
            CryptoObservation(
                axis_scores=axes,
                opportunity_score=85,
                data_ready=True,
                price_in_interest_zone=True,
                trend_stabilizing=True,
                stabilization_clusters=frozenset({"rates", "credit"}),
                persistence_ok=True,
                leadership_state="improving",
                fundamental_intact=True,
                derivatives_hard_block=True,
            )
        )
        self.assertEqual(result.buy_state, "B0")
        self.assertIn("DERIVATIVES_HARD_BLOCK", result.reason_codes)


if __name__ == "__main__":
    unittest.main()
