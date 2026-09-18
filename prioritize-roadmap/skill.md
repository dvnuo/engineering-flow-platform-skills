---
name: prioritize-roadmap
description: "Rank product initiatives with a reviewable basis (RICE only when the inputs allow it), record the trade-offs, and draft an outcome-based Now/Next/Later roadmap with dependencies, capacity and commitment status. Use when a PM or BA must prioritise a backlog, justify a ranking, or sequence a roadmap."
---

# Prioritisation and outcome roadmap

Produce a ranking whose reasoning can be checked, and, when asked, an outcome-based roadmap. Connect user and business outcomes, evidence, capacity and dependencies, and keep visible what the decision makers have not confirmed yet.

## Non-negotiable rules

1. The deliverable is a Markdown file under `output/` plus a short reply with a download link. Do not paste the whole document into chat.
2. Every number comes from the member's message, an attached file, or a tool result. Never invent reach, effort, confidence, capacity or release dates. Write `Unknown` and say who can supply the value.
3. Separate the mechanical score from the recommended order, and the recommendation from what is already committed or approved.
4. Write the document and the reply in the language the member used. Keep candidate IDs and headings stable across revisions.
5. This skill drafts the analysis. It does not reorder Jira or publish a roadmap, and it never claims that it did.

## Inputs

- Attached files land under `uploads/` in the workspace; read them with the read tool before quoting anything.
- When the member points at a Jira issue, Confluence page or GitHub file, fetch it through bash with the runtime CLIs (`jira`, `confluence`, `gh`), always with `--json`, and read the `ok` / `data` / `error` envelope. Discover commands with `jira commands --json` or `confluence commands --json`. A source you could not fetch is a missing input.
- Read the goals, candidate items, evidence, current ranking, team capacity, dependencies, time windows and existing commitments the member supplied. Keep original IDs (Jira keys, backlog IDs); otherwise assign `I-01`, `I-02`, ... and say these are local IDs, not Jira keys.
- If the member only wants a ranking, skip the roadmap. If a method is already in use (ICE, weighted scoring, MoSCoW), apply it as defined instead of forcing RICE.
- Ask at most one question, and only when the goal or the comparison basis is unclear. Record every other gap as `Unknown`.

## Workflow

### 1. Hard constraints first

List confirmed deadlines, contractual obligations, security or compliance requirements, dependencies and unavailable resources, each with evidence and owner. Unconfirmed constraints are assumptions.

Classify work as must-do, optional, validate-first or blocked. A score never cancels a confirmed obligation. When constraints conflict or capacity is short, show what is infeasible and which trade-off needs a decision; do not hide the conflict behind a low score.

### 2. One comparison basis

For every candidate: target user, problem, expected outcome, evidence, cost and risk. Rewrite "ship feature X" as an observable user or business change while keeping the link to the original item.

Use RICE only when the inputs are sufficient and comparable. Otherwise compare impact against effort qualitatively and state the uncertainty. Unknown is not zero and not a middle score, and items measured on different scales do not share one ranking.

When RICE applies, declare before calculating:

- **Reach**: the count of one entity in one time window (for example accounts affected per quarter). Accounts are not users. Distinct counts from different periods cannot be added or prorated without checking deduplication, coverage and seasonality; any conversion built on extra assumptions is a scenario, not an observed value.
- **Impact**: per-unit effect on the shared goal, on an agreed scale; a proposed scale is labelled `To confirm`. Do not multiply reach into impact again.
- **Confidence**: a proportion between 0 and 1 (80% becomes 0.8), backed by evidence, never guessed from tone.
- **Effort**: one unit (for example person-weeks) covering design, development, testing and coordination, and greater than zero.
- **Score**: `RICE = R x I x C / E`. Show the raw inputs, units, result and sources. Missing data, `E = 0`, negative or out-of-range inputs give `not computable`, not a number.

### 3. Recommend the trade-offs

Where dependencies, confirmed obligations or strategic choices move an item away from its score order, say so item by item with reason, evidence and the decision owner.

Bucket items as proceed, validate first, defer or not selected, each with a reason. Do not pad a top-five. Close scores are not a decided order: run a sensitivity check with the ranges the member gave, or name the unknowns that would flip the order.

Flag overlapping reach or double-counted benefit; a portfolio's value is not the sum of independent gains. High-impact, low-confidence items go to validation rather than being dropped.

### 4. Outcome roadmap (when asked)

Organise by Now/Next/Later or by the member's existing windows. For each entry: target user, expected outcome, metric, candidate deliverables, dependencies, owner and the basis for confidence.

Map prerequisites first and check for cycles, missing predecessors and cross-team dependencies. Dependencies are not dates: without reliable durations and capacity, give an order only.

Check known effort against available capacity per team and window, including maintenance and run load. Unknown capacity is written as `capacity feasibility not confirmed`.

Now/Next/Later is a planning order, not a commitment. List existing commitments separately from proposed changes; when a commitment cannot be met, show the conflict and the options instead of silently dropping or slipping it.

### 5. Deliver

1. Read `references/template.md` (relative to this skill's directory) and keep only the sections the task needs; delete empty sections instead of filling them with placeholders.
2. Save the document as `output/roadmap-<slug>.md`, where `<slug>` is a short ASCII, lowercase, hyphenated name for the product or planning cycle. For a revision, write to the same path so the earlier link keeps working.
3. Before replying, re-check units, denominators, value ranges and formulas, then dependencies, capacity conclusions and commitment status. Keep items with missing evidence in the table and say what evidence would change the decision.
4. Reply in the member's language with: two or three sentences on the ranking and what drives it; the decisions still needed (at most five); the download link written exactly as a workspace link, for example `[Download roadmap-2026-q4.md](workspace:output/roadmap-2026-q4.md)`; and one line saying the file is also in the Server Files panel under `output/`.

## Hand-offs

- Requirements for the items in Now: `write-product-requirements`.
- Metric definitions for the outcomes: `define-product-metrics`.
- Changes to Jira ranking or fields go through the existing Jira flows, not through this skill.
