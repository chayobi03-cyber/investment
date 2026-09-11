from datetime import date


CAPTURE = {
    "status": "PROVISIONAL",
    "observation_end": date(2025, 7, 31),
    "publication_date": date(2025, 8, 18),
    "available_at": date(2025, 8, 18),
    "raw_sha256": None,
    "raw_capture_verified": False,
    "revision_verified": False,
}


def test_observation_and_publication_are_separate():
    assert CAPTURE["observation_end"] < CAPTURE["publication_date"]


def test_pit_blocks_prepublication_decision():
    decision_timestamp = date(2025, 8, 17)
    assert not CAPTURE["available_at"] <= decision_timestamp


def test_pit_allows_postpublication_decision():
    decision_timestamp = date(2025, 8, 18)
    assert CAPTURE["available_at"] <= decision_timestamp


def test_missing_raw_hash_cannot_be_primary_verified():
    assert CAPTURE["raw_sha256"] is None
    assert CAPTURE["status"] == "PROVISIONAL"


def test_unverified_revision_cannot_be_primary_verified():
    assert CAPTURE["revision_verified"] is False
    assert CAPTURE["status"] == "PROVISIONAL"


def test_raw_capture_flag_matches_hash_state():
    assert CAPTURE["raw_capture_verified"] is False
    assert CAPTURE["raw_sha256"] is None
