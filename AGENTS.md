# AGENTS.md — Agent Wiki MVP Instructions

This file provides context for AI agents operating on this project.

## What this project is

A structured memory and retrieval system for AI-human collaboration.
It converts free-form human notes into machine-readable, queryable records.

## Four entity layers (retrieval priority order)

1. **Principle** — Distilled behavioral/structural rules from sessions
2. **Pattern** — Recurring failure, success, or reframing patterns
3. **Session** — Single-mechanism interaction records
4. **Raw Input** — Original unstructured notes (fallback evidence only)

## Key constraints

- Never generate Pattern without evidence from Session or Principle
- Always process bottom-up: Raw → Session → Principle → Pattern
- Prefer matching existing Pattern before creating a new one
- `surface_problem` and `actual_problem` are mandatory in every session

## File locations

- Raw inputs: `data/raw/YYYY/MM/DD/`
- Sessions: `data/sessions/`
- Principles: `data/principles/`
- Patterns: `data/patterns/`
- Exports: `data/exports/`

## Schema reference

See `SPECS/SCHEMA_v0.2.md` for full field definitions.

## When querying

Use `scripts/query.py` with `--type` and `--query` arguments.
Priority: Principle → Pattern → Session → Raw
