---
name: jira-to-manual-test-cases
description: Generate manual test cases (preconditions/steps/expected/negative) from Jira issues
version: 1.0.0
owner: qa-platform
triggers:
  - jira manual test
  - issue to manual test
  - jira test case
  - Generate manual tests from Jira
tools:
  - jira_get_issue
  - jira_search
planning_mode: required
execution_style: stepwise
ask_user_policy: blocked_only
strategy:
  - "1. First extract the issue objective, acceptance criteria, and dependencies."
  - "2. When information is insufficient, ASK_USER for key preconditions and evaluation criteria."
  - "3. Generate structured manual tests: preconditions, steps, expected, negative."
  - "4. Advance one small step per round to avoid overly long, unreviewable output."
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

# Jira to Manual Test Cases

Used to generate manual test cases from a QA execution perspective, not automation code.

## Skill Mode Progression
- First confirm testing goals and scope.
- If information is insufficient, start with **[ASK_USER]**.
- Gradually provide actionable manual test case drafts and **[EXECUTE]**.
- After completion, summarize the test checklist and **[FINISH]**.

## Suggested Output
- Preconditions
- Test Steps
- Expected Results
- Negative/exception paths
- Execution priority suggestions
