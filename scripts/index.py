"""
index.py — Regenerate helper index files

Usage:
    python scripts/index.py

Outputs:
    data/indexes/sessions_by_project.json
    data/indexes/patterns_by_parent.json
    data/indexes/principles_by_query_form.json
    data/indexes/meta_collaboration_patterns.json
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils import (
    indexes_dir,
    load_all,
    patterns_dir,
    principles_dir,
    sessions_dir,
    write_json,
)


def build_sessions_by_project(sessions: list[dict]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = defaultdict(list)
    for s in sessions:
        project = s.get("project") or "unknown"
        index[project].append(s["session_id"])
    return dict(index)


def build_patterns_by_parent(patterns: list[dict]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = defaultdict(list)
    for p in patterns:
        parent = p.get("parent_pattern_id") or "__root__"
        index[parent].append(p["pattern_id"])
    return dict(index)


def build_principles_by_query_form(principles: list[dict]) -> dict[str, list[str]]:
    """Map each query_form phrase → list of principle_ids."""
    index: dict[str, list[str]] = defaultdict(list)
    for p in principles:
        for qf in (p.get("query_forms") or []):
            index[qf].append(p["principle_id"])
    return dict(index)


def build_meta_collaboration_patterns(patterns: list[dict]) -> list[dict]:
    return [
        {
            "pattern_id": p["pattern_id"],
            "name": p.get("name"),
            "definition": p.get("definition"),
            "agent_response": p.get("agent_response"),
        }
        for p in patterns
        if p.get("type") == "meta-collaboration"
    ]


def regenerate_indexes() -> None:
    sessions = load_all(sessions_dir())
    principles = load_all(principles_dir())
    patterns = load_all(patterns_dir())
    idx_dir = indexes_dir()

    sbp = build_sessions_by_project(sessions)
    write_json(idx_dir / "sessions_by_project.json", sbp)
    print(f"[index] sessions_by_project.json → {len(sbp)} projects")

    pbp = build_patterns_by_parent(patterns)
    write_json(idx_dir / "patterns_by_parent.json", pbp)
    print(f"[index] patterns_by_parent.json  → {len(pbp)} parents")

    pqf = build_principles_by_query_form(principles)
    write_json(idx_dir / "principles_by_query_form.json", pqf)
    print(f"[index] principles_by_query_form.json → {len(pqf)} query forms")

    mcp = build_meta_collaboration_patterns(patterns)
    write_json(idx_dir / "meta_collaboration_patterns.json", mcp)
    print(f"[index] meta_collaboration_patterns.json → {len(mcp)} patterns")

    print("\n[index] Done.")


def main() -> None:
    regenerate_indexes()


if __name__ == "__main__":
    main()
