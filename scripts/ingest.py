"""
ingest.py — Ingest free-form text as Raw Input

Usage:
    python scripts/ingest.py --source manual --text "..."
    python scripts/ingest.py --source file --file path/to/note.txt
    python scripts/ingest.py --source stdin
    python scripts/ingest.py --source manual --text "..." --project "MyProject" --lang ko
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

# Allow running from any cwd
sys.path.insert(0, str(Path(__file__).parent))

from utils import next_raw_id, now_iso, raw_dir, write_json, write_markdown


def detect_language(text: str) -> str:
    """Rough language detection: Korean characters → ko, else en."""
    korean_chars = sum(1 for c in text if "\uAC00" <= c <= "\uD7A3" or "\u3131" <= c <= "\u314E")
    return "ko" if korean_chars / max(len(text), 1) > 0.05 else "en"


def ingest(
    raw_text: str,
    source: str,
    language: str | None = None,
    project_guess: str | None = None,
    date: datetime | None = None,
) -> str:
    """Store raw_text as a Raw Input record. Returns the input_id."""
    now = date or datetime.now(tz=timezone.utc)
    directory = raw_dir(now)
    directory.mkdir(parents=True, exist_ok=True)

    input_id = next_raw_id(now)
    lang = language or detect_language(raw_text)

    frontmatter = {
        "input_id": input_id,
        "source": source,
        "language": lang,
        "project_guess": project_guess,
        "timestamp": now_iso(),
        "raw_text": raw_text,
    }

    # Write markdown
    md_path = directory / f"{input_id}.md"
    body = f"# {input_id}\n\n{raw_text}"
    write_markdown(md_path, frontmatter, body)

    # Write companion JSON
    json_path = directory / f"{input_id}.json"
    write_json(json_path, frontmatter)

    print(f"[ingest] Saved: {md_path}")
    return input_id


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingest free-form text as Raw Input into agent-wiki-mvp"
    )
    parser.add_argument(
        "--source",
        required=True,
        choices=["manual", "file", "stdin"],
        help="Input source type",
    )
    parser.add_argument("--text", help="Raw text to ingest (use with --source manual)")
    parser.add_argument("--file", dest="filepath", help="Path to text file (use with --source file)")
    parser.add_argument("--lang", help="Language code (e.g. ko, en). Auto-detected if omitted.")
    parser.add_argument("--project", help="Project name guess")

    args = parser.parse_args()

    if args.source == "manual":
        if not args.text:
            parser.error("--text is required when --source is manual")
        raw_text = args.text

    elif args.source == "file":
        if not args.filepath:
            parser.error("--file is required when --source is file")
        raw_text = Path(args.filepath).read_text(encoding="utf-8")

    elif args.source == "stdin":
        print("Reading from stdin (Ctrl+D to finish)...")
        raw_text = sys.stdin.read()

    else:
        parser.error(f"Unknown source: {args.source}")

    raw_text = raw_text.strip()
    if not raw_text:
        print("[ingest] Error: empty input", file=sys.stderr)
        sys.exit(1)

    input_id = ingest(
        raw_text=raw_text,
        source=args.source,
        language=args.lang,
        project_guess=args.project,
    )
    print(f"[ingest] input_id: {input_id}")


if __name__ == "__main__":
    main()
