import unittest

import pandas as pd

from scripts.crypto.validate_permission_layer_pit import validate


def make_frame() -> pd.DataFrame:
    return pd.DataFrame({
        "asset":["BTC","ETH"],
        "series_id":["A","B"],
        "observation_timestamp":["2026-09-20T00:00:00Z","2026-09-20T00:00:00Z"],
        "available_at":["2026-09-20T01:00:00Z","2026-09-20T01:00:00Z"],
        "source_id":["SRC1","SRC1"],
        "unit":["USD","USD"],
        "value":[100.0,200.0],
        "ingested_at":["2026-09-20T02:00:00Z","2026-09-20T02:00:00Z"]
    })


class PermissionLayerTests(unittest.TestCase):
    def test_valid_pit_observations(self):
        result = validate(make_frame())
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["rows"], 2)

    def test_future_availability_is_rejected_against_explicit_cutoff(self):
        frame = make_frame()
        frame.loc[0, "available_at"] = "2026-09-27T00:00:00Z"
        with self.assertRaises(SystemExit):
            validate(frame, as_of=pd.Timestamp("2026-09-26T00:00:00Z"))

    def test_future_availability_is_not_rejected_by_wall_clock(self):
        frame = make_frame()
        frame.loc[0, "available_at"] = "2099-01-01T00:00:00Z"
        result = validate(frame)
        self.assertEqual(result["status"], "PASS")

    def test_availability_before_observation_is_rejected(self):
        frame = make_frame()
        frame.loc[0,"available_at"] = "2026-09-19T23:00:00Z"
        with self.assertRaises(SystemExit):
            validate(frame)


if __name__ == "__main__":
    unittest.main()
