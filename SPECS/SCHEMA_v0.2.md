# SCHEMA_v0.2.md — Entity Schema Definitions

## 1. Raw Input

```yaml
input_id:        # str  — e.g. RAW-20260312-001
source:          # str  — manual | file | stdin
language:        # str  — ko | en | ...
project_guess:   # str | null
timestamp:       # ISO 8601
raw_text:        # str
```

---

## 2. Session Record

```yaml
session_id:           # str  — e.g. Q3-CAM-001
title:                # str
project:              # str
domain:               # str
phase:                # enum → see controlled values
outcome_type:         # enum → see controlled values
resolution_status:    # enum → see controlled values
raw_source_ids:       # list[str]
summary:              # str
context:              # str
surface_problem:      # str  ← MANDATORY
actual_problem:       # str  ← MANDATORY
trigger:              # str
human_state:          # str
questioning_pattern:  # str
agent_failure_mode:   # str
constraints:          # list[str]
observability_notes:  # str
action_taken:         # str
what_changed:         # str
result:               # str
why_it_mattered:      # str
candidate_principles: # list[str]  — principle_ids
candidate_patterns:   # list[str]  — pattern_ids
confidence:           # float 0.0–1.0
```

### Controlled values — phase
- ideation
- planning
- implementation
- debugging
- evaluation
- launch
- reflection
- meta-collaboration

### Controlled values — outcome_type
- failure
- success
- mixed
- reframing
- discovery

### Controlled values — resolution_status
- unresolved
- partial
- resolved
- resolved_accidentally
- ongoing

---

## 3. Principle

```yaml
principle_id:         # str  — e.g. PR-001
title:                # str
statement:            # str  — sentence-shaped, queryable
description:          # str
source_session_ids:   # list[str]
applicability:        # str
anti_applicability:   # str
signals:              # list[str]
query_forms:          # list[str]  ← important for agent retrieval
agent_implication:    # str
confidence:           # float 0.0–1.0
status:               # enum: draft | stable | deprecated
```

### Quality rules
- Must be sentence-shaped
- Must be queryable
- Must express mechanism, not vague advice
- Must link to at least one session

---

## 4. Pattern

```yaml
pattern_id:                # str  — e.g. PAT-001
name:                      # str  — kebab-case slug
type:                      # enum → see controlled values
definition:                # str
triggers:                  # list[str]
signals:                   # list[str]
included_principle_ids:    # list[str]
representative_session_ids: # list[str]
parent_pattern_id:         # str | null
related_pattern_ids:       # list[str]
agent_response:            # str
confidence:                # float 0.0–1.0
stability:                 # enum: draft | provisional | stable
```

### Controlled values — type
- failure
- success
- reframing
- leverage
- behavioral
- meta-collaboration

### Controlled values — stability
- draft
- provisional
- stable

### Rules
- Prefer matching existing Pattern before creating new
- Never create with no supporting Session or Principle
- Shallow taxonomy only; no deep hierarchy in MVP
