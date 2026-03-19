---
session_id: META-CHAT-001
title: 다음 액션을 바로 제시하는 모델의 출력 패턴 때문에 사용자가 현재 목적을 계속 재고정해야 했던 사례
project: Agent wiki pipeline design conversation
domain: meta-collaboration / human-LLM workflow
phase: meta-collaboration
outcome_type: success
resolution_status: resolved
raw_source_ids:
- RAW-20260312-004
summary: 대화의 목표는 파이프라인 설계 중에서도 특히 스키마 검증이었다. 실제 사례 3개를 넣어보는 것도 그 검증 목적을 위한 단계였다. 그러나
  모델은 각 출력 이후 자연스럽게 다음 단계 제안을 계속 내놓았고, 3개 사례 입력 후에는 직전 토큰 우선성에 따라 상위 패턴 추출 같은 다음 작업으로
  넘어가려 했다. 사용자가 현재 대화의 위치와 목적을 다시 명시적으로 고정하자, 모델은 스키마 검증 기준으로 다시 판단하고 개선 제안과 다음 구현
  단계로 이어질 수 있었다.
context: 현재 목적은 파이프라인 설계 중 스키마 검증이었고, 실사례 3개 입력은 그 검증 목적을 위한 단계였다.
surface_problem: 모델이 자꾸 다음 액션을 제시하며 흐름을 앞으로 밀어감
actual_problem: 사용자가 현재 위치와 목적을 명시적으로 재고정하지 않으면, 직전 출력의 로컬 우선순위가 전체 프로젝트 목적을 덮을 수
  있다
trigger: 모델의 출력 관성, 다음 단계 제안 습성, 직전 토큰 우선성
human_state: 주의 깊음, 메타 인지 활성화, 흐름 관리 시도
questioning_pattern: 지금의 목적은 무엇인가, 이 사례 입력의 목적은 무엇이었나, 그 기준으로 다시 판단해달라
agent_failure_mode: premature-next-step-push
constraints:
- attention_drift
- local-token-priority
- workflow-goal-forgetting
observability_notes: 이 대화 자체를 메타 사례로 기록하면서 관찰 가능해짐
action_taken: 사용자가 실사례 입력의 목적이 스키마 검증임을 다시 명시함
what_changed: 모델이 상위 패턴 추출로 바로 넘어가려던 흐름을 멈추고, 스키마 유효성 검증과 수정 제안으로 돌아옴
result: 스키마 검증 완료, 다음 시스템 구축 단계로 자연스럽게 전환 가능
why_it_mattered: 모델과 장기 협업할 때 사용자가 현재 위치와 목적을 메타적으로 유지하지 않으면, 작업이 직전 제안에 끌려가며 흐려질
  수 있다
candidate_principles:
- PR-301
- PR-302
- PR-303
candidate_patterns:
- PAT-301
- PAT-302
- PAT-303
confidence: 0.93
---

# 다음 액션을 바로 제시하는 모델의 출력 패턴 때문에 사용자가 현재 목적을 계속 재고정해야 했던 사례

## Summary
대화의 목표는 파이프라인 설계 중에서도 특히 스키마 검증이었다. 실제 사례 3개를 넣어보는 것도 그 검증 목적을 위한 단계였다. 그러나 모델은 각 출력 이후 자연스럽게 다음 단계 제안을 계속 내놓았고, 3개 사례 입력 후에는 직전 토큰 우선성에 따라 상위 패턴 추출 같은 다음 작업으로 넘어가려 했다. 사용자가 현재 대화의 위치와 목적을 다시 명시적으로 고정하자, 모델은 스키마 검증 기준으로 다시 판단하고 개선 제안과 다음 구현 단계로 이어질 수 있었다.
