# Repair Patterns

Map the triage class to a bounded code change. Follow the repo's existing structure
(typical layout: `features/*.feature`, `steps/*Steps.java`, `driver/` page objects
with common/ios/android implementations — see mobilex-test-cases-generator).

## Pattern 1 — Locator update

1. From the stack frame, find the page object field/method holding the stale locator.
2. From the Phase 3 observe/page source at the failure point, pick the most stable
   attribute available (accessibility id > resource-id/name > role+name > text > xpath).
3. Update per platform. Shared page object + platform divergence → update both the
   iOS and Android implementations; verify each if the CI covers both.
4. If the same locator string appears in multiple page objects, fix all occurrences
   (search the repo) — but do not invent an abstraction layer in a maintenance PR.

## Pattern 2 — Flow adaptation

1. Diff the expected flow (Gherkin + old page objects) against the observed flow
   (Mode B replay).
2. New mandatory screen → add a page object + a traversal call in the affected
   navigation method, not in every scenario.
3. New conditional screen (one-time dialog, promo, consent) → guarded dismissal
   (`if visible within short timeout → dismiss`), placed in the shared navigation
   path so all scenarios benefit.
4. Removed screen/step → delete the traversal; keep the assertion that follows.
5. Reordered flow → reorder page-object calls; scenario text stays put unless the
   user-visible story changed.

## Pattern 3 — Wait strengthening

- Replace fixed sleeps with the repo's explicit-wait helpers (visibility/clickable).
- Anchor waits on the element/state the NEXT action needs, not on generic delays.
- Timeout increases need a measured reason in the PR (e.g. session video shows the
  screen taking ~8s on the CI device class).
- Add at most one wait per failing transition; if three+ places need new waits for
  one scenario, suspect flow drift or an app performance regression instead.

## Pattern 4 — Test data repair

- Prefer self-provisioning: if the repo has data-setup hooks/APIs, create the needed
  state in `Background`/hooks rather than pointing at another fragile record.
- Config-only fixes (accounts, URLs, env names) go in the repo's config files with
  the change called out in the PR; never hardcode secrets — use the existing secret
  mechanism (env vars / CI credentials).

## Java/Cucumber specifics

- Keep step-definition signatures stable; changing a Gherkin phrase means updating
  the `@Given/@When/@Then` regex too — grep for other features using the same phrase
  before changing it.
- Run `mvn -q test-compile` after every batch of edits; fix compilation fully before
  any device verification.
- Respect the repo's formatter/checkstyle if present; do not reformat whole files.

## PR checklist (all classes)

- [ ] One failure class named, with evidence links (Jenkins build, BrowserStack session)
- [ ] Before/after for each locator or flow change
- [ ] Verification: compile + targeted replay (session link) and/or CI run (build link)
- [ ] No unrelated diffs (formatting, deps, refactors)
- [ ] Anything observed-but-not-fixed listed explicitly
