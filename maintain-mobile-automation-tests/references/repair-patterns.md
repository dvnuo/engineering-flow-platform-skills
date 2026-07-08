# Repair Patterns: Java + Cucumber + Appium

How to apply the smallest correct change once Phase 2 classified a failure as **test-script drift** (class A) or a targeted **infra/data** fix (class C/D). Every change is grounded in the Phase 3 evidence (the app-source XML/screenshot and Appium log at failure), never in a guess.

## Find the code behind a failing Gherkin step

A Cucumber-JVM mobile suite is layered. Trace the failure from the `.feature` down to the locator:

1. **Feature file** (`src/test/resources/**/*.feature`) — the failing scenario name from `build test-report` maps to a `Scenario:` line; the failing step text (from the log's failure block) maps to a `Given/When/Then` line.
2. **Step definition** (`src/test/java/**/steps/*.java`) — find the `@Given/@When/@Then` whose regex/cucumber-expression matches the failing step text. This is the glue.
3. **Page object / screen / driver** — the step usually delegates to a page object or a `DeviceStepDriver`-style abstraction (see the generator skill's structure: `driver/`, `driver/impl/common|ios|android`). The actual `By`/`@FindBy`/`@AndroidFindBy`/`@iOSXCUITFindBy` locator lives here.
4. **Locator constant** — the specific selector that threw `NoSuchElementException`/`TimeoutException`.

Search commands (run in the cloned repo):

```bash
grep -rn "Scenario: <name>" src/test/resources
grep -rn "<failing step text fragment>" src/test/java   # find the @When/@Then glue
grep -rn "<old locator id or text>" src/test/java        # find the locator constant
```

## Pattern A1 — Locator changed

The element still exists (visible in the failure screenshot / app-source XML) but under a new id/text/xpath.

- Take the **new** identifier from the app-source XML at failure, not from memory.
- Prefer stable strategies in this order: accessibility id (`content-desc` / `accessibility id`) → resource-id (`resource-id`) → unique visible text → constrained xpath. Avoid absolute/positional xpath (`//android.widget.FrameLayout[2]/...`) — those re-break on the next layout change.
- Update only the locator constant; keep the step and scenario unchanged.

Appium/Java examples:

```java
// Before: broke when the id was renamed in the app
@AndroidFindBy(id = "com.app:id/btn_login")
// After: use the stable accessibility id present in the failure XML
@AndroidFindBy(accessibility = "login-submit")
private WebElement loginButton;
```

```java
// By-strategy form
// Before
private static final By LOGIN = By.id("com.app:id/btn_login");
// After
private static final By LOGIN = AppiumBy.accessibilityId("login-submit");
```

If Android drifted, check whether the iOS locator (`@iOSXCUITFindBy`) needs the mirror change — platform parity failures often ship together.

## Pattern A2 — An extra screen/step was inserted

A new permission dialog, consent screen, tooltip, or app-update prompt now appears mid-flow.

- If it is **incidental** (a system/permission dialog, a one-off promo) → handle it in a hook or a reusable page-object method, not by editing every scenario. Guard it so it is a no-op when the dialog is absent:

```java
public void dismissOptionalConsentIfPresent() {
    List<WebElement> accept = driver.findElements(AppiumBy.accessibilityId("consent-accept"));
    if (!accept.isEmpty()) {
        accept.get(0).click();
    }
}
```

- If it is a **genuine new step in the user journey** (the product really added a required step) → that is a scenario-level change: add the step to the `.feature` intent and prefer confirmation first (see the golden rule in `skill.md`).

## Pattern A3 — Element needs a scroll/gesture to reach

The target is off-screen in the failure XML.

- Scroll to the target before interacting; use the readiness of the element, not a fixed offset. Prefer the project's existing scroll helper; if using `mobile-auto` live to discover the gesture, mirror it into the Java helper.

```java
// Prefer a scroll-to-text/id helper over a hardcoded swipe count.
scrollToAccessibilityId("checkout-button");
```

## Pattern A4 — Timing / stale element

`StaleElementReferenceException`, or the element exists but is not yet interactable.

- Replace fixed sleeps with an explicit wait on the **real** readiness signal (visible/enabled/clickable), not `Thread.sleep`.

```java
// Before
Thread.sleep(3000);
loginButton.click();
// After
new WebDriverWait(driver, Duration.ofSeconds(15))
    .until(ExpectedConditions.elementToBeClickable(LOGIN))
    .click();
```

- For a re-rendering screen, re-find the element after the action that invalidated it rather than caching the reference.

## Pattern C — Targeted robustness (only with proven flakiness)

Only when Phase 2 classified as infra/flakiness **and** evidence shows a repeatable timing weakness. Make the narrowest change: an explicit wait, or a bounded retry on one known-flaky gesture. Never a blanket sleep, never a broad `try/catch(Exception)` that swallows real failures, never a scenario-logic change.

## Pattern D — Test data / environment / capabilities

- Fix credentials/data handling to be secret-safe: read from env/secret, never inline. When driving `mobile-auto` directly, use `--text-env`/`--text-stdin`.
- Correct wrong capabilities (device, OS version, app build/version) in the config, not in the scenario.
- If the app-under-test build was wrong (feature not present in that build), the fix is the pipeline/capability, not the test.

## Change hygiene

- One logical fix per commit; keep the diff minimal and reviewable.
- Add a short comment at the changed locator/step explaining what drifted and citing the Jenkins build and BrowserStack session, e.g. `// locator drifted in build app-main#412 (bs session ...): btn_login -> accessibility id login-submit`.
- Do not reformat unrelated code, bump dependencies, or "clean up" beyond the fix — that hides the real change from the reviewer.
- Keep the `.feature` untouched unless the business flow genuinely changed.
