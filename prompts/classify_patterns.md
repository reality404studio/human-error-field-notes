# classify_patterns.md — Prompt for Pattern Classification

## Task
Match or create Pattern records from Session Records and Principles.

## Rules
1. ALWAYS try to match an existing Pattern before creating a new one
2. Never create a Pattern with no supporting Session or Principle
3. Shallow taxonomy only — do not build deep hierarchy

## Required schema fields

```
pattern_id, name, type, definition, triggers, signals,
included_principle_ids, representative_session_ids,
parent_pattern_id, related_pattern_ids, agent_response,
confidence, stability
```

## Matching criteria
A session matches an existing pattern if:
- Its triggers overlap with the pattern's triggers
- Its signals overlap with the pattern's signals
- The mechanism described is the same

## Stability
All new patterns start as `provisional` unless there are 3+ confirming sessions.

## Output format
Each pattern as a markdown file with YAML frontmatter.
