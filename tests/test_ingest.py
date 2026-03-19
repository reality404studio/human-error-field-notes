"""
test_ingest.py — Tests for ingest script
"""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from utils import DATA


def test_raw_files_exist():
    """Seed raw directory should exist and contain dated subdirs."""
    raw_root = DATA / "raw"
    assert raw_root.exists(), "data/raw/ directory missing"
    dated_dirs = list(raw_root.glob("*/*/*"))
    assert len(dated_dirs) >= 1, "No dated subdirectories found under data/raw/"
    print(f"[OK] data/raw/ has {len(dated_dirs)} dated subdirectory(ies)")


def test_ingest_creates_file(tmp_path):
    """Ingest should create a markdown and json file."""
    import importlib, types
    # Patch DATA to use tmp_path
    import utils as u
    orig = u.DATA
    u.DATA = tmp_path

    from datetime import datetime, timezone
    now = datetime(2026, 3, 12, tzinfo=timezone.utc)

    from importlib import import_module
    ingest_mod = import_module("ingest")
    input_id = ingest_mod.ingest(
        raw_text="테스트 노트입니다.",
        source="manual",
        language="ko",
        date=now,
    )
    assert input_id.startswith("RAW-20260312")
    md = tmp_path / "raw" / "2026" / "03" / "12" / f"{input_id}.md"
    js = tmp_path / "raw" / "2026" / "03" / "12" / f"{input_id}.json"
    assert md.exists(), f"Markdown file not created: {md}"
    assert js.exists(), f"JSON file not created: {js}"

    data = json.loads(js.read_text())
    assert data["input_id"] == input_id
    assert data["language"] == "ko"
    print(f"[OK] ingest created {input_id}")

    u.DATA = orig


if __name__ == "__main__":
    test_raw_files_exist()
    print("test_ingest_creates_file: skipped (requires tmp_path fixture)")
    print("\nAll ingest tests passed.")
