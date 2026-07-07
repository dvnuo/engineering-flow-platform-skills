---
name: mobile-auto-test-maintenance
description: "Diagnose and repair failing mobile automation tests (Jenkins + Cucumber/Java + BrowserStack). Fetches Jenkins evidence, takes over or replays BrowserStack sessions, classifies the failure, adapts the test code to app changes without changing scenario intent, verifies, and opens a PR. Use when: a Jenkins mobile test job failed, a cucumber scenario is flaky/broken, or a locator/page changed in the app."
version: 1.0.0
owner: qa-platform
triggers:
  - "fix mobile tests"
  - "mobile test maintenance"
  - "jenkins mobile test failed"
  - "repair automation script"
  - "/fix-mobile-tests"
  - jira_assignee
  - timer
tools:
  - run_command
  - git_clone
  - git_commit
  - git_push
  - github_create_or_update_file
  - github_get_file_content
planning_mode: required
execution_style: stepwise
ask_user_policy: blocked_only
output_format: markdown
references:
  - references/jenkins-evidence.md
  - references/failure-triage.md
  - references/browserstack-session-takeover.md
  - references/repair-patterns.md
opencode:
  execution_kind: prompt_only
  compatibility: full
  permission:
    default: ask
  capability_tags:
    - prompt-only
    - tools-required
    - qa-maintenance
    - jenkins
    - browserstack
    - long-running
  tool_mappings:
    run_command: efp_run_command
    git_clone: efp_git_clone
    git_commit: efp_git_commit
    git_push: efp_git_push
    github_create_or_update_file: efp_github_create_or_update_file
    github_get_file_content: efp_github_get_file_content
---

# Mobile Auto Test Maintenance

Maintain an existing mobile automation suite (Jenkins + Java + Cucumber + BrowserStack)
when the app changes but the test scenarios do not. The `jenkins` and `mobile-auto`
CLIs are available through Bash; always pass `--json` and inspect the `ok/data/error`
envelope.

## Prime Directives

1. **Scenario intent is immutable.** You adapt the implementation (locators, waits,
   navigation steps, page objects) to the app; you never weaken, delete, or skip a
   scenario to make it pass. If the scenario itself no longer matches the product,
   stop and report — that is a requirements decision, not maintenance.
2. **A real app bug is not a test bug.** If evidence shows the app misbehaving,
   do NOT change the test. Report the defect with evidence (see Deliverables).
3. **Every repair needs evidence.** Never patch a locator based on guesswork; base
   changes on an `observe` snapshot, Appium page source, or session logs that show
   the current UI.
4. **Respect session ownership.** Import someone else's BrowserStack session only to
   observe and diagnose. Never `run finish` a session you imported unless the run is
   clearly abandoned or the requester told you to. Prefer starting your own session
   for interactive repair experiments.
5. **Bounded blast radius.** Change only the files the failure implicates. Never
   reformat, upgrade dependencies, or refactor unrelated code in a maintenance PR.

## Inputs (multiple entry points)

Resolve context in this order; ask only if truly ambiguous (`ask_user_policy: blocked_only`):

- **Chat / slash command**: a Jenkins job path + build number, a Jenkins URL, a
  BrowserStack session id/URL, or "the latest failure of <job>".
- **Delegation (`jira_assignee` / `timer`)**: parse `input_payload.delegation` for a
  Jira issue that references a Jenkins build or job; for timer delegations, the rule
  conditions name the Jenkins job(s) to watch — check the most recent completed build
  and exit cleanly with "no action needed" if it passed.
- **Missing pieces**: if only a job is known, use `jenkins build status <job> lastCompletedBuild --json`
  to find the newest failure. If only a BrowserStack session is known, work backward
  from its logs to the feature/scenario.

Identify the test repository from the Jenkins job config (`jenkins api get /job/<job>/config.xml`),
the Jira issue, or user input. Clone/checkout it in the workspace before repair.

## Workflow

Work phase by phase; announce each phase transition briefly. Long-running phases
(builds, device sessions) are normal — do not abandon a phase because it is slow.

### Phase 1 — Collect Jenkins evidence

Follow `references/jenkins-evidence.md`. Outcome: the failing scenario(s), the failing
step, the exception + stack frame in test code, the BrowserStack session id(s), and
downloaded artifacts (junit/cucumber reports, screenshots).

### Phase 2 — Triage the failure

Classify using `references/failure-triage.md` into exactly one primary class:

| Class | Typical signal | Action |
|---|---|---|
| Locator drift | NoSuchElement / stale ref, app version bumped | Repair locator |
| Flow drift | Element exists but flow changed (new screen, moved button, changed onboarding) | Repair steps/page objects |
| Timing/flakiness | Intermittent waits, works on retry | Strengthen waits, not sleeps |
| Environment/infra | BrowserStack/network/app upload/Jenkins node errors | No code change; report + optionally re-run |
| App defect | App crash, wrong behavior vs. scenario | No code change; file defect report |
| Test data | Expired accounts, seed data drift | Fix data/config, not logic |

If evidence is insufficient to classify, go to Phase 3 before deciding.

### Phase 3 — Live device evidence (when needed)

Follow `references/browserstack-session-takeover.md`.

- Session still running → `session candidates/probe` → `run import --probe` →
  `run guard` → `run diagnose` → `observe`. Read-only unless clearly abandoned.
- Session finished → `run diagnose` on the imported session collects device logs,
  Appium logs, and video metadata; then start a fresh session (`run start`) with the
  same app build to reproduce: replay the failing scenario's steps manually with
  `observe`/`locate`/`tap`/`type` until the point of failure, and capture the current
  page source at that point — this is your ground truth for the new locator/flow.

### Phase 4 — Repair

Follow `references/repair-patterns.md`. Locate the failing step definition and page
object from the stack frame; map the observed UI (Phase 3) onto the repair pattern.
Keep Gherkin untouched unless the flow drift genuinely adds/removes a user-visible
step — in that case change the minimum wording and call it out in the PR.

### Phase 5 — Verify (layered, cheapest first)

1. **Compile**: `mvn -q -pl <module> test-compile` (or the repo's build command).
2. **Targeted replay**: re-drive the repaired steps on a fresh BrowserStack session
   with `mobile-auto` (observe → act → assert) OR run the single scenario locally if
   the repo supports it: `mvn test -Dcucumber.filter.tags="@<ticket-or-tag>"`.
3. **CI proof**: trigger the Jenkins job for the branch/scenario when parameters
   allow: `jenkins job build-with-params <job> --param BRANCH=<fix-branch> --param TAGS=@<tag> --json`,
   then `jenkins build log-follow` until the verdict. If the job cannot run a subset,
   state that in the PR and rely on step 2 evidence.

Never claim success without at least step 2 or 3 passing.

### Phase 6 — Deliver

- Commit on a branch named `fix/mobile-tests/<job-or-ticket>-<short-slug>`; open a PR.
- PR body must contain: failure class, root cause, evidence (Jenkins build link,
  BrowserStack session link, before/after locator or flow), verification performed,
  and anything intentionally NOT fixed.
- For delegation tasks, `final_response` is the Portal-owned status body: summarize
  class → cause → fix → verification → PR link. Return `reply_handled_by_skill: false`.
- **App defect / environment outcomes**: no PR; deliver the defect/infra report with
  evidence instead, and say explicitly that the test code was intentionally unchanged.
- Always `run finish` your own sessions (`--collect-artifacts` when diagnostics
  matter) and `run release` any imported claim, even on failure paths.

## Blockers

Treat these as blockers (report the exact command + error; do not improvise setup):
missing `jenkins`/`mobile-auto` credentials, no access to the test repository,
BrowserStack plan limits, or a Jenkins job that requires parameters you cannot infer.
