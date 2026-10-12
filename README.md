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

## API

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

`scripts/`의 CLI는 브라우저를 거치지 않으므로 CORS와 무관하게 동작합니다. 브라우저에서 다른 주소의 페이지가 이 API를 부를 때만 아래 허용 목록이 적용됩니다.

호스트(서버) 환경 변수 **`ALLOWED_ORIGINS`** 에 프론트 주소를 쉼표로 구분해 넣습니다. 스키마, 호스트, 포트만 쓰고 경로는 빼세요.

```bash
ALLOWED_ORIGINS=https://your-frontend.example,http://localhost:5173
```

값을 비우면 로컬 개발 주소만 허용합니다.

- `http://localhost:3000`
- `http://127.0.0.1:3000`
- `http://localhost:5173`
- `http://127.0.0.1:5173`

이 저장소에는 프론트 설정, 배포 파일, 운영 프론트 주소가 없습니다. 운영 프론트를 붙이는 호스트에서는 `ALLOWED_ORIGINS`에 그 주소를 넣으세요. `*` 는 무시되고, 쿠키를 주고받는 CORS는 꺼져 있습니다. 예시는 `.env.example`을 보세요.

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
