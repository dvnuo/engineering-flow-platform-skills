---
name: java-cucumber-generator
description: Convert business requirements into Java Cucumber test drafts (feature + step definitions + structure suggestions)
version: 1.0.0
owner: qa-platform
triggers:
  - java cucumber
  - cucumber java
  - generate cucumber for java
  - Generate Java Cucumber
tools: []
planning_mode: required
execution_style: stepwise
ask_user_policy: blocked_only
strategy:
  - "1. First identify business goals, roles, and key rules; if info is insufficient, ASK_USER first."
  - "2. Advance only one valuable small step per round: for example, feature draft first, then step-definition scaffold."
  - "3. For simple requirements, one EXECUTE pass may be enough; for complex ones, iterate in rounds and FINISH with an actionable checklist."
  - "4. Do not unfold too many implementation details at once; prioritize completing acceptance rules and boundary behaviors."
output_format: markdown
opencode:
  execution_kind: prompt_only
  compatibility: full
  permission:
    default: ask
  capability_tags:
    - prompt-only
---

# Java Cucumber Generator

Used to turn business-scenario requirements into actionable Cucumber test drafts in a Java tech stack.

## Skill Mode Progression
- If key information is missing (roles, business rules, success/failure conditions), start with **[ASK_USER]**.
- When information is sufficient, execute the most critical current step with **[EXECUTE]**.
- After completion, provide a result summary and **[FINISH]**.

## Suggested Output
- Feature file draft (Feature / Scenario / Scenario Outline)
- Java step-definition draft (Given/When/Then method scaffold)
- Page/Service class organization suggestions
- Minimum executable test-structure suggestions

## Tool Usage Principles
- By default, proceed using user input first.
- Use tools only when they are clearly helpful (e.g., reading existing project conventions).
- Do not overuse tools for merely "possibly useful" reasons.
