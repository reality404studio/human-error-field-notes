# MVP_BUILD_PLAN.md — Build Sequence

## Build order

Follow this sequence exactly. Do not skip ahead.

1. **Directory structure** — create all folders
2. **Schemas and serializers** — `SPECS/SCHEMA_v0.2.md` + shared helpers
3. **Ingest** — `scripts/ingest.py`
4. **Seed raw input** — store 4 provided raw inputs
5. **Sessionize** — `scripts/sessionize.py` using seed examples
6. **Distill** — `scripts/distill.py`
7. **Classify** — `scripts/classify.py`
8. **Export** — `scripts/export.py`
9. **Query** — `scripts/query.py`
10. **Tests** — validate seed data references and basic queries

---

## Milestone 1 (minimum viable)

- `ingest.py` works
- Seeded markdown/json records exist
- `export.py` builds aggregate JSON
- `query.py` retrieves relevant principles/patterns

## Example queries that must work from seed data

- `"왜 모델이 같은 해결책 루프만 반복하지?"`
- `"구조를 먼저 물어야 하는 상황은 언제지?"`
- `"인간용 계획을 모델에게 그대로 주면 왜 안 되지?"`
- `"대화가 다음 단계로 밀릴 때 원래 목적을 어떻게 유지하지?"`

---

## Acceptance criteria

- [ ] Free-form input ingested into Raw storage
- [ ] One raw note generates one or more Session files
- [ ] Session files generate Principle files
- [ ] Pattern files created or matched from those
- [ ] Exports regenerated successfully
- [ ] Query script retrieves relevant Sessions/Principles/Patterns
- [ ] All 4 seed cases present and linked correctly

---

## What NOT to build in MVP

- Rich frontend UI
- Multi-user auth
- Cloud deployment
- Full autonomous write-back without review
- Complex vector DB integration
- Visualization dashboards
