# Triage Playbook: Jenkins → BrowserStack → Root Cause

Concrete command sequences for diagnosing a failed mobile automation build. Every command uses `--json`; read the `ok`/`data`/`error` envelope. Replace `<job>`, `<build>`, and ids with real values from prior output.

## 1. Confirm and characterize the Jenkins failure

```bash
# Did it actually fail, and what is the build URL?
jenkins build status <job> <build> --json

# Structured failing test cases (JUnit / Cucumber-JVM JUnit formatter).
jenkins build test-report <job> <build> --json
```

`build test-report` returns `failures[]` with `suite`, `class_name`, `name`, `error_details`, `error_stack_trace`, and `duration`; `failure_count_total` is the true count even if the returned list was capped by `--max-failures`. Read `error_details` / `error_stack_trace` to get the exception class and message per failing scenario.

If `has_report:false` (no test report was published — common when the Maven build failed to compile, or the reporter is not wired up), fall back to the console log:

```bash
jenkins build log <job> <build> --json
# For a long/streaming build, page the log:
jenkins build log-follow <job> <build> --max-rounds 5 --json
```

In the console log, look for:
- The failing scenario/step and the Cucumber failure block.
- The Java exception and stack trace (`NoSuchElementException`, `TimeoutException`, `StaleElementReferenceException`, assertion `expected:<...> but was:<...>`, `SessionNotCreatedException`, app crash).
- A **compile failure** (`BUILD FAILURE`, `COMPILATION ERROR`) — that is a source problem to fix directly, no BrowserStack session needed.
- BrowserStack dashboard URLs (`app-automate.browserstack.com/...`) or a `sessionId` / `session_id`, usually printed by the test's BrowserStack setup or an `onFail` hook.

## 2. Correlate the failure to its BrowserStack session

Preferred: a **shared build-name convention**. Many Jenkinsfiles set the BrowserStack `buildName` capability to something like `${JOB_NAME}-${BUILD_NUMBER}`. If so, list every session in that build regardless of outcome:

```bash
mobile-auto session candidates --build "<job-name>-<build-number>" --status "" --probe=false --json
```

`--status ""` removes the "running only" filter and `--probe=false` skips the live Appium controllability check — both are required because Jenkins sessions have already ended and are not live-controllable.

Fallback: parse a dashboard URL or raw session id out of the Jenkins console log, then:

```bash
mobile-auto session probe --from-url "<browserstack-dashboard-url>" --probe=false --json
# or
mobile-auto session probe --session-id "<hashed-session-id>" --probe=false --json
```

Map each failing Jenkins scenario to the BrowserStack session that ran it (by session name, which usually carries the scenario/test name, or by timestamp ordering within the build).

## 3. Pull the session evidence (post-mortem takeover)

Import the finished session into a local run so its artifacts can be collected, then diagnose:

```bash
mobile-auto run import --from-url "<dashboard-url>" --status "" --probe=false --json
# capture run_id from the response, then:
mobile-auto run diagnose --run-id <run-id> --collect-artifacts --out evidence --json
```

`run diagnose --collect-artifacts` downloads, when available: `appiumlogs`, `devicelogs`, `crashlogs`, `networklogs`, plus session video and the captured app source (page hierarchy XML) and screenshot. BrowserStack finalizes these only after the session ends, so a completed session's evidence is often more complete than a live one's.

Read, in order of signal for a drift diagnosis:
1. **Appium log around the failing step** — the exact locator strategy and value that was attempted, and the resulting error. This tells you precisely what the test looked for.
2. **App source XML / screenshot at failure** — the actual element hierarchy on screen at that moment. This is your source of truth for the **new** correct locator or the changed screen. Compare "what the test looked for" vs. "what was actually there".
3. **Crash log / device log** — if the app crashed or an ANR occurred (points toward a product bug, not test drift).
4. **Network log** — if a backend call failed (points toward environment/data, not the UI).

## 4. Optional live reproduction (only when needed to confirm a fix)

When post-mortem artifacts are not conclusive, or you want to confirm a new locator interactively before pushing, start a fresh live run on the same device/app:

```bash
mobile-auto run start --file <app-ref-or-.apk> --platform <android|ios> --device "<device>" --network public --json
mobile-auto observe --run-id <run-id> --json
mobile-auto locate --run-id <run-id> --role button --name "<label>" --json
mobile-auto tap --run-id <run-id> --ref <obs>:<el> --wait-change --post-observe --json
```

Rules: use only refs from the latest `observe`; re-observe after every mutating action; prefer action-level `--wait-visible` / `--wait-change` / `--wait-gone` over sleeps. Always `mobile-auto run finish --run-id <run-id> --status <passed|failed> --collect-artifacts --json` when done, and release any BrowserStack capacity you claimed.

## Correlation quick reference

| Jenkins signal | Likely class | Where to confirm |
|---|---|---|
| `NoSuchElementException` / `TimeoutException` waiting for element | test-script drift (locator/page) | Appium log + app source XML at failure |
| `StaleElementReferenceException` | drift (screen re-rendered) or timing | app source XML + step navigation |
| assertion `expected:<x> but was:<y>` | product bug OR intended change OR stale test data | app screenshot + network log + ticket |
| app crash / ANR in device/crash log | product bug | crash log + video |
| `SessionNotCreatedException` / device unavailable / capacity | infra | BrowserStack build metadata, retry |
| backend 4xx/5xx in network log | environment/data | network log + test config |
| `COMPILATION ERROR` / `BUILD FAILURE` before tests ran | source problem | Jenkins log only (no session) |
