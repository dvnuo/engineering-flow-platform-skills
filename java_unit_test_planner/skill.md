---
name: java-unit-test-planner
description: Generate Java unit test design ideas (cases/mocks/edge/exception) from class/method requirements
version: 1.0.0
owner: dev-qa-collab
triggers:
  - java unit test
  - unit test planner
  - Generate Java unit test ideas
  - Java test design
tools: []
planning_mode: required
execution_style: stepwise
ask_user_policy: blocked_only
strategy:
  - "1. First determine the responsibilities, inputs/outputs, dependencies, and exception paths of the test target."
  - "2. ASK_USER when method signatures or key business rules are missing."
  - "3. Advance one focus per round: normal path, edge case, exception, mock strategy."
  - "4. Focus on test design; full implementation code is not required."
output_format: markdown
opencode:
  execution_kind: prompt_only
  compatibility: full
  permission:
    default: ask
  capability_tags:
    - prompt-only
---

# Java Unit Test Planner

Used to quickly create a Java unit test plan during dev-test collaboration.

## Skill Mode Progression
- For information gaps, prioritize **[ASK_USER]**.
- After clarification, gradually **[EXECUTE]** and output test design.
- After coverage is complete, **[FINISH]** with priority and implementation suggestions.

## Suggested Output
- Test Cases list
- Mock Points
- Edge Cases
- Exception Paths
- Priority and refactoring suggestions
