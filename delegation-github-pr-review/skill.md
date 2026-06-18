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

Use this skill for an `agent_async_task` created from a `github_pr_review` Portal Delegation. The task represents a GitHub user who was directly requested as a pull request reviewer. Perform a concise, high-signal review, post line-specific findings as inline PR comments where practical, and return the final review body in `final_response` for Portal to post as a PR comment.

All GitHub reads and inline review comment writebacks must use the GitHub CLI: `gh pr view`, `gh pr diff`, and `gh api`. Do not use platform GitHub wrapper tools. Do not approve the PR, request changes, submit a formal GitHub review state, or post the final top-level PR comment yourself.

Portal owns start feedback and final reply delivery. Portal adds/removes the PR start reaction and posts the final PR comment from `final_response`; return `reply_handled_by_skill: false`. The skill must not add/remove Portal-owned reactions, post the final PR comment, or create/update Portal-owned status comments.

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

## Portal-Owned Start Feedback

Do not create start feedback or reactions. `input_payload.delegation.reaction_target` may be present for Portal-owned feedback, but the skill should only record relevant context and continue with the review. Portal owns the PR start reaction lifecycle.

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
2. Return `status: "blocked"`.
3. Set `final_response` to explain that the PR changed since the delegation event and should be re-queued for the current head SHA.
4. Include both the observed SHA and current SHA in `audit_trace` when available.

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

## Inline Comment Writeback

Inline comments are the preferred/default writeback for line-anchorable findings. Any finding tied to a changed line should normally be posted as an inline PR comment with `gh api` so the author can find it at the relevant diff hunk.

Use inline comments for actionable correctness, security, reliability, compatibility, migration, testing, or maintainability findings that can be anchored to a changed line. Do not spam low-value style comments, but do not hide actionable line-specific findings only in `final_response`.

Create inline comments with the PR head SHA and the changed file path/line from the diff:

```bash
gh api -X POST /repos/{owner}/{repo}/pulls/{number}/comments \
  -f body="$comment_body" \
  -f commit_id="$head_sha" \
  -f path="$path" \
  -F line="$line" \
  -f side=RIGHT
```

For multi-line findings, use the GitHub PR review comment fields for a line range when the range is precise and supported by the diff. Anchor to `side=RIGHT` for changed lines in the PR head; use `side=LEFT` only when the issue can only be anchored to removed/base-side code.

Try to include a GitHub suggestion block when the fix is small, precise, syntactically valid, and can be applied directly on the commented line or selected range:

````markdown
```suggestion
replacement code
```
````

Do not include a suggestion block if the fix is uncertain, requires broader design decisions, spans unrelated code, or cannot be represented safely for the selected line/range. If no suggestion block is safe, still include concrete fix guidance in the inline comment.

Record every inline comment write in `external_actions` with at least:

- endpoint
- path
- line or line range
- severity
- summary
- `suggestion_provided: true|false`

The final `final_response` should summarize review scope, list posted inline comments, and include only broad/non-line-anchorable findings or validation gaps. Avoid duplicating the full inline comment bodies unless needed for context.

Do not add broad final comments, approval reviews, or request-changes reviews. Inline review comments are not the final reply; Portal delivers the final PR comment from `final_response`.

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

## Inline Comments Posted

## Broad Findings

### Blocking

### Important

### Suggestions

## Validation Gaps

## Overall Assessment
```

If there are no findings in a severity group, write `None found.` for that group. Keep the final response useful to the PR author and reviewers.
