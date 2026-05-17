---
name: feature-stepdef-scaffolder
description: Complete step-definition design scaffolds based on existing Gherkin features
version: 1.0.0
owner: qa-platform
triggers:
  - step definition scaffold
  - feature to step defs
  - Generate step definitions from feature files
  - Cucumber step scaffold
tools: []
planning_mode: required
execution_style: stepwise
ask_user_policy: blocked_only
strategy:
  - "1. First parse existing feature scenarios and parameters."
  - "2. ASK_USER when technical conventions are missing (test framework, directory, naming)."
  - "3. Output step-definition scaffold and organization suggestions in rounds."
  - "4. Avoid generating a large amount of low-quality boilerplate at once."
output_format: markdown
opencode:
  execution_kind: prompt_only
  compatibility: full
  permission:
    default: ask
  capability_tags:
    - prompt-only
---

# Feature StepDef Scaffolder

Used to quickly generate step-definition design scaffolds from existing feature files.

## Skill Mode Progression
- Input existing feature text or path.
- If technical conventions are missing, start with **[ASK_USER]**.
- Output step structures scenario by scenario via **[EXECUTE]**.
- After convergence, **[FINISH]** with implementation suggestions.
