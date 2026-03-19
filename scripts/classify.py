"""
classify.py — Match or create Pattern records from Sessions and Principles

Usage:
    # Seed a single pattern YAML
    python scripts/classify.py --seed path/to/pattern.yaml

    # Seed a YAML list of patterns
    python scripts/classify.py --seed-list path/to/patterns_list.yaml

    # Show existing patterns (for matching before creating new)
    python scripts/classify.py --list
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils import load_all, patterns_dir, write_json, write_markdown

import yaml


VALID_TYPES = {"failure", "success", "mixed", "reframing", "leverage", "behavioral", "meta-collaboration"}
VALID_STABILITY = {"draft", "provisional", "stable"}

REQUIRED_FIELDS = [
    "pattern_id", "name", "type", "definition",
    "representative_session_ids", "agent_response", "confidence", "stability",
]


def validate_pattern(data: dict) -> list[str]:
    errors = []
    for f in ("pattern_id", "name", "definition", "representative_session_ids"):
        if not data.get(f):
            errors.append(f"Missing mandatory field: {f}")
    if data.get("type") and data["type"] not in VALID_TYPES:
        errors.append(f"Invalid type: {data['type']}")
    if data.get("stability") and data["stability"] not in VALID_STABILITY:
        errors.append(f"Invalid stability: {data['stability']}")
    return errors


def find_matching_pattern(data: dict) -> dict | None:
    """Check if any existing pattern matches by trigger/signal overlap."""
    existing = load_all(patterns_dir())
    new_triggers = set(data.get("triggers") or [])
    new_signals = set(data.get("signals") or [])

    for pat in existing:
        existing_triggers = set(pat.get("triggers") or [])
        existing_signals = set(pat.get("signals") or [])
        trigger_overlap = new_triggers & existing_triggers
        signal_overlap = new_signals & existing_signals
        if trigger_overlap or signal_overlap:
            return pat
    return None


def save_pattern(data: dict) -> Path:
    patterns_dir().mkdir(parents=True, exist_ok=True)
    pid = data["pattern_id"]
    md_path = patterns_dir() / f"{pid}.md"

    body = (
        f"# {data.get('name', pid)} ({pid})\n\n"
        f"**Type:** {data.get('type', '')}\n\n"
        f"## Definition\n{data.get('definition', '')}\n\n"
        f"## Agent Response\n{data.get('agent_response', '')}"
    )
    write_markdown(md_path, data, body)

    json_path = patterns_dir() / f"{pid}.json"
    write_json(json_path, data)
    return md_path


def seed_pattern(record: dict) -> None:
    errors = validate_pattern(record)
    if errors:
        print(f"  [WARN] {record.get('pattern_id', '?')}: {errors}")

    # Check for match before saving
    match = find_matching_pattern(record)
    if match and match.get("pattern_id") != record.get("pattern_id"):
        print(f"  [INFO] Similar existing pattern found: {match.get('pattern_id')} — {match.get('name')}")

    path = save_pattern(record)
    print(f"[classify] Saved: {path}")


def seed_from_yaml(yaml_path: Path) -> None:
    raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        for item in raw:
            seed_pattern(item)
    else:
        seed_pattern(raw)


def seed_from_list(yaml_path: Path) -> None:
    records = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    for record in records:
        seed_pattern(record)


def list_patterns() -> None:
    patterns = load_all(patterns_dir())
    if not patterns:
        print("[classify] No patterns found.")
        return
    print(f"\n{'ID':<12} {'TYPE':<20} {'NAME'}")
    print("-" * 60)
    for p in patterns:
        print(f"{p.get('pattern_id',''):<12} {p.get('type',''):<20} {p.get('name','')}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify Patterns from Sessions and Principles")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--seed", help="Path to single pattern YAML")
    group.add_argument("--seed-list", help="Path to YAML file with list of patterns")
    group.add_argument("--list", action="store_true", help="List all existing patterns")

    args = parser.parse_args()

    if args.seed:
        seed_from_yaml(Path(args.seed))
    elif args.seed_list:
        seed_from_list(Path(args.seed_list))
    elif args.list:
        list_patterns()


if __name__ == "__main__":
    main()
