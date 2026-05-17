---
name: bug-repro-test-designer
description: Generate reproduction paths, validation points, and regression test drafts from bug descriptions
version: 1.0.0
owner: qa-platform
triggers:
  - bug repro test
  - defect test design
  - Bug reproduction scenarios
  - Generate bug regression tests
tools: []
planning_mode: required
execution_style: stepwise
ask_user_policy: blocked_only
strategy:
  - "1. First extract reproduction preconditions, trigger steps, actual results, and expected results."
  - "2. When key reproduction conditions are missing, ASK_USER and do not blindly guess environment or data."
  - "3. Advance one goal per round: reproduce first, then verify the fix, then expand regression scope."
  - "4. Finally FINISH with an actionable defect-verification checklist."
output_format: markdown
opencode:
  execution_kind: prompt_only
  compatibility: full
  permission:
    default: ask
  capability_tags:
    - prompt-only
---

# Bug Repro Test Designer

Used to quickly form test action plans during defect analysis and regression phases.

## Skill Mode Progression
- When reproduction conditions are missing, start with **[ASK_USER]**.
- When information is sufficient, **[EXECUTE]** the current key validation step.
- Finally **[FINISH]** with reproduction + regression checklist.
