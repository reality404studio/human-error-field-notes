"""
test_distill.py — Tests for seeded Principle records
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from utils import load_all, principles_dir

EXPECTED_COUNT = 22


def test_principle_count():
    principles = load_all(principles_dir())
    assert len(principles) == EXPECTED_COUNT, (
        f"Expected {EXPECTED_COUNT} principles, found {len(principles)}"
    )
    print(f"[OK] {len(principles)} principle files found")


def test_mandatory_fields():
    principles = load_all(principles_dir())
    for p in principles:
        pid = p.get("principle_id", "?")
        assert p.get("statement"), f"{pid}: missing statement"
        assert p.get("source_session_ids"), f"{pid}: missing source_session_ids"
        assert p.get("query_forms"), f"{pid}: missing query_forms (required for agent retrieval)"
    print(f"[OK] All principles have mandatory fields")


def test_query_forms_are_lists():
    principles = load_all(principles_dir())
    for p in principles:
        pid = p.get("principle_id", "?")
        qf = p.get("query_forms")
        assert isinstance(qf, list) and len(qf) >= 1, (
            f"{pid}: query_forms must be a non-empty list"
        )
    print(f"[OK] All principles have query_forms as non-empty lists")


def test_valid_status():
    valid = {"draft", "stable", "deprecated"}
    principles = load_all(principles_dir())
    for p in principles:
        pid = p.get("principle_id", "?")
        assert p.get("status") in valid, f"{pid}: invalid status={p.get('status')}"
    print(f"[OK] All principles have valid status")


if __name__ == "__main__":
    test_principle_count()
    test_mandatory_fields()
    test_query_forms_are_lists()
    test_valid_status()
    print("\nAll distill tests passed.")
