---
name: delegation-jira-assignee
description: Handle long-running Jira assignee delegations, manage the Jira status comment lifecycle, and assign the issue back to the reporter.
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
    - writeback
---

# Delegation Jira Assignee

Use this skill for an `agent_async_task` created from a `jira_assignee` Portal Delegation. The task represents a Jira issue assigned to the configured agent or user. The skill owns Jira writeback: add a start comment, edit that same comment with the final result, and assign the issue back to the reporter when finished.

Jira operations should use the EFP `jira` CLI from `engineering-flow-platform-tools` through Bash. Use `jira schema` or `jira commands` only when needed to discover the exact supported command shape. Do not rely on Portal for the Jira final reply; return `reply_handled_by_skill: true`.

## Runtime Input

Parse `input_payload.delegation` first, then use `metadata` as fallback context.

Resolve the issue key or issue URL from:

1. `input_payload.delegation.source_url`
2. `input_payload.delegation.reply_target.issue_key`
3. `input_payload.delegation.source_payload.issue`
4. `metadata`

Expected delegation fields may include `source`, `provider`, `source_url`, `source_comment`, `represented_identity`, `reply_target`, `reaction_target`, and `source_payload`.

If no issue key or URL can be resolved, return `status: "blocked"` with a precise blocker. Do not invent a project key or issue number.

## Start Comment

At the very start, add a concise Jira comment saying the EFP agent has started processing the issue. The comment must say it is an automated EFP delegation run.

Write the body to a temporary file and run:

```bash
jira issue comment add <issue-key-or-url> --body-file <tmpfile> --json
```

Parse and store the created comment id as `jira_status_comment_id`. Record the command and result in `external_actions` and `audit_trace`.

If adding the start comment fails, continue only if it is safe to inspect the issue without writeback. Return `status: "blocked"` or `status: "error"` with `final_response` explaining that Jira writeback failed. Do not silently complete a Jira assignee task when the status comment cannot be created.

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

Use this final comment structure:

```markdown
Automated EFP delegation result.

## Outcome

## Work Performed / Analysis

## Blockers

## Validation

## Next Recommendation
```

## Final Comment Update

Finalize by editing the same start comment with the final result:

```bash
jira issue comment update <issue-key-or-url> <comment-id> --body-file <tmpfile> --json
```

The `final_response` field in the output must be exactly the same text written to the Jira comment. If editing the final comment fails, do not add a second final comment unless that is necessary to avoid losing the result. Record the failure and any fallback write in `audit_trace` and `external_actions`.

## Assign Back To Reporter

After the final comment update, assign the Jira issue back to the reporter.

Extract reporter identity from the issue fields. Prefer the CLI assignment command:

```bash
jira issue assign <issue-key-or-url> --user <reporter.name-or-key> --json
```

If Jira Cloud exposes only `accountId` and the CLI assignment command cannot use it, confirm the exact API path from `jira commands`, `jira schema`, or observed CLI behavior. Then use a raw Jira API fallback only when necessary, for example:

```bash
jira api put <issue-assignee-endpoint> --body-file <tmpfile> --json
```

The fallback body should contain the reporter account id, such as `{"accountId":"..."}`. Record assignment success or failure in `external_actions`. Set `jira_reassigned_to_reporter` to `true` only when reassignment succeeds.

## Output Contract

Return pure JSON when possible. If the runtime requires markdown, include exactly one machine-readable JSON block.

Required fields:

```json
{
  "status": "success | blocked | error",
  "summary": "Short operational summary.",
  "final_response": "Same text written to the Jira status comment.",
  "reply_handled_by_skill": true,
  "blockers": [],
  "next_recommendation": "Concrete next step.",
  "artifacts": [],
  "audit_trace": [],
  "external_actions": [],
  "jira_status_comment_id": "created comment id or null",
  "jira_reassigned_to_reporter": false
}
```

For blocked or error results, still try to update the original status comment with the blocker or error result when a comment id exists.
