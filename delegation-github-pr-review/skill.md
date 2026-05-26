---
name: delegation-github-pr-review
description: Handle long-running GitHub pull request review delegations created when the represented GitHub user is requested as a reviewer.
version: 1.0.0
owner: engineering-flow-platform
triggers:
  - github_pr_review
  - delegation github pr review
  - review requested delegation
  - pull request review delegation
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
    - pull-request-review
    - long-running
---

# Delegation GitHub PR Review

Use this skill for an `agent_async_task` created from a `github_pr_review` Portal Delegation. The task represents a GitHub user who was directly requested as a pull request reviewer. Perform a concise, high-signal review and return the final review body for Portal to post as a PR comment.

All GitHub reads and optional writes must use the GitHub CLI: `gh pr view`, `gh pr diff`, and `gh api`. Do not use platform GitHub wrapper tools. Do not approve the PR, request changes, submit a formal GitHub review state, or post the final top-level PR comment yourself. Portal posts `final_response`.

## Runtime Input

Parse the runtime JSON from `input_payload.delegation` first. Treat missing fields defensively and use `metadata` only as fallback context.

Resolve these values before reviewing:

- owner
- repo
- pull number
- PR URL
- represented identity
- observed head SHA, when available

Resolution order:

1. `input_payload.delegation.reply_target`
2. `input_payload.delegation.source_payload`
3. `input_payload.delegation.source_url`
4. `metadata`
5. GitHub API recovery from the URL or PR number

Expected delegation fields may include `source`, `provider`, `source_url`, `source_comment`, `represented_identity`, `reply_target`, `reaction_target`, and `source_payload`. If the target PR cannot be resolved after recovery, return `status: "blocked"` with a precise blocker in `blockers` and a `final_response` explaining what context is missing.

## Start Reaction

At the very start, add an eyes reaction and record the returned reaction id and cleanup endpoint in `audit_trace`.

Prefer `input_payload.delegation.reaction_target`. If the event has no triggering comment, react to the PR issue itself:

```bash
gh api -X POST /repos/{owner}/{repo}/issues/{pull_number}/reactions -f content=eyes -H "Accept: application/vnd.github+json"
```

Supported reaction targets:

- PR issue: `/repos/{owner}/{repo}/issues/{pull_number}/reactions`
- issue comment: `/repos/{owner}/{repo}/issues/comments/{comment_id}/reactions`
- PR review comment: `/repos/{owner}/{repo}/pulls/comments/{comment_id}/reactions`

If adding the reaction fails, continue the review and add the failure details to `audit_trace`. Never let a reaction failure hide the review result.

## Fetch Context

Fetch enough PR context with `gh` before forming conclusions. Use the PR URL if available; otherwise use the pull number with `-R {owner}/{repo}`.

```bash
gh pr view <url-or-number> --json number,url,title,state,isDraft,author,baseRefName,headRefName,headRefOid,baseRefOid,mergeable,reviewDecision,additions,deletions,changedFiles,createdAt,updatedAt,body
gh pr diff <url-or-number>
gh api repos/{owner}/{repo}/pulls/{number}
gh api repos/{owner}/{repo}/pulls/{number}/files --paginate
gh api repos/{owner}/{repo}/issues/{number}/comments --paginate
gh api repos/{owner}/{repo}/pulls/{number}/reviews --paginate
gh api repos/{owner}/{repo}/pulls/{number}/comments --paginate
```

Inspect prior comments and reviews before writing findings. Avoid repeating concerns that are already raised unless the existing discussion is incomplete or wrong.

## Freshness Gate

Before reviewing, compare the observed head SHA from `input_payload.delegation.source_payload`, `input_payload.delegation.reply_target`, or `metadata` with the current PR head SHA from `gh pr view` or `gh api repos/{owner}/{repo}/pulls/{number}`.

If the PR head changed:

1. Do not perform a stale review.
2. Remove the eyes reaction if one was added.
3. Return `status: "blocked"`.
4. Set `final_response` to explain that the PR changed since the delegation event and should be re-queued for the current head SHA.
5. Include both the observed SHA and current SHA in `audit_trace` when available.

## Review Method

Review priorities, in order:

1. correctness
2. security
3. reliability
4. backward compatibility / API contract safety
5. data migrations and rollout risk
6. test coverage gaps
7. maintainability
8. style only when it affects meaning, readability, or safety

Prefer fewer, high-impact findings over noisy comments. A good result may contain no findings if the diff is sound; still report review focus and validation gaps.

For each finding, include:

- severity: `blocking`, `important`, or `suggestion`
- file and line if available
- issue
- why it matters
- suggested fix

Do not speculate. If the diff lacks enough context, fetch the surrounding file from the PR head or state the uncertainty explicitly.

## Optional Inline Comments

Normally return only `final_response` and let Portal post the final PR comment. If you choose to add inline review comments through `gh api`, only do so for precise, line-anchorable issues. Record every inline write in `external_actions`, including endpoint, path, line, and summary.

Do not add broad final comments, approval reviews, or request-changes reviews.

## Cleanup Reaction

Before returning success, blocked, or error output, remove the eyes reaction if one was created.

```bash
gh api -X DELETE /repos/{owner}/{repo}/issues/{pull_number}/reactions/{reaction_id}
gh api -X DELETE /repos/{owner}/{repo}/issues/comments/{comment_id}/reactions/{reaction_id}
gh api -X DELETE /repos/{owner}/{repo}/pulls/comments/{comment_id}/reactions/{reaction_id}
```

Use the deletion endpoint that matches the reaction target. If cleanup fails, include the failure in `audit_trace` and still return the main task result.

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

`final_response` must be markdown with this structure:

```markdown
## PR Summary

## Review Focus

## Findings

### Blocking

### Important

### Suggestions

## Validation Gaps

## Overall Assessment
```

If there are no findings in a severity group, write `None found.` for that group. Keep the final response useful to the PR author and reviewers.
