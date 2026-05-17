---
name: skill-mode-demo
description: Use lightweight skill mode to complete requirement clarification, draft generation, and final delivery in steps
version: 1.0.0
owner: platform
triggers:
  - skill mode demo
  - Draft assistant
  - Requirement clarification
tools: []
planning_mode: required
execution_style: stepwise
ask_user_policy: blocked_only
strategy:
  - "1. Analyze user goals and constraints"
  - "2. When key info is missing, ask only the minimum necessary questions"
  - "3. Provide an executable draft first, then converge to the final result"
output_format: markdown
opencode:
  execution_kind: prompt_only
  compatibility: full
  permission:
    default: ask
  capability_tags:
    - prompt-only
---

# Skill Mode Demo

This skill is used to validate a lightweight skill session:
- Support [ASK_USER] to request required information
- Continue with [EXECUTE] after user input
- Output [FINISH] when completed
