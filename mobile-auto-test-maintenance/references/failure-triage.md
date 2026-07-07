# Failure Triage Decision Tree

Classify into exactly ONE primary class before touching code. Multiple failures in
one build: triage each scenario separately; they often share one root cause — say so.

## Quick discriminators

Ask in order:

1. **Did the app version change since the last green build?**
   Yes → suspect locator/flow drift. No → suspect environment, data, or flakiness.
2. **Is the failure deterministic?** (same step, same error, multiple builds/retries)
   Deterministic → drift, data, or app defect. Intermittent → timing or infra.
3. **Does the element exist on the live screen?** (Phase 3 observe at the failure point)
   Exists with different attributes → locator drift. Screen itself different → flow
   drift. Exists and matches but interaction fails → timing or app defect.

## Classes

### 1. Locator drift
- Signals: `NoSuchElementException`, `StaleElementReferenceException`, empty `locate`
  results for a previously working selector; observe shows the element with a changed
  id/text/accessibility label.
- Repair: update the locator in the page object (never inline in steps). Prefer
  stable attributes: accessibility id > resource-id/name > role+name > text > xpath.
  Cross-check both platforms if the page object is shared.

### 2. Flow drift
- Signals: element genuinely absent; a new screen (dialog, consent, onboarding,
  promo) appears first; navigation reordered; observe shows an unexpected page.
- Repair: adjust page objects/steps to traverse the new flow. Additions that are
  conditional in the app (e.g. a one-time dialog) must be handled conditionally
  (`if present, dismiss`) — not as a mandatory step that breaks the other path.
- Only touch the `.feature` file if a user-visible step genuinely changed; keep the
  scenario's business intent identical and flag the wording change in the PR.

### 3. Timing / flakiness
- Signals: passes on retry; failures move between steps; errors like element not
  interactable yet, animation races; duration close to a timeout boundary.
- Repair: replace `Thread.sleep` with explicit conditions (visibility, clickable,
  network-idle hooks the repo already has). Increase timeout ONLY with a reason tied
  to evidence (e.g. cold start on low-end device measured at Ns). One retry layer
  max — never stack retries to bury a real race.

### 4. Environment / infrastructure
- Signals: BrowserStack session failed to start, app upload/`bs://` id expired,
  tunnel (Local) errors, device allocation timeouts, Jenkins node/docker errors,
  dependency download failures — all BEFORE any scenario step ran.
- Repair: none in test code. Deliver an infra report; optionally re-trigger the
  build (`jenkins job build ... --json`) once if the cause looks transient, and say
  you did.

### 5. App defect
- Signals: app crash in device logs, ANR, server 5xx surfaced in UI, behavior
  contradicting the scenario on the LIVE screen (Phase 3 confirms the test is
  faithfully doing what a user would).
- Action: do NOT modify the test. File/report the defect with: scenario, expected vs
  actual, session link, device logs from `run diagnose`, screenshots. If a Jira
  project is configured, create the issue via the `jira` CLI and link it.

### 6. Test data
- Signals: login rejected for seeded account, entity referenced by the test missing,
  expired tokens/coupons; app and locators fine.
- Repair: fix fixtures/config/data-setup steps. If data is provisioned outside the
  repo, report exactly which record is broken and how to restore it.

## Tie-breakers

- Locator vs flow: if the target element exists anywhere in the current flow →
  locator drift; if you must pass through new/changed screens to reach it → flow drift.
- Timing vs app defect: reproduce manually at human speed in Mode B; if it still
  misbehaves slowly, it is the app.
- When still ambiguous after Phase 3, present the two candidate classes with their
  evidence and the safer repair; do not fabricate certainty.
