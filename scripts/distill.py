"""
distill.py — Extract Principle records from Session Records

Usage:
    # Seed a single principle YAML
    python scripts/distill.py --seed path/to/principle.yaml

    # Seed a YAML list of principles
    python scripts/distill.py --seed-list path/to/principles_list.yaml

    # Show sessions to help manual distillation
    python scripts/distill.py --from-session Q3-CAM-001
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils import parse_frontmatter, principles_dir, sessions_dir, write_json, write_markdown

import yaml


VALID_STATUSES = {"draft", "stable", "deprecated"}

REQUIRED_FIELDS = [
    "principle_id", "title", "statement", "description",
    "source_session_ids", "query_forms", "agent_implication",
    "confidence", "status",
]


def validate_principle(data: dict) -> list[str]:
    errors = []
    for f in ("principle_id", "statement", "source_session_ids", "query_forms"):
        if not data.get(f):
            errors.append(f"Missing mandatory field: {f}")
    if data.get("status") and data["status"] not in VALID_STATUSES:
        errors.append(f"Invalid status: {data['status']}")
    if data.get("confidence") is not None:
        c = data["confidence"]
        if not (0.0 <= float(c) <= 1.0):
            errors.append(f"confidence must be 0.0–1.0, got {c}")
    return errors


def save_principle(data: dict) -> Path:
    principles_dir().mkdir(parents=True, exist_ok=True)
    pid = data["principle_id"]
    md_path = principles_dir() / f"{pid}.md"

    body = (
        f"# {data.get('title', pid)}\n\n"
        f"## Statement\n{data.get('statement', '')}\n\n"
        f"## Description\n{data.get('description', '')}"
    )
    write_markdown(md_path, data, body)

    json_path = principles_dir() / f"{pid}.json"
    write_json(json_path, data)
    return md_path


def seed_principle(record: dict) -> None:
    errors = validate_principle(record)
    if errors:
        print(f"  [WARN] {record.get('principle_id', '?')}: {errors}")
    path = save_principle(record)
    print(f"[distill] Saved: {path}")


def seed_from_yaml(yaml_path: Path) -> None:
    raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        for item in raw:
            seed_principle(item)
    else:
        seed_principle(raw)


def seed_from_list(yaml_path: Path) -> None:
    records = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    for record in records:
        seed_principle(record)


def show_session(session_id: str) -> None:
    path = sessions_dir() / f"{session_id}.md"
    if not path.exists():
        print(f"[distill] Session not found: {session_id}", file=sys.stderr)
        return
    fm = parse_frontmatter(path)
    print(f"\n=== Session: {session_id} ===")
    for key in ("title", "outcome_type", "summary", "actual_problem",
                "why_it_mattered", "candidate_principles"):
        val = fm.get(key, "")
        print(f"{key}: {val}")
    print("\n[distill] Review above and create principle YAML manually.")
    print("          Then run: python scripts/distill.py --seed path/to/principle.yaml")


def main() -> None:
    parser = argparse.ArgumentParser(description="Distill Principles from Session Records")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--from-session", metavar="SESSION_ID",
                       help="Show session details to assist manual distillation")
    group.add_argument("--seed", help="Path to single principle YAML")
    group.add_argument("--seed-list", help="Path to YAML file with list of principles")

    args = parser.parse_args()

    if args.from_session:
        show_session(args.from_session)
    elif args.seed:
        seed_from_yaml(Path(args.seed))
    elif args.seed_list:
        seed_from_list(Path(args.seed_list))


if __name__ == "__main__":
    main()
