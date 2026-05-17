---
name: test-scope-clarifier
description: Clarify first, then output test scope for ambiguous requirements (in/out scope, assumptions, open questions)
version: 1.0.0
owner: qa-platform
triggers:
  - clarify test scope
  - test scope
  - Requirement clarification for test scope
  - Test scope analysis
tools: []
planning_mode: required
execution_style: stepwise
ask_user_policy: blocked_only
strategy:
  - "1. For ambiguous requirements, first identify uncertainties and ASK_USER the minimum necessary questions."
  - "2. Advance only one clarification point per round; avoid asking too many questions at once."
  - "3. Gradually refine in scope / out of scope / assumptions / open questions."
  - "4. Finally FINISH with actionable test scope recommendations."
output_format: markdown
opencode:
  execution_kind: prompt_only
  compatibility: full
  permission:
    default: ask
  capability_tags:
    - prompt-only
---

# Test Scope Clarifier

This is a high-frequency multi-round collaboration skill for turning ambiguous requirements into actionable test scope.

## Skill Mode Progression
- Clarify first; do not rush to output the final solution.
- When key business inputs are missing, you must **[ASK_USER]**.
- Converge on one key uncertainty per round and **[EXECUTE]**.
- After convergence, **[FINISH]** with structured scope recommendations.

## Suggested Output
- In Scope
- Out of Scope
- Assumptions
- Open Questions
- Suggested Test Areas
