# distill_principles.md — Prompt for Principle Distillation

## Task
Extract Principle candidates from one or more Session Records.

## Quality rules — a good Principle MUST:
- Be sentence-shaped (a complete declarative statement)
- Be queryable (someone could search for it)
- Express a mechanism, not vague advice
- Link back to one or more Session records

## Required schema fields

```
principle_id, title, statement, description, source_session_ids,
applicability, anti_applicability, signals, query_forms, agent_implication,
confidence, status
```

## Critical field: query_forms
List 2–4 natural-language questions that would lead an agent to retrieve this principle.
This field is the primary retrieval hook.

## Status
All new principles start as `draft`.

## Output format
Each principle as a markdown file with YAML frontmatter.
