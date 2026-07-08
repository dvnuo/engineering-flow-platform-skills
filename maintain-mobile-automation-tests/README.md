# Maintain Mobile Automation Tests

Diagnose and repair a failing mobile automation suite (Java + Cucumber + Appium on BrowserStack, run by Jenkins) while preserving each scenario's business intent.

This is the maintenance counterpart to `mobilex-test-cases-generator` (which creates the tests): this skill keeps an existing suite green as the app under test drifts.

## What it does

Given a failed Jenkins mobile-automation build (or a direct request to fix a mobile test), the agent:

1. **Triages** from Jenkins — `jenkins build test-report` / `jenkins build log` to get the failing scenarios, exceptions, and BrowserStack session references.
2. **Classifies** each failure — test-script drift vs. genuine product bug vs. infra/flakiness vs. test-data/environment (`references/failure-taxonomy.md`). Misclassification is the most damaging error, so this is evidence-driven.
3. **Takes over the BrowserStack session post-mortem** — `mobile-auto run import --status "" --probe=false` then `run diagnose --collect-artifacts` to pull device/Appium/crash/network logs, video, and the app-source XML/screenshot at the failing step (`references/triage-playbook.md`).
4. **Repairs** the test scripts minimally — updates locators/page objects/step glue/waits to match the current UI, keeping the `.feature` intent intact (`references/repair-patterns.md`).
5. **Verifies and delivers** — local compile gate, re-runs the suite through Jenkins on a fix branch, confirms the previously failing scenarios pass, and opens a PR — or delivers a findings report when no test change is correct (`references/verify-and-deliver.md`).

## Golden rule

Preserve scenario intent. Adapt *how* the app is driven (locators, waits, navigation) when the UI drifts; only change the `.feature` when the business flow genuinely changed. Never make a test pass by weakening assertions or hiding a real product bug.

## Requirements

Runtime image CLIs (invoked via the runtime shell, not model function tools):

- `jenkins` — build status, `build test-report`, `build log`, `build wait`, artifacts.
- `mobile-auto` — BrowserStack App Automate session takeover and diagnostics.
- `git` / `gh` — repo inspection and PR creation.
- `mvn` (JDK 21 + Maven 3.9, present in the OpenCode runtime image) — local compile gate.

The `jenkins build test-report` / `jenkins build wait` commands and the `mobile-auto` post-mortem takeover flags used here are provided by `engineering-flow-platform-tools`.

## Files

- `skill.md` — skill definition and phase-by-phase workflow.
- `references/triage-playbook.md` — concrete Jenkins → BrowserStack command sequences.
- `references/failure-taxonomy.md` — failure classification with signals and actions.
- `references/repair-patterns.md` — Java/Cucumber/Appium fix patterns.
- `references/verify-and-deliver.md` — verification loop, PR body, findings report.
