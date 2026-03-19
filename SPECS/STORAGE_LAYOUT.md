# STORAGE_LAYOUT.md — Storage Layout Reference

## Root

```
agent-wiki-mvp/
├── README.md          — project overview
├── AGENTS.md          — agent instructions
├── SPECS/             — specification documents
├── data/              — all entity data
├── prompts/           — LLM prompt templates
├── scripts/           — CLI processing scripts
└── tests/             — test suite
```

## data/

```
data/
├── inbox/             — drop zone for new free-form notes
├── raw/
│   └── YYYY/MM/DD/
│       └── {input_id}.md       — e.g. RAW-20260312-001.md
├── sessions/
│   └── {session_id}.md         — e.g. Q3-CAM-001.md
├── principles/
│   └── {principle_id}.md       — e.g. PR-001.md
├── patterns/
│   └── {pattern_id}.md         — e.g. PAT-001.md
├── indexes/
│   ├── sessions_by_project.json
│   ├── patterns_by_parent.json
│   ├── principles_by_query_form.json
│   └── meta_collaboration_patterns.json
└── exports/
    ├── all_sessions.json
    ├── all_principles.json
    ├── all_patterns.json
    └── graph.json
```

## File format per entity

Each entity file = markdown with YAML frontmatter:

```markdown
---
{yaml fields}
---

# Summary / Statement / Definition
{human-readable prose}
```

## Naming conventions

| Entity | ID format | Example |
|---|---|---|
| Raw Input | RAW-YYYYMMDD-NNN | RAW-20260312-001 |
| Session | {project_code}-NNN | Q3-CAM-001 |
| Principle | PR-NNN | PR-001 |
| Pattern | PAT-NNN | PAT-001 |

## graph.json structure

```json
{
  "nodes": [
    {"id": "RAW-20260312-001", "type": "raw"},
    {"id": "Q3-CAM-001", "type": "session"},
    {"id": "PR-001", "type": "principle"},
    {"id": "PAT-001", "type": "pattern"}
  ],
  "edges": [
    {"from": "Q3-CAM-001", "to": "RAW-20260312-001", "rel": "source"},
    {"from": "PR-001", "to": "Q3-CAM-001", "rel": "derived_from"},
    {"from": "PAT-001", "to": "PR-001", "rel": "includes"}
  ]
}
```
