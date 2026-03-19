"""
test_sessionize.py — Tests for seeded Session records
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from utils import load_all, sessions_dir

EXPECTED_SESSION_IDS = {
    "Q3-CAM-001",
    "Q3-PT-001", "Q3-PT-002", "Q3-PT-003", "Q3-PT-004", "Q3-PT-005",
    "Q3-SM-001", "Q3-SM-002", "Q3-SM-003", "Q3-SM-004",
    "META-CHAT-001",
}

EXPECTED_COUNT = 11


def test_session_count():
    sessions = load_all(sessions_dir())
    assert len(sessions) == EXPECTED_COUNT, (
        f"Expected {EXPECTED_COUNT} sessions, found {len(sessions)}"
    )
    print(f"[OK] {len(sessions)} session files found")


def test_session_ids_present():
    sessions = load_all(sessions_dir())
    found_ids = {s["session_id"] for s in sessions}
    missing = EXPECTED_SESSION_IDS - found_ids
    assert not missing, f"Missing session IDs: {missing}"
    print(f"[OK] All expected session IDs present")


def test_mandatory_fields():
    sessions = load_all(sessions_dir())
    for s in sessions:
        sid = s.get("session_id", "?")
        assert s.get("surface_problem"), f"{sid}: missing surface_problem"
        assert s.get("actual_problem"), f"{sid}: missing actual_problem"
        assert s.get("raw_source_ids"), f"{sid}: missing raw_source_ids"
    print(f"[OK] All sessions have mandatory fields (surface_problem, actual_problem, raw_source_ids)")


def test_raw_source_ids_format():
    sessions = load_all(sessions_dir())
    for s in sessions:
        for rid in s.get("raw_source_ids", []):
            assert rid.startswith("RAW-"), f"Invalid raw_source_id: {rid} in {s['session_id']}"
    print(f"[OK] All raw_source_ids have correct format")


if __name__ == "__main__":
    test_session_count()
    test_session_ids_present()
    test_mandatory_fields()
    test_raw_source_ids_format()
    print("\nAll sessionize tests passed.")
