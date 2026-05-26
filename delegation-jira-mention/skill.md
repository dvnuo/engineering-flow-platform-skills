---
name: delegation-jira-mention
description: Handle long-running Jira mention delegations and return a Portal-owned Jira status comment body with a final answer or result.
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
---

# Delegation Jira Mention

Use this skill for an `agent_async_task` created from a `jira_mention` Portal Delegation. The task represents an issue/mention delegation from a Jira issue comment. Inspect the issue and mention context, perform the requested bounded work, and return the exact Jira status comment body in `final_response`.

The private Jira service and the configured EFP `jira` CLI/tool are already configured in the runtime. Jira operations must use that `jira` tool through Bash. Use `jira commands --json` or `jira schema ... --json` only when needed to discover command shape, options, or supported fields.

Portal owns start feedback and final reply delivery. Portal creates the Jira start/status comment and updates that same comment with `final_response`; return `reply_handled_by_skill: false`. The skill must not create or update Portal-owned status comments, post Jira comments for reply delivery, reassign the issue unless explicitly asked, or provide Jira setup guidance.

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

## Portal-Owned Status Comment

Do not add or edit Jira comments for delegation status or final reply delivery. Portal creates the start/status comment before the skill runs and updates that same comment with the returned `final_response`. The `final_response` field must be the exact markdown Portal should use to update the Jira status comment.

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

Use this `final_response` structure:

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
  "final_response": "Exact markdown Portal should use to update the Jira status comment.",
  "reply_handled_by_skill": false,
  "blockers": [],
  "next_recommendation": "Concrete next step.",
  "artifacts": [],
  "audit_trace": [],
  "external_actions": []
}
```

If reassignment is explicitly requested and attempted, include `jira_reassigned_to_reporter` and the assignment action in `external_actions`.
