---
name: opencode-deterministic-fixture
description: Deterministic prompt-only skill used by integration smoke tests for native and OpenCode runtime wiring.
version: 1.0.0
owner: engineering-flow-platform
triggers:
  - /opencode-deterministic-fixture
  - deterministic fixture skill
tools: []
opencode:
  execution_kind: prompt_only
  compatibility: full
  permission:
    default: allow
  capability_tags:
    - integration-fixture
    - deterministic
---
This is a deterministic integration fixture skill.

When invoked by a smoke test, respond with exactly:

EFP_SKILL_FIXTURE_OK

Do not call tools. Do not inspect files. Do not ask follow-up questions.
