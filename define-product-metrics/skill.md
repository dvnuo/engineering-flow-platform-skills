---
name: define-product-metrics
description: "Define product success metrics as a reproducible calculation contract (entity, formula, denominator, window, exclusions), with baselines, targets, guardrails and the events needed to measure them. Use when a PM or BA must specify KPIs, a measurement plan or instrumentation needs, before dashboards or experiment analysis are built."
version: 1.0.0
owner: engineering-flow-platform
triggers:
  - /define-product-metrics
  - define product success metrics
  - specify KPI definitions and guardrails
  - 定义产品指标口径与埋点需求
  - 制定产品效果衡量方案
tools: []
output_format: markdown
references:
  - references/template.md
opencode:
  execution_kind: prompt_only
  compatibility: full
  permission:
    default: ask
  capability_tags:
    - prompt-only
    - deliverable
    - product-management
---

# Product metrics and measurement plan

Write the metric dictionary and instrumentation needs that product, data, engineering and operations can work from: what success means, how each number is calculated, and what decision changes when it moves. This skill does not build dashboards, run queries or analyse experiments.

## Non-negotiable rules

1. The deliverable is a Markdown file under `output/` plus a short reply with a download link. Do not paste the whole document into chat.
2. Every value comes from the member's message, an attached file, or a tool result. Never invent baselines, historical values, trends or query results. Write `Unknown` for missing values and label proposed thresholds `suggested`.
3. A metric name is not a definition. Every metric gets a formula with numerator, denominator, eligible population and window.
4. Write the document and the reply in the language the member used. Keep metric IDs and headings stable across revisions.
5. This skill defines and plans. It does not connect to analytics platforms, deploy events, create alerts or write bundles, and it never claims that it did.

## Inputs

- Attached files land under `uploads/` in the workspace; read them with the read tool before quoting anything.
- When the member points at a Jira issue, Confluence page or GitHub file, fetch it through bash with the runtime CLIs (`jira`, `confluence`, `gh`), always with `--json`, and read the `ok` / `data` / `error` envelope. Discover commands with `jira commands --json` or `confluence commands --json`. A source you could not fetch is a missing input.
- Use the target users, product value, business goals, key flows, existing metrics, data sources and constraints supplied. Where a metric glossary already exists, reuse it and point out conflicts.
- Confirm the decision the metrics must support (find the drop-off, judge a capability, monitor experience).
- Ask at most one question, and only when it changes which metrics matter. Record every other gap as `Unknown`.

## Workflow

### 1. Choose metrics that fit the decision

Start from the value the user gets and pick the few metrics that influence this decision:

- **Outcome metrics**: the user or business result to improve. Propose a North Star only when it fits; do not force one.
- **Driver metrics**: behaviours the team can influence and expects to move the outcome.
- **Guardrail metrics**: what must not get worse (experience, reliability, cost, another team's outcome).
- **Business metrics**: revenue, cost or similar, only where relevant to this decision.

For each, state what decision changes when it moves. Activity-only metrics get a quality, success-rate or segment view. Driver-to-outcome links are hypotheses; correlation is not causation.

### 2. Write a reproducible calculation contract

Assign `M-01`, `M-02`, ... and define at least:

- Business meaning, analysis entity (user, account, task, order), unit and grain.
- Formula, numerator, denominator, eligible population and event conditions. Count metrics say `no denominator`.
- Window, time zone (Hong Kong, UTC+8, unless the member says otherwise), start and end rule, calendar or rolling period; for retention, the cohort entry condition and return window.
- Deduplication key, rules for repeated or retried events, exclusions and the segments to compare.
- Data source, known fields, refresh latency and the owner of the definition; unknown fields stay `To confirm`.
- Handling of zero denominators, missing events, late data and partial windows. Missing data never becomes zero.

State whether a ratio aggregates as total numerator over total denominator or with explicit weights; do not average group percentages by default. Mark metrics with different definitions or incomplete windows as not comparable.

### 3. Baseline, target and guardrails

List the actual baseline with its observation period, the target or direction, the deadline and the evidence, each separately. With direction only, describe the expected change and the plan to establish a baseline.

Give every main outcome at least one relevant guardrail or say why none applies, with the same rigour of definition, threshold source, window and owner. Separate product anomalies from data-quality anomalies so a collection failure is not read as user behaviour.

Alerts are response suggestions: who looks, what condition and duration trigger an investigation, what to check first, when to stop or roll back a related experiment. Without a baseline, do not set pseudo-precise thresholds, and never turn an alert into a causal conclusion.

### 4. Instrumentation needs

Map each M ID to the events, attributes, business object IDs, trigger moment and calculation source it needs. Mark each as `exists (evidence)`, `verify availability` or `proposed`.

For new events, describe the business meaning of one trigger, idempotency and deduplication, client or server origin, and the required fields only. Event and field names without an agreed convention are proposals.

Provide acceptance examples: how success, failure or cancel, retry, cross-window, zero-denominator and late-data cases should count. These are planned checks, not completed tests.

### 5. Deliver

1. Read `references/template.md` (relative to this skill's directory) and keep only the sections the task needs; a small task keeps only the metrics involved.
2. Save the document as `output/metrics-<slug>.md`, where `<slug>` is a short ASCII, lowercase, hyphenated name for the product or initiative. For a revision, write to the same path so the earlier link keeps working.
3. Recommend how each metric is viewed (trend for change, funnel for stages, segments for differences), how often, and by whom; do not assume daily data.
4. Before replying, check that two analysts would get the same number from the same input, that missing data is detectable, that targets and baselines are separate, and that guardrails cover the main side effects.
5. Reply in the member's language with: two or three sentences on the metric set and the decision it supports; the fields or owners still to confirm (at most five); the download link written exactly as a workspace link, for example `[Download metrics-onboarding.md](workspace:output/metrics-onboarding.md)`; and one line saying the file is also in the Server Files panel under `output/`.

## Hand-offs

- Engineering and data teams work from the M IDs and the `To confirm` fields.
- Test cards in `product-discovery` and outcome entries in `prioritize-roadmap` should cite these definitions.

## Provenance

Method adapted from Pawel Huryn's phuryn/pm-skills (MIT). Pinned sources, licence and the EFP additions are listed in `README.md` next to this file.
