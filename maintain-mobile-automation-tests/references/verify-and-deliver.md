# Verify and Deliver

Prove the fix before claiming it, then deliver a reviewable change or an evidence-backed findings report. Never report "fixed" without a verifying signal.

## 1. Local build gate (fast, cheap, do it first)

If the runtime image provides Maven (JDK 21 + Maven 3.9 are present in the OpenCode runtime image), at minimum confirm the change compiles before spending a Jenkins run:

```bash
cd <test-repo>
mvn -q -DskipTests test-compile        # compile test sources only
```

A compile failure here means the edit is wrong — fix it before pushing. Do not run the full device suite locally (it needs BrowserStack credentials and devices); the authoritative functional verification is the Jenkins re-run below. If the project uses Gradle, use its convention (`./gradlew compileTestJava`).

## 2. Commit to a fix branch

```bash
git checkout -b fix/<job>-<build>-<short-slug>
git add <only the files you changed>
git commit    # message links the evidence
```

Commit message should state: which scenario(s) failed, the classification, what drifted, and the Jenkins build + BrowserStack session that proved it. Example:

```
Fix login locator drift in <job> #<build>

Scenario "Successful login with valid credentials" failed with
NoSuchElementException on the login button. BrowserStack session
<id> app-source XML shows the button moved from id
com.app:id/btn_login to accessibility id "login-submit".
Updated LoginPage locator only; scenario intent unchanged.
```

Push the branch. Never commit secrets, evidence artifacts, or downloaded logs into the test repo.

## 3. Functional re-run through Jenkins (authoritative)

Trigger the suite on the fix branch and wait for the result:

```bash
# Trigger against the fix branch (param name is project-specific: BRANCH/GIT_BRANCH/branch).
jenkins job build-with-params <job> --param BRANCH=fix/<job>-<build>-<short-slug> --json
# The response carries a queue id; resolve it to a build number, then wait:
jenkins build wait <job> <new-build> --timeout-sec <suite-duration-seconds> --json
# Confirm the previously failing scenarios now pass and nothing regressed:
jenkins build test-report <job> <new-build> --json
```

Verification passes only when:
- the build result is `SUCCESS` (or the previously-failing scenarios are now `PASSED`), **and**
- `failure_count_total` did not grow with new, unrelated failures your change caused.

If the re-run still fails on the same scenario, the diagnosis or fix was wrong — return to Phase 2/3 with the new session's evidence. Bound this loop: do not blindly re-trigger more than a couple of times; if two evidence-driven attempts do not converge, stop and report what you learned.

Set `--timeout-sec` from the historical suite duration (roughly the failed build's duration plus margin), and never below the mobile suite's real runtime. If a full re-run is impractical, at least run the narrowed tag/scenario if the job supports a `TAGS`/`CUCUMBER_FILTER_TAGS` parameter.

## 4. Open the PR

Prefer the `create-pull-request` flow, or use `gh` directly (consistent with the delegation skills):

```bash
gh pr create --base <base> --head fix/<job>-<build>-<short-slug> \
  --title "Fix <scenario> locator drift (<job> #<build>)" \
  --body "<structured body below>"
```

PR body structure:

```markdown
## Why
<job> #<build> failed: <scenario(s)> — <exception summary>. Classified as test-script drift (locator/page/flow).

## Root cause
<what the app changed>, confirmed from BrowserStack session <id> app-source XML / Appium log.

## Change
<file>: <old locator/step> -> <new locator/step>. Scenario intent unchanged. (Or: `.feature` updated because the product flow genuinely changed — with rationale.)

## Verification
Re-ran <job> #<new-build> on this branch -> SUCCESS; previously failing scenario(s) now pass; no new failures.

## Notes
Platform parity: <checked iOS/Android mirror | n/a>. Secrets: none committed.
```

## 5. When no code change is correct (product bug / infra / data)

For class B/C/D where changing the test would be wrong, deliver a **findings report** instead of a PR, and leave the test failing (it is correctly catching the problem for B):

```markdown
## Finding: <product defect | infra | test-data/environment>
- Scenario: <name> in <job> #<build>
- Classification: <B product bug | C infra | D data/env>
- Evidence: <crash log excerpt | assertion expected-vs-actual + screenshot | network 5xx | capacity error> (BrowserStack session <id>)
- Why the test is not the fix: <the test correctly asserts the requirement / the environment failed, not the UI>
- Recommendation: <file product bug ticket X | retry build | rotate test account | correct capability/app build>
```

For a product bug, recommend filing/linking a Jira defect with the evidence; do not modify the assertion to match the bug.

## Delivery checklist

- [ ] Fix compiles locally (or compile step is genuinely unavailable — say so).
- [ ] Only intended files changed; no secrets, no artifacts, no unrelated churn.
- [ ] Jenkins re-run on the fix branch verifies the previously failing scenario(s) now pass with no new failures — build number cited.
- [ ] `.feature` intent preserved (or scenario-level change explicitly justified/confirmed).
- [ ] PR opened with the structured body, or a findings report delivered when no code change is correct.
- [ ] Final report follows the `skill.md` output contract.
