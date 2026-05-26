---
name: delegation-jira-mention
description: Handle long-running Jira mention delegations and manage the Jira status comment lifecycle with a final answer or result.
version: 1.0.0
owner: engineering-flow-platform
triggers:
  - jira_mention
  - delegation jira mention
  - jira mention delegation
  - mentioned in Jira issue delegation
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
    - mention
    - long-running
    - writeback
---

# Delegation Jira Mention

Use this skill for an `agent_async_task` created from a `jira_mention` Portal Delegation. The task represents an issue/mention delegation from a Jira issue comment. The skill owns Jira writeback: add a start comment immediately and edit that same comment with the final answer or result.

The private Jira service and the configured EFP `jira` CLI/tool are already configured in the runtime. Jira operations must use that `jira` tool through Bash. Use `jira commands --json` or `jira schema ... --json` only when needed to discover command shape, options, or supported fields. Do not rely on Portal for the Jira final reply; return `reply_handled_by_skill: true`.

If a Jira command fails because the runtime is not configured or the configured tool is unavailable, treat it as an environment blocker. Report the exact failed command and error in `final_response`, `blockers`, `audit_trace`, and `external_actions`; do not provide setup instructions.

## Runtime Input

Parse `input_payload.delegation` first, then use `metadata` as fallback context.

Resolve:

- issue key or issue URL
- triggering mention text
- triggering comment id, author, and URL when available
- represented identity

Use these sources in order:

1. `input_payload.delegation.source_url`
2. `input_payload.delegation.source_comment`
3. `input_payload.delegation.source_payload.comment`
4. `input_payload.delegation.reply_target.issue_key`
5. `input_payload.delegation.source_payload.issue`
6. `metadata`

Expected delegation fields may include `source`, `provider`, `source_url`, `source_comment`, `represented_identity`, `reply_target`, `reaction_target`, and `source_payload`.

If the issue cannot be resolved, return `status: "blocked"` with exact missing fields. If the triggering comment cannot be resolved but the issue can be resolved, continue with the issue context and record the limitation in `audit_trace`.

## Start Comment

At the very start, add a concise Jira comment saying the EFP agent is processing the mention. The comment must say it is an automated EFP delegation run.

Write the body to a temporary file and run:

```bash
jira issue comment add <issue-key-or-url> --body-file <tmpfile> --json
```

Parse and store the created comment id as `jira_status_comment_id`. Record the command and result in `external_actions` and `audit_trace`.

If adding the start comment fails, continue only if it is safe to inspect the issue without writeback. Return `status: "blocked"` or `status: "error"` with `final_response` explaining that Jira writeback failed. Do not silently complete a Jira mention task when the status comment cannot be created.

## Fetch Issue Context

Fetch the issue and recent comments:

```bash
jira issue get <issue-key-or-url> --json
```

Inspect summary, description, status, priority, labels, components, assignee, reporter, recent comments, linked context, and acceptance criteria. If the CLI output omits comments or fields needed for the mention, discover command options:

```bash
jira commands --json
jira schema issue.get --json
```

Then refetch with supported field or expand options.

## Determine Intent

Classify the mention into one or more requested actions:

- answer a question
- explain state
- investigate a linked failure
- suggest next action
- summarize blockers
- perform a bounded action if the task context explicitly allows it

Respond as an agent acting on behalf of `input_payload.delegation.represented_identity`. Do not pretend to be the human user.

If the mention asks for external changes, do not perform them unless the issue text, delegation context, or user instructions explicitly grant permission and the target system is available. Otherwise, provide a concrete plan and blockers.

Do not reassign the issue for mention tasks unless the triggering comment explicitly asks for reassignment and it is safe.

## Final Comment Update

Edit the same start comment with the final response:

```bash
jira issue comment update <issue-key-or-url> <comment-id> --body-file <tmpfile> --json
```

The `final_response` field in the output must be exactly the same text written to the Jira comment. If editing the final comment fails, do not add a second final comment unless that is necessary to avoid losing the result. Record the failure and any fallback write in `audit_trace` and `external_actions`.

Use this final comment structure:

```markdown
Automated EFP delegation result.

## Mention Context

## Answer / Result

## Evidence

## Blockers

## Next Recommendation
```

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
  "jira_status_comment_id": "created comment id or null"
}
```

If reassignment is explicitly requested and attempted, include `jira_reassigned_to_reporter` and the assignment action in `external_actions`.
