# Failure Taxonomy

Classify every failing scenario before editing anything. The classification decides whether you change test code, report a defect, or recommend a retry. Misclassification is the most damaging error in test maintenance: "fixing" a test to hide a product bug, or "reporting a bug" for what is really a stale locator, both erode trust in the suite.

## A. Test-script drift (repair the implementation)

The scenario's business intent is still valid, but the app changed how it exposes that intent.

Signals:
- `NoSuchElementException` / `TimeoutException` for an element that clearly still exists on screen in the app-source XML/screenshot, under a different id/text/xpath/position.
- A screen was restructured, an element moved into a menu/tab, or an intermediate screen was added/removed.
- `StaleElementReferenceException` because the screen re-renders after an action.
- The app source XML at failure contains the target content, but not where/how the test looked for it.

Action: adapt the **locator / page object / step glue / navigation / wait** to match the current UI. Keep the `.feature` intent. This is the core maintenance case.

Sub-cases and their fixes:
- **Locator changed** → update the locator constant / `@FindBy` / `By` strategy to the new stable identifier (prefer accessibility id / resource-id / stable text over brittle absolute xpath).
- **Extra screen inserted** (for example a new consent/permission/tooltip step) → add the handling step in the page object or an `@Before`-style hook, not in every scenario, unless it is genuinely part of the business flow.
- **Element now needs a scroll / different gesture to reach** → add a scroll-to-target before the interaction.
- **Timing: element appears later** → wait for the real readiness signal (element visible/enabled, not a fixed sleep).

## B. Genuine product bug (report, do not "fix" the test)

The test is correct; the app is wrong.

Signals:
- App crash / ANR in the crash or device log at the failing step.
- Assertion mismatch where the **test's** expected value matches the requirement/ticket, and the app produced a wrong value (confirmed against the screenshot/network response).
- A required element is genuinely absent from the app source (not merely relocated) and its absence is a regression, not an intended removal.

Action: do **not** modify the test to pass. Produce a defect report with: the scenario, the expected vs. actual behavior, the evidence (screenshot, crash log, network response, video timestamp), the app build/version under test, and a reproduction note. Recommend filing/linking a product bug ticket. Leave the test failing (it is correctly catching the bug).

## C. Infrastructure / flakiness (retry and/or targeted robustness, not scenario logic)

The test and the app are both fine; the run environment failed.

Signals:
- `SessionNotCreatedException`, device allocation failure, BrowserStack capacity/queue errors, tunnel/local errors.
- Session timeout / idle termination unrelated to a specific step.
- Intermittent network blips in the network log, not a consistent backend failure.
- The same scenario passes on retry with no code change.

Action: recommend a retry of the specific build/scenario. Only make a **targeted** robustness change when a real, repeatable timing weakness is proven by evidence (for example replace a fixed sleep with an explicit wait, add a retry to a known-flaky gesture). Never paper over flakiness with blanket sleeps or broad try/catch. Do not change scenario intent.

## D. Test data / environment (fix config/data, not the scenario)

The scenario and app logic are fine, but the inputs or environment were wrong.

Signals:
- Backend 4xx/5xx for auth or data setup in the network log.
- Stale/expired test account, consumed one-time data, wrong environment endpoint.
- Wrong app build/version or wrong device capabilities were used (feature under test not present in that build).

Action: fix the test data, credentials handling, environment config, or capabilities/build reference. Prefer secret-safe patterns (`--text-env` / `--text-stdin`, never inline secrets). Do not weaken the scenario.

## Deciding between A and B (the hard case)

Assertion failures and "element missing" both span drift and product-bug. Resolve with evidence, not assumption:

1. Get the **requirement**: the Gherkin scenario, its tag/ticket, and if available the linked Jira acceptance criteria. What *should* happen?
2. Get the **actual**: the app-source XML, screenshot, and network response at the failing step. What *did* happen?
3. If the app still supports the intent but exposes it differently → **A (drift)**, adapt the implementation.
4. If the app fails to support the intent (crash, wrong result vs. the requirement, true regression) → **B (product bug)**, report it.
5. If the requirement itself changed (the product intentionally changed the flow) → this is a **scenario-level** change: update the `.feature` to the new intent, and prefer confirmation before doing so.

When you cannot get enough evidence to separate A from B confidently, stop and report the ambiguity with what you have — do not guess.
