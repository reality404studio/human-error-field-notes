# sessionize.md — Prompt for Sessionization

## Task
Convert a Raw Input into one or more Session Records.

## Splitting rule
Create one session per core mechanism.
Split when there is a strong change in:
- problem type
- questioning mode
- objective
- emotional state
- result
- framing model

## Required schema fields (ALL must be filled)

```
session_id, title, project, domain, phase, outcome_type, resolution_status,
raw_source_ids, summary, context, surface_problem, actual_problem, trigger,
human_state, questioning_pattern, agent_failure_mode, constraints,
observability_notes, action_taken, what_changed, result, why_it_mattered,
candidate_principles, candidate_patterns, confidence
```

## Critical rules
- `surface_problem` and `actual_problem` are MANDATORY and must be distinct
- `raw_source_ids` must reference the source raw input id
- `constraints` must be a list
- `candidate_principles` and `candidate_patterns` can be text labels or future ids

## Output format
Each session as a markdown file with YAML frontmatter followed by prose summary.
