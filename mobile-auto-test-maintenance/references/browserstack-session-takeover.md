# BrowserStack Session Takeover and Replay Playbook

Two distinct modes. Pick deliberately and say which one you are in.

## Mode A — Inspect an existing session (takeover)

Use when the Jenkins log gave you a session id, or a session may still be running.

```bash
mobile-auto session candidates --status running --json    # discover live sessions
mobile-auto session probe --session-id <id> --json        # capabilities, app, device, state
mobile-auto run import --session-id <id> --probe --json   # adopt it as a local run
mobile-auto run import --from-url <dashboard-url> --json  # same, from a dashboard URL
```

After import:

```bash
mobile-auto run guard --run-id <run> --hold-for 10m --json     # keep it from idling out
mobile-auto run diagnose --run-id <run> --out evidence --json  # device/Appium logs, video refs
mobile-auto observe --run-id <run> --json                      # current UI snapshot + refs
```

Rules:

- **Read-only by default.** `probe`, `diagnose`, `observe` are safe. Mutating actions
  (tap/type/scroll) on an imported session can race the original runner —
  BrowserStack does not enforce exclusive control. Only interact if the run is
  clearly abandoned (original runner finished/crashed) or you were told to take over.
- `run claim` is a local lease for coordination between agents, not a remote lock.
- **Never `run finish` an imported session** that the original CI runner may still
  own; `run release` your claim instead.
- Finished sessions can still be imported for `diagnose` (logs + video metadata).

## Mode B — Reproduce on a fresh session (replay)

Use for repair experiments and verification. Always your own session; full control.

```bash
mobile-auto run start --app <bs://app-id-or-file> --platform <android|ios> --device "<device>" --network public --json
```

- Match the failing build: same app id/version and a device close to the CI one
  (from Mode A `probe` or Jenkins parameters).
- `--network public` unless the app needs BrowserStack Local; private sessions must
  ensure the tunnel first (`BROWSERSTACK_LOCAL_BINARY` exists in the runtime image).

Replay the failing scenario step by step, mirroring the Gherkin:

```bash
mobile-auto observe --run-id <run> --json
mobile-auto locate --run-id <run> --role button --name "Login" --json
mobile-auto tap --run-id <run> --ref <obs>:<el> --wait-change --post-observe --json
mobile-auto type --run-id <run> --ref <obs>:<el> --text-env TEST_PASSWORD --json
mobile-auto wait visible --run-id <run> --text "Home" --timeout 20s --json
```

- Use only refs from the LATEST observe; re-observe after every mutating action
  (or use `--post-observe`).
- Secrets via `--text-env` / `--text-stdin`, never inline.
- At the failure point, the current `observe` output / page source is the ground
  truth for the new locator or flow. Save it into the evidence bundle.

Finish and collect:

```bash
mobile-auto run report --run-id <run> --out report.json --json
mobile-auto run finish --run-id <run> --status <passed|failed> --collect-artifacts --json
```

`run finish` is mandatory on every path, including errors — leaked sessions burn
device minutes and block parallel slots.

## Suite-style verification

When the repo's scenarios are expressible as a mobile-auto YAML suite:

```bash
mobile-auto test run --file suite.yaml --junit-out junit.xml --evidence-dir evidence --json
```

This gives CI-shaped proof (junit + evidence) without a Jenkins round trip.
