"""
query.py — Retrieve relevant entities from the agent wiki

Usage:
    python scripts/query.py --query "왜 모델이 같은 해결책 루프만 반복하지?"
    python scripts/query.py --query "구조를 먼저 물어야 하는 상황" --type principle
    python scripts/query.py --query "디버깅" --type session --filter phase=debugging
    python scripts/query.py --query "패턴" --type pattern --filter type=failure

Retrieval priority (when --type not specified):
    Principle > Pattern > Session > Raw
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils import DATA, load_all, patterns_dir, principles_dir, sessions_dir


# ── Scoring ───────────────────────────────────────────────────────────────────
def _text_of_session(s: dict) -> str:
    return " ".join(filter(None, [
        s.get("title"), s.get("summary"), s.get("surface_problem"),
        s.get("actual_problem"), s.get("why_it_mattered"),
        " ".join(s.get("candidate_principles") or []),
        " ".join(s.get("candidate_patterns") or []),
        " ".join(s.get("constraints") or []),
    ]))


def _text_of_principle(p: dict) -> str:
    return " ".join(filter(None, [
        p.get("title"), p.get("statement"), p.get("description"),
        " ".join(p.get("query_forms") or []),
        " ".join(p.get("signals") or []),
        p.get("applicability"), p.get("agent_implication"),
    ]))


def _text_of_pattern(p: dict) -> str:
    return " ".join(filter(None, [
        p.get("name"), p.get("definition"),
        " ".join(p.get("triggers") or []),
        " ".join(p.get("signals") or []),
        p.get("agent_response"),
    ]))


def score(text: str, keywords: list[str]) -> float:
    text_lower = text.lower()
    hits = sum(1 for kw in keywords if kw in text_lower)
    return hits / max(len(keywords), 1)


def tokenize(query: str) -> list[str]:
    """Simple tokenizer: split on whitespace and common Korean/English separators."""
    import re
    tokens = re.split(r"[\s,?？!！.。]+", query.strip())
    return [t.lower() for t in tokens if len(t) >= 2]


# ── Field filters ─────────────────────────────────────────────────────────────
def apply_filter(records: list[dict], filter_str: str | None) -> list[dict]:
    if not filter_str:
        return records
    key, _, value = filter_str.partition("=")
    return [r for r in records if str(r.get(key.strip(), "")) == value.strip()]


# ── Retrieval ─────────────────────────────────────────────────────────────────
def retrieve(
    query: str,
    entity_type: str | None = None,
    field_filter: str | None = None,
    top_k: int = 5,
) -> list[dict]:
    keywords = tokenize(query)
    results: list[dict] = []

    def search(records: list[dict], text_fn, kind: str, priority: int) -> None:
        records = apply_filter(records, field_filter)
        for rec in records:
            s = score(text_fn(rec), keywords)
            if s > 0:
                results.append({
                    "type": kind,
                    "priority": priority,
                    "score": s,
                    "id": rec.get(f"{kind}_id") or rec.get("pattern_id") or rec.get("session_id"),
                    "title": rec.get("title") or rec.get("name") or rec.get("pattern_id"),
                    "excerpt": (
                        rec.get("statement")
                        or rec.get("definition")
                        or rec.get("summary", "")[:120]
                    ),
                    "confidence": rec.get("confidence"),
                })

    if entity_type in (None, "principle"):
        search(load_all(principles_dir()), _text_of_principle, "principle", 1)
    if entity_type in (None, "pattern"):
        search(load_all(patterns_dir()), _text_of_pattern, "pattern", 2)
    if entity_type in (None, "session"):
        search(load_all(sessions_dir()), _text_of_session, "session", 3)

    # Sort: priority ascending, score descending
    results.sort(key=lambda r: (r["priority"], -r["score"]))
    return results[:top_k]


# ── Display ───────────────────────────────────────────────────────────────────
def display(results: list[dict], query: str) -> None:
    if not results:
        print(f'\n[query] No results found for: "{query}"')
        return
    print(f'\n[query] Results for: "{query}"')
    print("=" * 70)
    for i, r in enumerate(results, 1):
        conf = f"  confidence={r['confidence']}" if r.get("confidence") else ""
        print(f"\n#{i}  [{r['type'].upper()}] {r['id']}")
        print(f"    {r['title']}")
        print(f"    score={r['score']:.2f}{conf}")
        if r["excerpt"]:
            excerpt = r["excerpt"][:100].replace("\n", " ")
            print(f"    → {excerpt}...")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Query the agent wiki for relevant entities")
    parser.add_argument("--query", "-q", required=True, help="Natural language query")
    parser.add_argument(
        "--type", "-t",
        choices=["principle", "pattern", "session"],
        default=None,
        help="Entity type to search (default: all, priority order)",
    )
    parser.add_argument(
        "--filter", "-f",
        metavar="KEY=VALUE",
        default=None,
        help="Optional field filter, e.g. phase=debugging or type=failure",
    )
    parser.add_argument(
        "--top", "-n",
        type=int,
        default=5,
        help="Number of results to show (default: 5)",
    )

    args = parser.parse_args()
    results = retrieve(query=args.query, entity_type=args.type, field_filter=args.filter, top_k=args.top)
    display(results, args.query)


if __name__ == "__main__":
    main()
