# PIPELINE.md — Processing Pipeline Specification

## Overview

```
Human Note (free-form)
        ↓
   [1] ingest.py
        ↓
   Raw Input (data/raw/)
        ↓
   [2] sessionize.py
        ↓
   Session Record (data/sessions/)
        ↓
   [3] distill.py
        ↓
   Principle (data/principles/)
        ↓
   [4] classify.py
        ↓
   Pattern (data/patterns/)
        ↓
   [5] export.py
        ↓
   Aggregate JSON (data/exports/)
        ↓
   [6] query.py  ← Agent retrieval entry point
```

## Stage details

### Stage 1: Ingest
- Input: free-form text (stdin, file, or --text argument)
- Output: `data/raw/YYYY/MM/DD/{input_id}.md` + optional JSON
- Script: `scripts/ingest.py`

### Stage 2: Sessionize
- Input: raw_id
- Output: one or more `data/sessions/{session_id}.md`
- Split rule: one session = one core mechanism
- Script: `scripts/sessionize.py`

### Stage 3: Distill
- Input: session_id(s)
- Output: `data/principles/{principle_id}.md`
- Principle must be sentence-shaped and queryable
- Script: `scripts/distill.py`

### Stage 4: Classify
- Input: session_id(s) and/or principle_id(s)
- Output: `data/patterns/{pattern_id}.md`
- Always match existing before creating new
- Script: `scripts/classify.py`

### Stage 5: Export
- Input: all entities in data/
- Output: `data/exports/all_sessions.json`, `all_principles.json`, `all_patterns.json`, `graph.json`
- Script: `scripts/export.py`

### Stage 6: Query
- Input: query string + optional type filter
- Output: ranked relevant entity list
- Priority: Principle > Pattern > Session > Raw
- Script: `scripts/query.py`

## Processing rules

- Never generate Pattern without evidence from Session or Principle
- Always bottom-up: Raw → Session → Principle → Pattern
- Every Session must reference at least one raw_source_id
- Every Principle must reference at least one source_session_id
- Every Pattern must include at least one representative_session_id
