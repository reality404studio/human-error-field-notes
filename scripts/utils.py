"""
utils.py — Shared helpers for agent-wiki-mvp
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

# ── Project root ────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"


# ── Paths ────────────────────────────────────────────────────────────────────
def raw_dir(date: datetime | None = None) -> Path:
    d = date or datetime.now(tz=timezone.utc)
    return DATA / "raw" / f"{d.year}" / f"{d.month:02d}" / f"{d.day:02d}"


def sessions_dir() -> Path:
    return DATA / "sessions"


def principles_dir() -> Path:
    return DATA / "principles"


def patterns_dir() -> Path:
    return DATA / "patterns"


def exports_dir() -> Path:
    return DATA / "exports"


def indexes_dir() -> Path:
    return DATA / "indexes"


# ── ID generation ─────────────────────────────────────────────────────────────
def _next_id(directory: Path, prefix: str, date: datetime | None = None) -> str:
    """Generate next sequential ID of the form PREFIX-YYYYMMDD-NNN."""
    d = date or datetime.now(tz=timezone.utc)
    date_str = d.strftime("%Y%m%d")
    pattern = re.compile(rf"^{re.escape(prefix)}-{date_str}-(\d{{3}})\.md$")

    existing: list[int] = []
    for f in directory.glob(f"{prefix}-{date_str}-*.md"):
        m = pattern.match(f.name)
        if m:
            existing.append(int(m.group(1)))

    seq = (max(existing) + 1) if existing else 1
    return f"{prefix}-{date_str}-{seq:03d}"


def next_raw_id(date: datetime | None = None) -> str:
    d = date or datetime.now(tz=timezone.utc)
    return _next_id(raw_dir(d), "RAW", d)


# ── YAML frontmatter ──────────────────────────────────────────────────────────
def parse_frontmatter(path: Path) -> dict[str, Any]:
    """Read YAML frontmatter from a markdown file."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    return yaml.safe_load(parts[1]) or {}


def write_markdown(path: Path, frontmatter: dict[str, Any], body: str = "") -> None:
    """Write entity as markdown with YAML frontmatter."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fm_text = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)
    content = f"---\n{fm_text}---\n"
    if body:
        content += f"\n{body.strip()}\n"
    path.write_text(content, encoding="utf-8")


# ── JSON helpers ──────────────────────────────────────────────────────────────
def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


# ── Load all entities ─────────────────────────────────────────────────────────
def load_all(directory: Path) -> list[dict[str, Any]]:
    """Load all markdown frontmatter records from a directory."""
    records = []
    for f in sorted(directory.glob("*.md")):
        fm = parse_frontmatter(f)
        if fm:
            records.append(fm)
    return records


# ── Timestamp ─────────────────────────────────────────────────────────────────
def now_iso() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
