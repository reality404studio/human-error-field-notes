"""
test_classify.py — Tests for seeded Pattern records and cross-entity reference integrity
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from utils import load_all, patterns_dir, principles_dir, sessions_dir

EXPECTED_PATTERN_COUNT = 18

VALID_TYPES = {"failure", "success", "mixed", "reframing", "leverage", "behavioral", "meta-collaboration"}
VALID_STABILITY = {"draft", "provisional", "stable"}


def test_pattern_count():
    patterns = load_all(patterns_dir())
    assert len(patterns) == EXPECTED_PATTERN_COUNT, (
        f"Expected {EXPECTED_PATTERN_COUNT} patterns, found {len(patterns)}"
    )
    print(f"[OK] {len(patterns)} pattern files found")


def test_mandatory_fields():
    patterns = load_all(patterns_dir())
    for p in patterns:
        pid = p.get("pattern_id", "?")
        assert p.get("name"), f"{pid}: missing name"
        assert p.get("definition"), f"{pid}: missing definition"
        assert p.get("representative_session_ids"), f"{pid}: missing representative_session_ids"
    print(f"[OK] All patterns have mandatory fields")


def test_valid_type_and_stability():
    patterns = load_all(patterns_dir())
    for p in patterns:
        pid = p.get("pattern_id", "?")
        assert p.get("type") in VALID_TYPES, f"{pid}: invalid type={p.get('type')}"
        assert p.get("stability") in VALID_STABILITY, f"{pid}: invalid stability={p.get('stability')}"
    print(f"[OK] All patterns have valid type and stability")


def test_cross_reference_integrity():
    """All session/principle IDs referenced by patterns must actually exist."""
    sessions = {s["session_id"] for s in load_all(sessions_dir())}
    principles = {p["principle_id"] for p in load_all(principles_dir())}
    patterns = load_all(patterns_dir())

    errors = []
    for pat in patterns:
        pid = pat.get("pattern_id", "?")
        for sid in (pat.get("representative_session_ids") or []):
            if sid not in sessions:
                errors.append(f"{pid}: unknown session ref {sid}")
        for prid in (pat.get("included_principle_ids") or []):
            if prid not in principles:
                errors.append(f"{pid}: unknown principle ref {prid}")

    assert not errors, "Reference integrity errors:\n" + "\n".join(errors)
    print(f"[OK] All cross-references in patterns are valid")


def test_query_retrieval():
    """Test that the query script returns results for the 4 spec queries."""
    import importlib, types
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    import query as q_mod

    test_cases = [
        ("왜 모델이 같은 해결책 루프만 반복하지?", "PR-101"),
        ("구조를 먼저 물어야 하는 상황은 언제지?", "PR-105"),
        ("인간용 계획을 모델에게 그대로 주면 왜 안 되지?", "PR-202"),
        ("대화가 다음 단계로 밀릴 때 원래 목적을 어떻게 유지하지?", "PR-301"),
    ]
    for query_str, expected_top_id in test_cases:
        results = q_mod.retrieve(query_str, top_k=3)
        assert results, f"No results for: {query_str}"
        top_id = results[0]["id"]
        assert top_id == expected_top_id, (
            f"Query '{query_str}': expected top={expected_top_id}, got {top_id}"
        )
        print(f"[OK] '{query_str[:30]}...' → {top_id}")


if __name__ == "__main__":
    test_pattern_count()
    test_mandatory_fields()
    test_valid_type_and_stability()
    test_cross_reference_integrity()
    test_query_retrieval()
    print("\nAll classify tests passed.")
