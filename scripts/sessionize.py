"""
sessionize.py — Convert Raw Input into Session Records

Usage:
    # LLM-assisted mode (requires API key in environment)
    python scripts/sessionize.py --raw-id RAW-20260312-001

    # Manual/seed mode: write a session YAML directly
    python scripts/sessionize.py --seed path/to/session.yaml

    # Batch seed from a YAML list file
    python scripts/sessionize.py --seed-list path/to/sessions_list.yaml
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils import (
    DATA,
    load_all,
    parse_frontmatter,
    raw_dir,
    sessions_dir,
    write_json,
    write_markdown,
)

import yaml


REQUIRED_FIELDS = [
    "session_id", "title", "project", "domain", "phase", "outcome_type",
    "resolution_status", "raw_source_ids", "summary", "context",
    "surface_problem", "actual_problem", "trigger", "human_state",
    "questioning_pattern", "agent_failure_mode", "constraints",
    "observability_notes", "action_taken", "what_changed", "result",
    "why_it_mattered", "candidate_principles", "candidate_patterns", "confidence",
]

VALID_PHASES = {
    "ideation", "planning", "implementation", "debugging",
    "evaluation", "launch", "reflection", "meta-collaboration",
}

VALID_OUTCOME_TYPES = {"failure", "success", "mixed", "reframing", "discovery"}

VALID_RESOLUTION_STATUSES = {
    "unresolved", "partial", "resolved", "resolved_accidentally", "ongoing",
}


def validate_session(data: dict) -> list[str]:
    """Return list of validation errors (empty = ok)."""
    errors = []
    for f in ("session_id", "surface_problem", "actual_problem", "raw_source_ids"):
        if not data.get(f):
            errors.append(f"Missing mandatory field: {f}")
    if data.get("phase") and data["phase"] not in VALID_PHASES:
        errors.append(f"Invalid phase: {data['phase']}")
    if data.get("outcome_type") and data["outcome_type"] not in VALID_OUTCOME_TYPES:
        errors.append(f"Invalid outcome_type: {data['outcome_type']}")
    if data.get("resolution_status") and data["resolution_status"] not in VALID_RESOLUTION_STATUSES:
        errors.append(f"Invalid resolution_status: {data['resolution_status']}")
    return errors


def save_session(data: dict) -> Path:
    """Write a single session to data/sessions/{session_id}.md"""
    sessions_dir().mkdir(parents=True, exist_ok=True)
    sid = data["session_id"]
    md_path = sessions_dir() / f"{sid}.md"

    body = f"# {data.get('title', sid)}\n\n## Summary\n{data.get('summary', '')}"
    write_markdown(md_path, data, body)

    # Companion JSON
    json_path = sessions_dir() / f"{sid}.json"
    write_json(json_path, data)

    return md_path


def seed_session(record: dict) -> None:
    errors = validate_session(record)
    if errors:
        print(f"  [WARN] {record.get('session_id', '?')}: {errors}")
    path = save_session(record)
    print(f"[sessionize] Saved: {path}")


def seed_from_yaml(yaml_path: Path) -> None:
    """Load a single session YAML file or inline dict and save."""
    raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        for item in raw:
            seed_session(item)
    else:
        seed_session(raw)


def seed_from_list(yaml_path: Path) -> None:
    """Load a YAML file containing a list of sessions."""
    records = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    for record in records:
        seed_session(record)


def show_raw(raw_id: str) -> None:
    """Find and print a Raw Input record for manual review."""
    for year_dir in (DATA / "raw").glob("*/*/*/*"):
        pass
    # Search all raw markdown files
    for f in (DATA / "raw").rglob(f"{raw_id}.md"):
        fm = parse_frontmatter(f)
        print(f"\n=== Raw Input: {raw_id} ===")
        print(f"source: {fm.get('source')}")
        print(f"language: {fm.get('language')}")
        print(f"project_guess: {fm.get('project_guess')}")
        print("\nraw_text:")
        print(fm.get("raw_text", ""))
        return
    print(f"[sessionize] Raw Input not found: {raw_id}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sessionize Raw Input into Session Records")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--raw-id", help="Raw Input ID to load and display for manual sessionization")
    group.add_argument("--seed", help="Path to a single session YAML file to save directly")
    group.add_argument("--seed-list", help="Path to YAML file with list of sessions to seed")

    args = parser.parse_args()

    if args.raw_id:
        show_raw(args.raw_id)
        print("\n[sessionize] Review the raw text above and create session YAML manually,")
        print("             then run: python scripts/sessionize.py --seed path/to/session.yaml")

    elif args.seed:
        seed_from_yaml(Path(args.seed))

    elif args.seed_list:
        seed_from_list(Path(args.seed_list))


if __name__ == "__main__":
    main()
