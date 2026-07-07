# Jenkins Evidence Collection Playbook

Goal: from a job (and optionally build number), extract everything needed to triage
without re-running anything. Always `--json`; never guess URLs when a command exists.

## 1. Resolve the build

```bash
jenkins build status <job> lastCompletedBuild --json     # newest finished build + result
jenkins build status <job> <build> --json                # specific build
jenkins pipeline runs <job> --json                       # recent runs overview (pipeline jobs)
```

Record: build number, result, timestamp, changeset/app version parameters.

## 2. Locate the failing stage and log slice

```bash
jenkins pipeline stages <job> <build> --json             # find the failing stage id
jenkins pipeline node-log <job> <build> <node-id> --json # stage-scoped log (preferred)
jenkins build log <job> <build> --json                   # full console as fallback
```

In the log, extract (in this priority):

1. Cucumber scenario + step lines around the failure (`Scenario:` / step keywords).
2. The Java exception and the FIRST stack frame inside the test package — that frame
   is the file:line you will repair.
3. The BrowserStack session URL/id. Common shapes:
   `https://app-automate.browserstack.com/dashboard/v2/builds/<build-hash>/sessions/<session-id>`
   or a log line containing `sessionId`. Collect every session id near the failure.
4. App build/version under test (apk/ipa id, `bs://` app id, or version parameter).

## 3. Structured test reports

JUnit (if the job publishes it):

```bash
jenkins api get /job/<job-path>/<build>/testReport/api/json --query "tree=suites[cases[className,name,status,errorDetails,errorStackTrace]]" --json
```

Note: nested folders need `/job/` between each segment in raw API paths
(`folder/app` → `/job/folder/job/app`).

Cucumber JSON / HTML reports and screenshots are usually archived artifacts:

```bash
jenkins build artifacts <job> <build> --json
jenkins artifact download <job> <build> <path/to/cucumber.json> --output cucumber.json --json
```

`cucumber.json` gives exact step status, embedded screenshots, and durations —
prefer it over console parsing when available.

## 4. Differential context (was it ever green?)

```bash
jenkins build status <job> lastSuccessfulBuild --json
```

Compare parameters (app version!) between the last green and the failing build.
A failure that starts exactly at an app version bump is strong evidence of
locator/flow drift; a failure with unchanged app version points at environment,
data, or flakiness.

## 5. Evidence bundle

Keep a working note (used later in the PR body):

- job / build / result / when
- failing scenario(s) + step
- exception + test-code frame (file:line)
- BrowserStack session id(s) + app id/version
- last green build + what changed between
