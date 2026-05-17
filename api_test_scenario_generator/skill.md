---
name: api-test-scenario-generator
description: Generate API test scenarios (happy/validation/error/boundary) based on API requirements and rules
version: 1.0.0
owner: qa-platform
triggers:
  - api test scenario
  - generate api tests
  - API test scenarios
  - Generate API tests
tools: []
planning_mode: required
execution_style: stepwise
ask_user_policy: blocked_only
strategy:
  - "1. Identify endpoint paths, request fields, response schema, status codes, and business rules."
  - "2. If key fields or validation rules are missing, ASK_USER first, then continue."
  - "3. Advance one core step per round: happy path first, then validation/error/boundary."
  - "4. Focus on executable test ideas, not implementation details."
output_format: markdown
opencode:
  execution_kind: prompt_only
  compatibility: full
  permission:
    default: ask
  capability_tags:
    - prompt-only
---

# API Test Scenario Generator

Used to quickly draft API test coverage in early requirement stages.

## Skill Mode Progression
- If key request/response definitions are missing, prioritize **[ASK_USER]**.
- When information is sufficient, **[EXECUTE]** the most valuable current test group.
- After coverage is complete, summarize with **[FINISH]**.

## Suggested Result Structure
- Happy Path
- Validation Cases
- Error Cases
- Boundary Cases
- Risks and pending confirmations
