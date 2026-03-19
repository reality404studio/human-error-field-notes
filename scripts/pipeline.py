"""
pipeline.py — Fully automated Raw → Session → Principle → Pattern → Export pipeline
Uses Claude claude-haiku-3-5-20241022 for all LLM steps.

Usage:
    # Process an already-ingested raw input
    python scripts/pipeline.py --raw-id RAW-20260312-001

    # Ingest + full pipeline in one command
    python scripts/pipeline.py --text "오늘 있던 일..." --source manual

    # Ingest from file + full pipeline
    python scripts/pipeline.py --file path/to/note.txt

Environment:
    ANTHROPIC_API_KEY — required
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils import (
    DATA,
    now_iso,
    parse_frontmatter,
    raw_dir,
    write_json,
    write_markdown,
)

import yaml

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass

MODEL = "claude-haiku-3-5-20241022"
PROMPTS = Path(__file__).parent.parent / "prompts"


# ── Claude helper ─────────────────────────────────────────────────────────────
def call_claude(system_prompt: str, user_message: str) -> str:
    import anthropic
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set. Add it to .env or export it.")

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return message.content[0].text


# ── YAML extraction ───────────────────────────────────────────────────────────
def extract_yaml_blocks(text: str) -> list[dict]:
    """Extract all YAML blocks from LLM response and parse them."""
    # Try ```yaml ... ``` blocks first
    blocks = re.findall(r"```yaml\s*([\s\S]+?)```", text, re.MULTILINE)
    if not blocks:
        # Fallback: treat the whole response as YAML
        blocks = [text]

    results = []
    for block in blocks:
        try:
            parsed = yaml.safe_load(block.strip())
            if isinstance(parsed, list):
                results.extend(parsed)
            elif isinstance(parsed, dict):
                results.append(parsed)
        except yaml.YAMLError as e:
            print(f"  [WARN] YAML parse error: {e}")
    return results


# ── Load prompt files ─────────────────────────────────────────────────────────
def load_prompt(filename: str) -> str:
    path = PROMPTS / filename
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


# ── Step 0: Find raw record ───────────────────────────────────────────────────
def load_raw(raw_id: str) -> dict | None:
    for f in (DATA / "raw").rglob(f"{raw_id}.md"):
        return parse_frontmatter(f)
    return None


# ── Step 1: Sessionize ────────────────────────────────────────────────────────
def run_sessionize(raw_id: str, raw_text: str, project_guess: str | None) -> list[dict]:
    print(f"\n[pipeline] Step 1/3 — Sessionize (Claude Haiku)...")
    system = load_prompt("sessionize.md")
    user = f"""
Raw Input ID: {raw_id}
Project: {project_guess or 'unknown'}

Raw Text:
{raw_text}

---
위 raw text를 분석하여 Session Record YAML을 생성하세요.
각 세션을 yaml 코드블록(```yaml ... ```)으로 반환하세요.
session_id는 프로젝트와 날짜를 반영한 고유 ID를 새로 생성하세요.
raw_source_ids: [{raw_id}]
"""
    response = call_claude(system, user)
    sessions = extract_yaml_blocks(response)
    print(f"  → {len(sessions)} session(s) extracted")
    return sessions


# ── Step 2: Distill principles ────────────────────────────────────────────────
def run_distill(sessions: list[dict]) -> list[dict]:
    print(f"\n[pipeline] Step 2/3 — Distill Principles (Claude Haiku)...")
    system = load_prompt("distill_principles.md")
    sessions_yaml = yaml.dump(sessions, allow_unicode=True)
    user = f"""
다음 Session Record들로부터 Principle을 추출하세요.
각 Principle을 yaml 코드블록(```yaml ... ```)으로 반환하세요.
principle_id는 기존 PR-NNN 넘버링 이후 번호로 생성하세요.
status: draft

Sessions:
{sessions_yaml}
"""
    response = call_claude(system, user)
    principles = extract_yaml_blocks(response)
    print(f"  → {len(principles)} principle(s) extracted")
    return principles


# ── Step 3: Classify patterns ─────────────────────────────────────────────────
def run_classify(sessions: list[dict], principles: list[dict]) -> list[dict]:
    print(f"\n[pipeline] Step 3/3 — Classify Patterns (Claude Haiku)...")
    system = load_prompt("classify_patterns.md")

    # Load existing patterns for matching context
    from utils import load_all, patterns_dir
    existing_patterns = load_all(patterns_dir())
    existing_summary = yaml.dump(
        [{"pattern_id": p["pattern_id"], "name": p.get("name"), "triggers": p.get("triggers"), "signals": p.get("signals")}
         for p in existing_patterns],
        allow_unicode=True
    )

    sessions_yaml = yaml.dump(sessions, allow_unicode=True)
    principles_yaml = yaml.dump(principles, allow_unicode=True)

    user = f"""
다음 Sessions와 Principles로부터 Pattern을 매칭하거나 새로 생성하세요.
기존 패턴과 겹치면 새로 만들지 말고 related_pattern_ids에 참조만 추가하세요.
각 Pattern을 yaml 코드블록(```yaml ... ```)으로 반환하세요.
stability: provisional

기존 패턴 목록 (매칭 참고용):
{existing_summary}

New Sessions:
{sessions_yaml}

New Principles:
{principles_yaml}
"""
    response = call_claude(system, user)
    patterns = extract_yaml_blocks(response)
    print(f"  → {len(patterns)} pattern(s) extracted")
    return patterns


# ── Save helpers ──────────────────────────────────────────────────────────────
def save_entities(sessions: list[dict], principles: list[dict], patterns: list[dict]) -> None:
    from sessionize import save_session, validate_session
    from distill import save_principle, validate_principle
    from classify import save_pattern, validate_pattern

    print("\n[pipeline] Saving sessions...")
    for s in sessions:
        errs = validate_session(s)
        if errs:
            print(f"  [WARN] {s.get('session_id','?')}: {errs}")
        save_session(s)
        print(f"  → {s.get('session_id')}")

    print("\n[pipeline] Saving principles...")
    for p in principles:
        errs = validate_principle(p)
        if errs:
            print(f"  [WARN] {p.get('principle_id','?')}: {errs}")
        save_principle(p)
        print(f"  → {p.get('principle_id')}")

    print("\n[pipeline] Saving patterns...")
    for pat in patterns:
        errs = validate_pattern(pat)
        if errs:
            print(f"  [WARN] {pat.get('pattern_id','?')}: {errs}")
        save_pattern(pat)
        print(f"  → {pat.get('pattern_id')}")


def run_export_and_index() -> None:
    print("\n[pipeline] Rebuilding exports and indexes...")
    import export as exp
    import index as idx
    exp.export_all()
    idx.regenerate_indexes()


# ── Main pipeline ─────────────────────────────────────────────────────────────
def run_pipeline(raw_id: str) -> None:
    print(f"\n{'='*60}")
    print(f"[pipeline] Starting full pipeline for {raw_id}")
    print(f"{'='*60}")

    raw = load_raw(raw_id)
    if not raw:
        print(f"[pipeline] ERROR: Raw Input not found: {raw_id}", file=sys.stderr)
        sys.exit(1)

    raw_text = raw.get("raw_text", "")
    project_guess = raw.get("project_guess")

    sessions = run_sessionize(raw_id, raw_text, project_guess)
    if not sessions:
        print("[pipeline] ERROR: No sessions extracted.", file=sys.stderr)
        sys.exit(1)

    principles = run_distill(sessions)
    patterns = run_classify(sessions, principles)

    save_entities(sessions, principles, patterns)
    run_export_and_index()

    print(f"\n{'='*60}")
    print(f"[pipeline] Complete!")
    print(f"  Sessions:   {len(sessions)}")
    print(f"  Principles: {len(principles)}")
    print(f"  Patterns:   {len(patterns)}")
    print(f"{'='*60}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Full auto-pipeline: Raw → Session → Principle → Pattern → Export"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--raw-id", help="Already-ingested Raw Input ID")
    group.add_argument("--text", help="Raw text to ingest, then pipeline")
    group.add_argument("--file", dest="filepath", help="Text file to ingest, then pipeline")

    parser.add_argument("--source", default="manual", choices=["manual", "file", "stdin"])
    parser.add_argument("--lang", default=None)
    parser.add_argument("--project", default=None)

    args = parser.parse_args()

    if args.raw_id:
        run_pipeline(args.raw_id)

    else:
        # Ingest first, then pipeline
        import ingest as ing
        from datetime import datetime, timezone

        if args.text:
            raw_text = args.text.strip()
            source = "manual"
        else:
            raw_text = Path(args.filepath).read_text(encoding="utf-8").strip()
            source = "file"

        raw_id = ing.ingest(
            raw_text=raw_text,
            source=source,
            language=args.lang,
            project_guess=args.project,
        )
        run_pipeline(raw_id)


if __name__ == "__main__":
    main()
