# Agent Wiki MVP

자유형식 인간 노트를 에이전트가 검색·활용할 수 있는 구조화된 wiki로 변환하는 시스템.

## 4계층 구조

| 레이어 | 설명 |
|---|---|
| Raw Input | 인간이 쓴 날것의 메모 |
| Session Record | 하나의 핵심 메커니즘 단위로 정리된 기록 |
| Principle | 세션에서 증류된 원칙 (문장형, 검색 가능) |
| Pattern | 반복 관찰되는 행동/실패/성공 패턴 |

## 처리 순서

```
Raw → Session → Principle → Pattern
```

## 사용법

```bash
# 1. 텍스트 인제스트
python scripts/ingest.py --source manual --text "..."

# 2. 세션화
python scripts/sessionize.py --raw-id RAW-YYYYMMDD-NNN

# 3. 원칙 추출
python scripts/distill.py --session-id SESSION-ID

# 4. 패턴 분류
python scripts/classify.py --session-id SESSION-ID

# 5. 내보내기
python scripts/export.py

# 6. 쿼리
python scripts/query.py --type principle --query "검색어"
```

## 디렉토리 구조

```
agent-wiki-mvp/
  README.md
  AGENTS.md
  SPECS/
  data/
    inbox/
    raw/
    sessions/
    principles/
    patterns/
    indexes/
    exports/
  prompts/
  scripts/
  tests/
```
