from datetime import date


CAPTURE = {
    "status": "PROVISIONAL",
    "observation_end": date(2025, 7, 31),
    "publication_date": date(2025, 8, 18),
    "available_at": date(2025, 8, 18),
    "raw_sha256": "6d14bb93128997f635fd4c855c6d5432e7bb8a193f623f310892303ec0944160",
    "raw_capture_verified": True,
    "revision_verified": False,
    "pit_provenance_test_passed": False,
}


def test_observation_and_publication_are_separate():
    assert CAPTURE["observation_end"] < CAPTURE["publication_date"]


def test_pit_blocks_prepublication_decision():
    decision_timestamp = date(2025, 8, 17)
    assert not CAPTURE["available_at"] <= decision_timestamp


def test_pit_allows_date_level_postpublication_decision():
    decision_timestamp = date(2025, 8, 18)
    assert CAPTURE["available_at"] <= decision_timestamp


def test_raw_capture_and_hash_can_be_verified_without_primary_promotion():
    assert CAPTURE["raw_capture_verified"] is True
    assert len(CAPTURE["raw_sha256"]) == 64
    assert CAPTURE["revision_verified"] is False
    assert CAPTURE["status"] == "PROVISIONAL"


def test_unverified_revision_blocks_primary_promotion():
    assert CAPTURE["revision_verified"] is False
    assert CAPTURE["status"] == "PROVISIONAL"


def test_unexecuted_pit_provenance_blocks_primary_promotion():
    assert CAPTURE["pit_provenance_test_passed"] is False
    assert CAPTURE["status"] == "PROVISIONAL"
