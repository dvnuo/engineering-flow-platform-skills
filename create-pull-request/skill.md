---
name: create-pull-request
description: Inspect local or runtime-prepared git evidence, draft a pull request, and create it only when repository, branch, and PR fields are reliable
version: 1.0.0
owner: devops-team
triggers:
  - create pull request
  - create pr
  - open pr
  - /create-pull-request
tools:
  - run_command
  - github_get_default_branch
  - github_create_pull_request
task_tools:
  - run_command
when_to_use:
  - Use when the user asks to open a PR from current local repository work.
  - Use when the user provides a GitHub repository URL plus source and target branches for PR creation.
  - Use when PR content should be grounded in local git evidence before creation.
references:
  - ref-template.md
model: ""
opencode:
  execution_kind: prompt_only
  compatibility: degraded
  permission:
    default: ask
  capability_tags:
    - prompt-only
    - tools-required
  tool_mappings:
    run_command: efp_run_command
    github_get_default_branch: efp_github_get_default_branch
    github_create_pull_request: efp_github_create_pull_request
---

# Skill: create-pull-request

## Repository input modes

This skill supports two repository modes:

1. Current local repository mode:
   - Use the current working directory only when it is a git work tree.

2. Runtime-prepared repository mode:
   - If the runtime prompt says "Repository has been prepared at: <path>", all local git inspection commands MUST run from that path.
   - Do not run git inspection from `/workspace` unless `/workspace/.git` exists.
   - Do not ask where the local checkout is mounted when the user already provided `in git repo <url>` and the runtime provided a prepared path.

## Repository preparation expectations

- If the user provides `in git repo <url> from branch <head> to <base>`, prefer the runtime-prepared repository path injected by the adapter.
- If a prepared path is not provided and the runtime has not checked out the repo, ask one blocking question only if local checkout information is truly required.
- Do not invent a local checkout path.
- Do not use raw curl or ungoverned API calls to create the PR.

## Execution Contract (strict)
STEP 1: Execute phases in order. Do not skip steps.
STEP 2: Use `run_command` for local git inspection, and when a prepared repo path is provided all local git inspection commands must run from that path.
STEP 3: Do not call `github_create_pull_request` before drafting PR content.
STEP 4: If the user provided source/base branch explicitly, do not override them with `github_get_default_branch`.
STEP 5: `base` is required before PR creation.
STEP 6: If `github_create_pull_request` / `efp_github_create_pull_request` is unavailable, stop and report the exact missing tool blocker. Do not use raw curl.
STEP 7: Stop after either creating the PR or asking one blocking question.

## Phase 1 — Check repository state
1. Determine repository working directory:
   - If runtime provided "Repository has been prepared at: <path>", use that path for all local git inspection commands.
   - Otherwise use current working directory only if it is a git work tree.
2. Confirm repository context with `cd "$REPO_DIR" && git rev-parse --is-inside-work-tree`.
3. Get head branch with `cd "$REPO_DIR" && git branch --show-current`.
4. Inspect working tree status with `cd "$REPO_DIR" && git status --short`.
5. Inspect remotes with `cd "$REPO_DIR" && git remote -v`.
6. Infer GitHub owner/repo from remotes only when clear; if ambiguous, ask user.

## Phase 2 — Collect change information
1. Gather summary with `cd "$REPO_DIR" && git diff --stat`.
2. Gather changed files with `cd "$REPO_DIR" && git diff --name-only`.
3. Review recent commits with `cd "$REPO_DIR" && git log --oneline -5`.
4. If base is known, prefer comparison like `cd "$REPO_DIR" && git diff --stat "origin/<base>...HEAD"`.
5. Inspect detailed per-file diffs only when needed.
6. If user specified `from branch <head>`, treat that head branch as authoritative from user/runtime preflight context.
7. If current checked-out branch does not match explicit `<head>`, report blocker and stop without creating PR.
8. If base branch was explicitly provided as `to <base>`, do not call `github_get_default_branch` to override it.

## Phase 3 — Determine base branch
1. Use user explicit `to <base>` from slash command/runtime context first.
2. Otherwise use runtime-prepared context base branch when provided.
3. Otherwise infer from strong local repository evidence.
4. Call `github_get_default_branch` only when base was not explicitly provided and still cannot be resolved from runtime/local evidence.
5. If base branch remains ambiguous, ask one blocking question and stop.
6. Never override user-specified `to <base>` with a default branch result (for example, do not replace `develop` with `master`).
7. Do not pass formatted markdown text as branch name.
8. Do not guess `main` when base is missing.

## Phase 4 — Draft PR content (required before PR creation)
Prepare these sections first:
- PR Title
- Base Branch
- Head Branch
- Summary
- Files/Areas Changed
- Testing
- Risks / Notes

## Phase 5 — Validate required fields
Do not create PR unless all are reliable:
- repository owner
- repository name
- base branch
- head branch/current branch
- PR title
- PR body
If workspace is dirty, PR can still proceed from committed branch history, but note uncommitted changes in Risks / Notes.
If head branch identity is not reliable, stop and ask one concise blocking question.
If anything critical is missing, ask one concise blocking question and stop.

## Phase 6 — Create PR or ask user
- If ready, call `github_create_pull_request`.
- Required args are `owner`, `repo`, `title`, `body`, `head`, `base`, `dry_run: false`, `idempotency_key`.
- Use `idempotency_key` format: `create-pr:<owner>/<repo>:<head>:<base>`.
- If runtime permission policy denies write access, report permission blocker and stop.
- If no diff is found for `origin/<base>...HEAD`, ask user whether to proceed instead of creating an empty PR.

## Failure paths (must be explicit)
- Missing repository context:
  - If user did not provide repository URL and current directory is not a git repo, ask one blocking question for local checkout path.
  - If user provided repository URL but runtime checkout/prepared path is missing or failed, report checkout blocker and stop (do not ask for local checkout path).
- Missing create-PR tool:
  - Report `github_create_pull_request` / `efp_github_create_pull_request` unavailable.
  - Do not use raw curl.
  - Do not claim PR was created when only draft text exists.
- Permissions denied:
  - Report write permission denied.
  - Do not bypass permission controls.

## Local vs GitHub distinction
- Local inspection is performed with `run_command`.
- GitHub PR creation requires explicit `owner` and `repo`.
- If remote parsing from `git remote -v` is unclear, ask user instead of guessing.
