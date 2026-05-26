---
name: delegation-github-pr-mention
description: Handle long-running GitHub pull request mention delegations by answering or acting on the triggering PR comment context.
version: 1.0.0
owner: engineering-flow-platform
triggers:
  - github_pr_mention
  - delegation github pr mention
  - github mention delegation
  - pull request mention delegation
output_format: json
opencode:
  execution_kind: prompt_only
  compatibility: full
  permission:
    default: ask
  capability_tags:
    - prompt-only
    - delegation
    - github
    - pull-request-mention
    - long-running
---

# Delegation GitHub PR Mention

Use this skill for an `agent_async_task` created from a `github_pr_mention` Portal Delegation. The task represents a configured GitHub user who was mentioned in a PR issue comment or PR review comment. Determine the requested action from the mention, inspect enough context, and return the final response for Portal to post as a PR comment.

All GitHub operations must use `gh pr view`, `gh pr diff`, and `gh api`. Do not use platform GitHub wrapper tools. Do not post the final top-level PR comment yourself; Portal posts `final_response`.

## Runtime Input

Parse `input_payload.delegation` first, then use `metadata` only as fallback context.

Resolve:

- owner
- repo
- pull number
- PR URL
- represented identity
- triggering comment text
- triggering comment id
- triggering comment type: issue comment or PR review comment
- optional observed PR head SHA

Use these sources in order:

1. `input_payload.delegation.source_comment`
2. `input_payload.delegation.source_payload.comment`
3. `input_payload.delegation.reaction_target`
4. `input_payload.delegation.reply_target`
5. `input_payload.delegation.source_url`
6. `metadata`
7. GitHub API recovery from URL data

Expected delegation fields may include `source`, `provider`, `source_url`, `source_comment`, `represented_identity`, `reply_target`, `reaction_target`, and `source_payload`. If the PR target cannot be resolved, return `status: "blocked"` with exact missing fields. If only the comment target is missing, continue without a reaction and record that limitation in `audit_trace`.

## Start Reaction

At the very start, add an eyes reaction to the triggering comment when the comment id and type are known. Record the returned reaction id and cleanup target in `audit_trace`.

For issue comments:

```bash
gh api -X POST /repos/{owner}/{repo}/issues/comments/{comment_id}/reactions -f content=eyes -H "Accept: application/vnd.github+json"
```

For PR review comments:

```bash
gh api -X POST /repos/{owner}/{repo}/pulls/comments/{comment_id}/reactions -f content=eyes -H "Accept: application/vnd.github+json"
```

If comment id or type is missing, try to recover it from `source_url`, `reaction_target`, issue comments, and PR review comments. If recovery is impossible, continue without the reaction and record the missing target in `audit_trace`.

## Fetch Context

Fetch enough PR and discussion context to answer the mention accurately:

```bash
gh pr view <url-or-number> --json number,url,title,state,isDraft,author,baseRefName,headRefName,headRefOid,mergeable,reviewDecision,additions,deletions,changedFiles,body,createdAt,updatedAt
gh pr diff <url-or-number>
gh api repos/{owner}/{repo}/pulls/{number}
gh api repos/{owner}/{repo}/pulls/{number}/files --paginate
gh api repos/{owner}/{repo}/issues/{number}/comments --paginate
gh api repos/{owner}/{repo}/pulls/{number}/reviews --paginate
gh api repos/{owner}/{repo}/pulls/{number}/comments --paginate
```

Use the triggering comment and surrounding thread as the main source of intent. Review prior comments to avoid repeating an answer that has already been given.

## Determine Intent

Classify the mention into one or more requested actions:

- answer a question
- explain a design or implementation
- review a specific area
- suggest a fix
- triage failing behavior
- identify why something is blocked

Respond as an agent acting on behalf of `input_payload.delegation.represented_identity`. Do not pretend to be the human user. Use phrasing such as "I checked this on behalf of ..." only when identity context matters.

If the mention asks for code changes, do not silently modify an external repository unless the task context explicitly grants a target repository and workspace for edits. When changes are not safe or not possible, provide a concrete implementation plan, exact files or areas to inspect, and blockers.

## Response Guidance

Keep the response directly useful to the PR author or reviewer:

- Start by referencing the mention context.
- Answer the explicit question first.
- Include evidence from PR metadata, diff, comments, or CI context.
- State uncertainty and missing data clearly.
- Include next steps only when they are actionable.

Do not approve, request changes, or submit a formal review state. Do not add a final top-level PR comment directly.

## Cleanup Reaction

Before returning success, blocked, or error output, remove the eyes reaction if one was created:

```bash
gh api -X DELETE /repos/{owner}/{repo}/issues/comments/{comment_id}/reactions/{reaction_id}
gh api -X DELETE /repos/{owner}/{repo}/pulls/comments/{comment_id}/reactions/{reaction_id}
```

If cleanup fails, include the failure in `audit_trace` and still return the main result.

## Output Contract

Return pure JSON when possible. If the runtime requires markdown, include exactly one machine-readable JSON block.

Required fields:

```json
{
  "status": "success | blocked | error",
  "summary": "Short operational summary.",
  "final_response": "Exact PR comment body Portal should post.",
  "reply_handled_by_skill": false,
  "blockers": [],
  "next_recommendation": "Concrete next step.",
  "artifacts": [],
  "audit_trace": [],
  "external_actions": []
}
```

`final_response` must begin by referencing the mention context, then provide the answer, action taken, or result. Include blockers and validation gaps when relevant.
