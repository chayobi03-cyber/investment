import unittest

import pandas as pd

from src.investment_pipeline.crypto_permission import (
    BUY_ALLOWED,
    PermissionDataNotReady,
    attach_permission_overlay,
    validate_permission_history,
)


def make_history() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "decision_timestamp": pd.to_datetime(
                ["2026-09-20T00:00:00Z", "2026-09-21T00:00:00Z"]
            ),
            "available_at": pd.to_datetime(
                ["2026-09-20T01:00:00Z", "2026-09-21T01:00:00Z"]
            ),
            "permission_status": ["PASS", "PASS"],
            "market_gate": ["GREEN", "YELLOW"],
            "confirmed_regime": ["R1", "R2"],
            "buy_allowed": [False, False],
            "blocker_codes": ["", ""],
        }
    )


class CryptoPermissionOverlayTests(unittest.TestCase):
    def test_buy_allowed_is_hard_locked_false(self):
        self.assertFalse(BUY_ALLOWED)
        result = validate_permission_history(make_history())
        self.assertFalse(result.buy_allowed)

    def test_available_at_is_the_pit_join_clock(self):
        signals = pd.DataFrame(
            {
                "timestamp": pd.to_datetime(
                    [
                        "2026-09-20T00:30:00Z",
                        "2026-09-20T01:00:00Z",
                        "2026-09-21T02:00:00Z",
                    ]
                ),
                "entry_state": ["B2", "B3", "B4"],
            }
        )
        merged, result = attach_permission_overlay(signals, make_history())
        self.assertEqual(merged.iloc[0]["permission_status"], "DATA_NOT_READY")
        self.assertEqual(merged.iloc[1]["confirmed_regime"], "R1")
        self.assertEqual(merged.iloc[2]["confirmed_regime"], "R2")
        self.assertEqual(result.matched_rows, 2)

    def test_missing_history_fails_closed(self):
        signals = pd.DataFrame(
            {
                "timestamp": pd.to_datetime(
                    ["2026-09-20T00:00:00Z"]
                ),
            }
        )
        merged, result = attach_permission_overlay(signals, None)
        self.assertEqual(result.status, "DATA_NOT_READY")
        self.assertFalse(merged.iloc[0]["permission_match"])
        self.assertEqual(merged.iloc[0]["permission_status"], "DATA_NOT_READY")

    def test_true_buy_allowed_is_rejected(self):
        bad = make_history()
        bad.loc[0, "buy_allowed"] = True
        with self.assertRaises(PermissionDataNotReady):
            validate_permission_history(bad)

    def test_available_before_decision_is_rejected(self):
        bad = make_history()
        bad.loc[0, "available_at"] = pd.Timestamp("2026-09-19T23:00:00Z")
        with self.assertRaises(PermissionDataNotReady):
            validate_permission_history(bad)

    def test_future_available_at_is_checked_only_against_explicit_as_of(self):
        bad = make_history()
        bad.loc[0, "available_at"] = pd.Timestamp("2026-09-27T01:00:00Z")
        # Historical validators must not depend on the machine's current wall clock.
        result = validate_permission_history(
            bad, as_of=pd.Timestamp("2026-09-27T00:00:00Z")
        )
        self.assertEqual(result.status, "PASS")

        with self.assertRaises(PermissionDataNotReady):
            validate_permission_history(
                bad, as_of=pd.Timestamp("2026-09-26T00:00:00Z")
            )


if __name__ == "__main__":
    unittest.main()
