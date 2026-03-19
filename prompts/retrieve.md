# retrieve.md — Prompt for Agent Retrieval

## Task
Given a user query, retrieve the most relevant entities from the agent wiki.

## Query types and starting layer

| Query type | Start with |
|---|---|
| Case retrieval | Sessions |
| Principle retrieval | Principles |
| Pattern diagnosis | Patterns |

## Retrieval priority (when type is ambiguous)
1. Principle
2. Pattern
3. Session
4. Raw Input (fallback only)

## Matching method (MVP)
- Keyword match over: title, summary, statement, definition, query_forms, signals
- Optional field filter: phase, type, project, outcome_type

## Output format
Return a ranked list with:
- entity id
- entity type
- title or name
- short excerpt (summary or statement snippet)
- confidence score

## Example
Query: "왜 모델이 같은 해결책 루프만 반복하지?"
Expected top results:
- PR-101 (principle)
- PAT-101 (pattern)
- Q3-PT-001 (session)
