import unittest

from src.investment_pipeline.crypto_risk import (
    CryptoObservation,
    compute_market_score,
    confirm_regime,
    evaluate,
    regime_from_score,
)


BASE = {
    "trend": 80,
    "flow": 70,
    "volatility_risk": 60,
    "derivatives": 55,
    "macro": 50,
    "breadth": 65,
}


class CryptoRiskEngineTests(unittest.TestCase):
    def test_weighted_market_score(self):
        score = compute_market_score(BASE)
        self.assertAlmostEqual(score, 65.25)

    def test_missing_axis_is_fail_closed(self):
        data = dict(BASE)
        del data["flow"]
        result = evaluate(
            CryptoObservation(
                axis_scores=data,
                opportunity_score=70,
                data_ready=True,
            )
        )
        self.assertEqual(result.buy_state, "B0")
        self.assertEqual(result.permission_status, "BLOCKED")
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

    def test_b1_watch_without_stabilization(self):
        result = evaluate(
            CryptoObservation(
                axis_scores=BASE,
                opportunity_score=70,
                data_ready=True,
                price_in_interest_zone=True,
                trend_stabilizing=False,
            )
        )
        self.assertEqual(result.buy_state, "B1")
        self.assertEqual(result.exposure_multiplier, 0.0)

    def test_b2_requires_one_stabilization_cluster(self):
        result = evaluate(
            CryptoObservation(
                axis_scores=BASE,
                opportunity_score=70,
                data_ready=True,
                price_in_interest_zone=True,
                trend_stabilizing=True,
                stabilization_clusters=frozenset({"rates"}),
            )
        )
        self.assertEqual(result.buy_state, "B2")
        self.assertEqual(result.exposure_multiplier, 0.20)

    def test_b3_requires_persistence_and_fundamentals(self):
        result = evaluate(
            CryptoObservation(
                axis_scores=BASE,
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
        self.assertEqual(result.exposure_multiplier, 0.60)

    def test_b4_requires_two_confirmations_and_extreme_dislocation(self):
        result = evaluate(
            CryptoObservation(
                axis_scores=BASE,
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

    def test_multi_shock_blocks_buy(self):
        result = evaluate(
            CryptoObservation(
                axis_scores=BASE,
                opportunity_score=85,
                data_ready=True,
                price_in_interest_zone=True,
                trend_stabilizing=True,
                stabilization_clusters=frozenset({"rates", "credit"}),
                persistence_ok=True,
                leadership_state="improving",
                fundamental_intact=True,
                worsening_shock_clusters=frozenset({"rates", "fx"}),
            )
        )
        self.assertEqual(result.buy_state, "B0")
        self.assertEqual(result.confirmed_regime, "R6")


if __name__ == "__main__":
    unittest.main()
