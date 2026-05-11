---
name: create-pull-request
description: Inspect git evidence, draft a pull request, and create it only when required fields are reliable
version: 1.0.0
owner: devops-team
triggers:
  - create pull request
  - create pr
  - open pr
  - /create-pull-request
tools:
  - git_clone
  - run_command
  - github_get_default_branch
  - github_create_pull_request
task_tools:
  - git_clone
  - run_command
when_to_use:
  - Use when the user asks to open a PR from current local repository work.
  - Use when the user asks to create/open a pull request for a specified git repo URL and branch.
  - Use when the request includes patterns like "in git repo <url> from branch <head> to <base>".
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
    git_clone: efp_git_clone
    run_command: efp_run_command
    github_get_default_branch: efp_github_get_default_branch
    github_create_pull_request: efp_github_create_pull_request
---

# Skill: create-pull-request

## Execution Contract (strict)
STEP 1: Execute phases in order. Do not skip steps.
STEP 2: Use `run_command` for local git inspection and prefer git evidence over assumptions.
STEP 3: Do not call `github_create_pull_request` before drafting PR content.
STEP 4: If required info is missing or ambiguous, ask the user instead of guessing.
STEP 5: Stop after either creating the PR or asking one blocking question.

## Phase 0 — Parse request and prepare repository
1. Parse from user input:
   - `repo_url`: substring after `git repo`
   - `head_branch`: substring after `from branch`
   - `base_branch`: substring after `to`
2. If `repo_url` is provided:
   - Call `git_clone(repo_url=<repo_url>, branch=<head_branch if provided>, dry_run=false)`.
   - If `git_clone` succeeds, read its `target_dir` and set `prepared_repo_path = <target_dir>`.
   - Use `prepared_repo_path` as cwd for all subsequent `run_command` calls.
   - Do not run repository checks from `/workspace` unless `/workspace` itself is the prepared repository.
   - If `git_clone` fails (clone/fetch/checkout), report the error and stop. Do not continue to PR creation.
3. If `repo_url` is not provided:
   - Use current workspace local repository flow.
   - Run `git rev-parse --is-inside-work-tree` in default workspace cwd first.
   - If not inside a git repo, ask one blocking question and stop.
4. If `head_branch` is provided:
   - `git_clone` should checkout `head_branch`.
   - In Phase 1, `git branch --show-current` must equal `head_branch`; mismatch is a blocker.
5. Base selection rules:
   - If `base_branch` is provided by the user, prioritize it and do not override user-provided base.
   - `github_get_default_branch` may be used as reference, but it must not replace an explicit user base like `to develop`.
   - If `base_branch` is missing, call `github_get_default_branch`; if unavailable, infer from `origin/HEAD` or common branches; if still unreliable, ask one blocking question.
6. Owner/repo inference rules:
   - Prefer parsing owner/repo from `repo_url` first.
   - Support `https://github.com/owner/repo(.git)` and `git@github.com:owner/repo(.git)`.
   - If parsing fails, fallback to `git remote -v` evidence in prepared repo.
   - If still ambiguous, ask one blocking question.

## Phase 1 — Check repository state
1. Confirm repository context with `git rev-parse --is-inside-work-tree`.
2. Get head branch with `git branch --show-current`.
3. Inspect working tree status with `git status --short`.
4. Inspect remotes with `git remote -v`.
5. Infer GitHub owner/repo only when clear; if ambiguous, ask user.

## Phase 2 — Collect change information
1. Gather summary with `git diff --stat`.
2. Gather changed files with `git diff --name-only`.
3. Review recent commits with `git log --oneline -5`.
4. If base is known, prefer comparison like `git diff --stat origin/<base>...HEAD`.
5. Inspect detailed per-file diffs only when needed.

## Phase 3 — Determine base branch
1. If user provided `base_branch`, keep it.
2. Otherwise prefer `github_get_default_branch` with `owner`, `repo`.
3. The tool may return formatted text: extract only raw branch name.
4. If unavailable, infer cautiously from strong repo evidence.
5. If base branch remains ambiguous, ask user and stop.

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
If anything critical is missing, ask one concise blocking question and stop.

## Phase 6 — Create PR or ask user
- If ready, call `github_create_pull_request`.
- Required args: `owner`, `repo`, `title`, `body`, `head`, `base`, `dry_run=false`.
- If tool returns existing/idempotent PR, treat as success and return PR URL.
- If permission is denied, report a permission blocker and do not claim PR was created.
- If GitHub API error occurs, return concise error summary plus prepared title/body; do not retry in an infinite loop.

## Prohibitions
- Do not use raw curl to create PRs.
- Do not ask for local checkout path when repo_url is provided.
- Do not use gh CLI as fallback for PR creation in this skill.
- Do not override user-provided base from repo default branch.

## Happy path example (must be executable)
Input:
`/create-pull-request in git repo https://github.com/dvnuo/engineering-flow-platform-portal from branch feature/20260504-opencode-integrated to develop`

Expected tool order:
1. `git_clone(repo_url="https://github.com/dvnuo/engineering-flow-platform-portal", branch="feature/20260504-opencode-integrated", dry_run=false)`
2. `run_command(cmd="git rev-parse --is-inside-work-tree", cwd=<target_dir>)`
3. `run_command(cmd="git branch --show-current", cwd=<target_dir>)`
4. `run_command(cmd="git status --short", cwd=<target_dir>)`
5. `run_command(cmd="git diff --stat origin/develop...HEAD", cwd=<target_dir>)` (or fallback)
6. `run_command(cmd="git diff --name-only origin/develop...HEAD", cwd=<target_dir>)` (or fallback)
7. `run_command(cmd="git log --oneline origin/develop..HEAD", cwd=<target_dir>)` (or fallback)
8. `github_create_pull_request(..., head="feature/20260504-opencode-integrated", base="develop", dry_run=false)`

## Local vs GitHub distinction
- Local inspection is performed with `run_command` using prepared repo cwd.
- GitHub PR creation requires explicit `owner` and `repo`.
- If remote parsing is unclear, ask user instead of guessing.
