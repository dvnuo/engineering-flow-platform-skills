---
name: maintain-mobile-automation-tests
description: "Diagnose a failing Jenkins-run mobile automation suite (Java + Cucumber + BrowserStack), take over the BrowserStack session to find root cause, and repair the test scripts while preserving scenario intent. Use when: a mobile automation Jenkins build fails, a mobile test needs fixing after a UI/locator/page change, or the user asks to maintain/repair mobile automation tests."
version: 1.0.0
owner: qa-platform
triggers:
  - /maintain-mobile-tests
  - maintain mobile automation tests
  - fix mobile automation test
  - repair mobile automation test
  - mobile test failed in jenkins
  - jenkins mobile test failure
  - browserstack test failure
  - fix failing cucumber mobile test
output_format: markdown
references:
  - references/triage-playbook.md
  - references/failure-taxonomy.md
  - references/repair-patterns.md
  - references/verify-and-deliver.md
opencode:
  execution_kind: prompt_only
  compatibility: full
  permission:
    default: ask
  capability_tags:
    - prompt-only
    - jenkins
    - browserstack
    - mobile-automation
    - cucumber
    - test-maintenance
    - long-running
---

# Maintain Mobile Automation Tests

Diagnose and repair a mobile automation suite (Java + Cucumber + Appium on BrowserStack, run by Jenkins) when a build fails, while preserving the intent of each test scenario. Every decision must be grounded in evidence — Jenkins logs, the Jenkins test report, and the BrowserStack session's device/Appium logs, app source, and screenshots — never in a guess about what an element or page "probably" is now.

This skill is a long-running maintenance loop, not a one-shot generator. It is safe to run from a chat message, an async task, or a delegation. Work in phases and stop at the first genuine blocker or after delivering a fix.

## Tooling

Invoke the EFP CLIs through the runtime shell (`bash`). They are terminal binaries in the runtime image, not model function tools. Always pass `--json` and read the `ok` / `data` / `error` envelope.

- `jenkins ...` — build trigger, status, console log, `build test-report`, `build wait`, artifacts. See its `jenkins help llm --json` and `jenkins schema <command> --json`.
- `mobile-auto ...` — BrowserStack App Automate session takeover, `observe`, `locate`, actions, `run diagnose`. See `mobile-auto commands --json` and `mobile-auto schema <command> --json`.
- `git` / `gh` — inspect the test repo, branch, commit, and open a PR.
- `mvn` (Maven 3.9+, JDK 21) — compile/validate the Java test module locally before pushing when the runtime image provides it.

Never invent an element locator, a Jenkins path, or a BrowserStack session id. Resolve each from a real command output.

## Golden rule: preserve scenario intent

The `.feature` Gherkin describes **business intent** (what the user is trying to do). The step definitions, page objects, and locators describe **how** the app currently exposes that intent.

- When the app UI drifts (an element id/text/position changed, a screen was restructured, an extra step was inserted) but the scenario is still valid → **adapt the implementation** (locator, step glue, wait, navigation) and keep the Gherkin intent intact.
- Only change the `.feature` file itself when the **business flow genuinely changed** (a step no longer exists in the product, a new required step was added to the real user journey). Note this explicitly and prefer confirmation for scenario-level changes.
- Never make a test pass by weakening an assertion, adding a blanket sleep, catching-and-ignoring, or deleting a scenario, unless the user explicitly asks. A test that passes without verifying the intent is worse than a failing one.
- If the failure is a **real product bug** (the app is wrong, the test is right), do **not** rewrite the test to match the bug. Report it as a product defect with evidence.

## Phase 0 — Resolve inputs

Resolve, defensively, from the user message / task payload:

- `jenkins_job` (folder path) and `build` number (or `lastBuild` / `lastFailedBuild`).
- The **test repository** (git URL + branch) that holds the Cucumber/Java suite. If the runtime prepared a repo path, use it; otherwise clone with `git`.
- Optionally: a specific failing scenario/tag, a BrowserStack build-name convention, or a Jira ticket for context.

If neither a Jenkins build nor a concrete failing test is resolvable, ask **one** blocking question and stop.

## Phase 1 — Triage from Jenkins

Follow `references/triage-playbook.md`. In short:

1. `jenkins build status <job> <build> --json` — confirm it actually failed and get the result/URL.
2. `jenkins build test-report <job> <build> --json` — get failing scenario names, error messages, and stack traces directly. If `has_report:false`, fall back to `jenkins build log <job> <build> --json` and scan for the failing scenario, the exception, and BrowserStack dashboard URLs / session ids.
3. Extract, per failure: the scenario/step that failed, the exception type and message (for example `NoSuchElementException`, timeout, assertion mismatch, app crash), and the BrowserStack session reference.

## Phase 2 — Classify the failure

Before touching any file, classify each failure using `references/failure-taxonomy.md`:

- **Test-script drift** — locator/page/flow changed, scenario still valid → repair the implementation (most common maintenance case).
- **Genuine product bug** — app behaves incorrectly, test is right → report defect, do not "fix" the test.
- **Infra / flakiness** — device allocation, network, BrowserStack capacity, session timeout, transient wait → recommend retry and/or a targeted robustness fix; do not change scenario logic.
- **Test data / environment** — bad credentials, stale test data, wrong build/app version, wrong capabilities → fix config/data, not the scenario.

Misclassification is the most damaging error here — spend the evidence to get it right.

## Phase 3 — Take over the BrowserStack session for root cause

Only for failures where the Jenkins log/test-report is not conclusive (typically drift and product-bug candidates). Follow `references/triage-playbook.md`:

- The Jenkins-run session has **ended**, so use the **post-mortem** takeover shape: `mobile-auto run import --from-url <dashboard-url> --status "" --probe=false --json` (or `--session-id` / `--build <name>`). `--status "" --probe=false` is required because a finished session is neither "running" nor live-controllable.
- `mobile-auto run diagnose --run-id <run> --collect-artifacts --out evidence --json` — pull device logs, Appium logs, crash logs, network logs, session video, and the captured app source/screenshot at failure.
- Read the Appium log around the failing step to see exactly which locator strategy was attempted and what the page hierarchy actually contained. That XML/screenshot is your source of truth for the **new** correct locator — do not guess it.
- If a **live** reproduction on a fresh device is warranted (to confirm a fix interactively), start a new run with `mobile-auto run start ...`, then `observe` / `locate` / act. Re-observe after every mutating action. This is optional and heavier; prefer post-mortem artifacts first.

## Phase 4 — Repair

Follow `references/repair-patterns.md`. Work one file at a time, keep each change minimal and reviewable:

1. Locate the offending code: the step definition, page object, or locator constant behind the failing Gherkin step.
2. Apply the smallest change that restores the scenario's intent using the evidence from Phase 3 (new locator, adjusted navigation, explicit wait for the real readiness signal, corrected data).
3. Keep platform parity in mind: if a locator changed on Android, check whether the iOS implementation needs the mirror change.
4. Leave a short comment explaining what drifted and when, and reference the Jenkins build / BrowserStack session in the commit message.

## Phase 5 — Verify and deliver

Follow `references/verify-and-deliver.md`:

1. If Maven is available, compile the test module locally (`mvn -q -DskipITs test-compile` or the project's convention) so the change at least builds before pushing.
2. Commit to a fix branch with an evidence-linked message.
3. Re-run the suite through Jenkins to confirm the fix: `jenkins job build-with-params <job> --param BRANCH=<fix-branch> ... --json`, then `jenkins build wait <job> <new-build> --timeout-sec <suite-duration> --json`, then `jenkins build test-report <job> <new-build> --json` and confirm the previously failing scenarios now pass and nothing regressed.
4. Open a PR with `gh` (or the create-pull-request flow), summarizing: which scenarios failed, the root-cause classification, what drifted, the exact change, and the verifying build number.
5. For product-bug / infra / data classifications where no test change is correct, deliver a findings report instead of a code change, with the evidence and a concrete recommendation.

## Output contract

End with a concise markdown report:

```markdown
## Failing build
<job> #<build> — <result> — <jenkins url>

## Failures triaged
- <scenario> — <classification> — <one-line root cause>

## Changes made
- <file>: <what drifted → what changed>   (or "None — see findings")

## Verification
- Re-run: <job> #<new-build> — <result>
- Previously failing scenarios: <pass/fail>

## Product/infra findings (if any)
- <defect or infra issue> — <evidence> — <recommendation>

## PR
- <url or "not applicable">
```

## Stop conditions

- Root cause cannot be determined from Jenkins + BrowserStack evidence → stop with a precise blocker and the evidence gathered.
- The correct fix is a scenario-level change to the real user journey → prefer confirmation before rewriting `.feature` intent.
- Failure is a genuine product bug → report it; do not alter the test to pass.
- BrowserStack session or artifacts are unavailable / expired → report what is missing and what to re-capture.
