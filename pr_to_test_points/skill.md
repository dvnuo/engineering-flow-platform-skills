---
name: pr-to-test-points
description: Extract test points and regression suggestions from PR descriptions or changes
version: 1.0.0
owner: qa-platform
triggers:
  - pr test points
  - pull request test
  - Generate test points from a PR
  - Code-change test points
tools: []
planning_mode: required
execution_style: stepwise
ask_user_policy: blocked_only
strategy:
  - "1. Identify PR goals, change scope, and risk paths; use tools to inspect diffs when needed."
  - "2. If information is insufficient, ASK_USER (e.g., release scope, key business impact)."
  - "3. Output minimum actionable test points and regression suggestions, then FINISH."
output_format: markdown
opencode:
  execution_kind: prompt_only
  compatibility: full
  permission:
    default: ask
  capability_tags:
    - prompt-only
---

# PR to Test Points

Used to quickly convert code changes into a test execution checklist, suitable for pre-release review.

## Skill Mode Characteristics
- Can use tools to read PR/change context.
- If business context is missing, start with **[ASK_USER]**.
- Produce one clear testing increment per round and **[EXECUTE]**.
