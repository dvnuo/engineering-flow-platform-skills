---
name: jira-to-cucumber-tests
description: Generate Cucumber scenario drafts from Jira issues, asking minimal questions when information is insufficient
version: 1.0.0
owner: qa-platform
triggers:
  - jira cucumber
  - issue to cucumber
  - jira to cucumber
  - Generate Cucumber from Jira
tools:
  - jira_get_issue
  - jira_search
planning_mode: required
execution_style: stepwise
ask_user_policy: blocked_only
strategy:
  - "1. Prioritize extracting acceptance criteria, business flows, and constraints from the Jira issue."
  - "2. If issue information is insufficient, avoid over-guessing; ASK_USER for key acceptance conditions first."
  - "3. Advance one step per round: understand the issue first, then produce scenario drafts, then FINISH."
  - "4. Use tools only when clearly needed to obtain issue information; avoid speculative queries."
output_format: markdown
opencode:
  execution_kind: prompt_only
  compatibility: degraded
  permission:
    default: ask
  capability_tags:
    - prompt-only
    - tools-required
  tool_mappings:
    jira_get_issue: efp_jira_get_issue
    jira_search: efp_jira_search
---

# Jira to Cucumber Tests

Used to convert Jira issues into reviewable Cucumber test drafts.

## Skill Mode Progression
- Prioritize reading requirement context from the issue key/link.
- If acceptance criteria are missing, use **[ASK_USER]** to get the minimum required information.
- Produce a scenario list first, then complete the feature draft, and finally **[FINISH]**.

## Suggested Output
- Key acceptance criteria summary
- Gherkin Scenarios（happy/negative/boundary）
- Directly reviewable feature draft

## Tool Usage Principles
- `jira_get_issue` / `jira_search` Use only when it clearly advances the current step.
- If business rules are missing, ask the user first; do not indiscriminately query many issues.
