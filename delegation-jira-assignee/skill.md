---
name: delegation-jira-assignee
description: Handle long-running Jira assignee delegations, return a Portal-owned Jira status comment body, and assign the issue back to the reporter.
version: 1.0.0
owner: engineering-flow-platform
triggers:
  - jira_assignee
  - delegation jira assignee
  - jira assigned delegation
  - assigned Jira issue delegation
output_format: json
opencode:
  execution_kind: prompt_only
  compatibility: full
  permission:
    default: ask
  capability_tags:
    - prompt-only
    - delegation
    - jira
    - assignee
    - long-running
---

# Delegation Jira Assignee

Use this skill for an `agent_async_task` created from a `jira_assignee` Portal Delegation. The task represents a Jira issue assigned through the issue delegation. Inspect the issue context, work the issue as far as possible, return the exact Jira status comment body in `final_response`, and assign the issue back to the reporter when finished.

The private Jira service and the configured EFP `jira` CLI/tool are already configured in the runtime. Jira operations must use that `jira` tool through Bash. Use `jira commands --json` or `jira schema ... --json` only when needed to discover command shape, options, or supported fields.

Portal owns start feedback and final reply delivery. Portal creates the Jira start/status comment and updates that same comment with `final_response`; return `reply_handled_by_skill: false`. The skill must not create or update Portal-owned status comments, post Jira comments for reply delivery, or provide Jira setup guidance.

If a Jira command fails because the runtime is not configured or the configured tool is unavailable, treat it as an environment blocker. Report the exact failed command and error in `final_response`, `blockers`, `audit_trace`, and `external_actions`; do not provide setup instructions.

## Runtime Input

Parse `input_payload.delegation` first, then use `metadata` as fallback context.

Resolve the issue key or issue URL from:

1. `input_payload.delegation.source_url`
2. `input_payload.delegation.reply_target.issue_key`
3. `input_payload.delegation.source_payload.issue`
4. `metadata`

Expected delegation fields may include `source`, `provider`, `source_url`, `source_comment`, `represented_identity`, `reply_target`, `reaction_target`, and `source_payload`.

If no issue key or URL can be resolved, return `status: "blocked"` with a precise blocker. Do not invent a project key or issue number.

## Portal-Owned Status Comment

Do not add or edit Jira comments for delegation status or final reply delivery. Portal creates the start/status comment before the skill runs and updates that same comment with the returned `final_response`. The `final_response` field must be the exact markdown Portal should use to update the Jira status comment.

## Fetch Issue Context

Fetch the full issue context:

```bash
jira issue get <issue-key-or-url> --json
```

Inspect summary, description, status, priority, labels, components, assignee, reporter, recent comments, linked context, and acceptance criteria. If the initial output omits needed fields, discover available options:

```bash
jira commands --json
jira schema issue.get --json
```

Then refetch with the CLI-supported field or expand options.

## Work The Issue

Work the issue as far as possible from available context:

- Identify the requested outcome and acceptance criteria.
- Inspect linked repository, PR, build, incident, runbook, or document context when the workspace and task context allow it.
- Perform bounded local analysis when files are available.
- Do not modify external systems unless the issue text, delegation context, or user instructions explicitly allow the action.
- Do not invent facts, statuses, owners, dates, or validation results.
- If required information is missing, produce a precise blocker list.

Use this `final_response` structure:

```markdown
Automated EFP delegation result.

## Outcome

## Work Performed / Analysis

## Blockers

## Validation

## Next Recommendation
```

## Assign Back To Reporter

After completing the work and preparing `final_response`, assign the Jira issue back to the reporter.

Use the reporter identifier returned by `jira issue get`, then run the normal CLI assignment command:

```bash
jira issue assign <issue-key-or-url> --user <reporter-identifier> --json
```

If the reporter identifier is missing from the fetched issue or unsupported by the configured `jira` tool, record a blocker or assignment action failure instead of inventing identity details. Record assignment success or failure in `external_actions`. Set `jira_reassigned_to_reporter` to `true` only when reassignment succeeds.

## Output Contract

Return pure JSON when possible. If the runtime requires markdown, include exactly one machine-readable JSON block.

Required fields:

```json
{
  "status": "success | blocked | error",
  "summary": "Short operational summary.",
  "final_response": "Exact markdown Portal should use to update the Jira status comment.",
  "reply_handled_by_skill": false,
  "blockers": [],
  "next_recommendation": "Concrete next step.",
  "artifacts": [],
  "audit_trace": [],
  "external_actions": [],
  "jira_reassigned_to_reporter": false
}
```
