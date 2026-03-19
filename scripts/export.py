"""
export.py — Generate aggregate JSON exports from all entity files

Usage:
    python scripts/export.py

Outputs:
    data/exports/all_sessions.json
    data/exports/all_principles.json
    data/exports/all_patterns.json
    data/exports/graph.json
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils import (
    DATA,
    exports_dir,
    load_all,
    now_iso,
    patterns_dir,
    principles_dir,
    sessions_dir,
    write_json,
)


def build_graph(sessions: list[dict], principles: list[dict], patterns: list[dict]) -> dict:
    nodes = []
    edges = []

    # Raw nodes from session references
    raw_ids: set[str] = set()
    for s in sessions:
        for rid in (s.get("raw_source_ids") or []):
            raw_ids.add(rid)

    for rid in sorted(raw_ids):
        nodes.append({"id": rid, "type": "raw"})

    for s in sessions:
        nodes.append({"id": s["session_id"], "type": "session", "title": s.get("title", "")})
        for rid in (s.get("raw_source_ids") or []):
            edges.append({"from": s["session_id"], "to": rid, "rel": "source"})

    for p in principles:
        nodes.append({"id": p["principle_id"], "type": "principle", "title": p.get("title", "")})
        for sid in (p.get("source_session_ids") or []):
            edges.append({"from": p["principle_id"], "to": sid, "rel": "derived_from"})

    for pat in patterns:
        nodes.append({"id": pat["pattern_id"], "type": "pattern", "name": pat.get("name", "")})
        for pid in (pat.get("included_principle_ids") or []):
            edges.append({"from": pat["pattern_id"], "to": pid, "rel": "includes"})
        for sid in (pat.get("representative_session_ids") or []):
            edges.append({"from": pat["pattern_id"], "to": sid, "rel": "representative"})
        if pat.get("parent_pattern_id"):
            edges.append({"from": pat["pattern_id"], "to": pat["parent_pattern_id"], "rel": "child_of"})

    return {"nodes": nodes, "edges": edges}


def export_all() -> None:
    sessions = load_all(sessions_dir())
    principles = load_all(principles_dir())
    patterns = load_all(patterns_dir())

    exports = exports_dir()

    write_json(exports / "all_sessions.json", sessions)
    print(f"[export] all_sessions.json  → {len(sessions)} records")

    write_json(exports / "all_principles.json", principles)
    print(f"[export] all_principles.json → {len(principles)} records")

    write_json(exports / "all_patterns.json", patterns)
    print(f"[export] all_patterns.json  → {len(patterns)} records")

    graph = build_graph(sessions, principles, patterns)
    write_json(exports / "graph.json", graph)
    print(f"[export] graph.json          → {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")

    # Metadata summary
    meta = {
        "exported_at": now_iso(),
        "counts": {
            "sessions": len(sessions),
            "principles": len(principles),
            "patterns": len(patterns),
            "graph_nodes": len(graph["nodes"]),
            "graph_edges": len(graph["edges"]),
        }
    }
    write_json(exports / "meta.json", meta)
    print(f"[export] meta.json")
    print(f"\n[export] Done.")


def main() -> None:
    export_all()


if __name__ == "__main__":
    main()
