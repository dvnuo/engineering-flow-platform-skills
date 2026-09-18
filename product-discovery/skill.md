---
name: product-discovery
description: "Turn interviews, feedback and data summaries into an evidence log, opportunity and solution comparison, and assumption tests, or a research plan when no evidence exists yet. Use when a PM or BA asks for product discovery, interview planning, research synthesis, or wants a problem validated before a build decision."
version: 1.0.0
owner: engineering-flow-platform
triggers:
  - /product-discovery
  - plan product discovery
  - synthesize customer research into opportunities
  - 产品发现与问题验证
  - 根据访谈梳理用户机会和实验
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

# Product discovery and validation plan

Turn what the member already has (interview notes, feedback, support tickets, usage summaries, constraints) into a traceable discovery document: an evidence log, the problem and the outcome it should change, competing opportunities and solutions, and test cards for the riskiest assumptions. When there is no research yet, deliver the research plan (problem hypotheses, interview guide, test plan) instead of findings. Detailed requirements for a chosen solution belong to `write-product-requirements`.

## Non-negotiable rules

1. The deliverable is a Markdown file under `output/` plus a short reply with a download link. Do not paste the whole document into chat.
2. Every fact comes from the member's message, an attached file, or a tool result. Never invent quotes, interview results, numbers, dates, names or validated conclusions. Write `Unknown` or `To confirm` and say who can confirm.
3. Keep observed facts, interpretations, assumptions and recommendations visibly separate. A recommendation never turns into an approved decision on its own.
4. Write the document and the reply in the language the member used. Keep IDs and section headings stable across revisions.
5. This skill analyses and plans. It does not run experiments, contact respondents, write bundles or create Jira issues, and it never claims that it did.

## Inputs

- Attached files land under `uploads/` in the workspace; read them with the read tool before quoting anything.
- When the member points at a Jira issue, Confluence page or GitHub file, fetch it through bash with the runtime CLIs (`jira`, `confluence`, `gh`), always with `--json`, and read the `ok` / `data` / `error` envelope. Discover commands with `jira commands --json` or `confluence commands --json`. A source you could not fetch is a missing input; never summarise a document from its title.
- Identify the decision the member needs to make: keep researching, choose a problem, compare solutions, or move into requirements.
- Ask at most one question, and only when the answer would change that decision. Record every other gap as `Unknown` and continue with what can be done.

## Workflow

### 1. Catalogue the evidence

Give every piece of material an ID (`E-01`, `E-02`, ...) with source, date, exact location (page, timestamp, ticket), user segment, sample and limitations. Sources you did not read are marked `not read`.

Record three things separately:

- **Observed facts**: behaviour, quotes or numbers the material directly supports, each with its E ID. Keep quotes verbatim; anonymise respondents with a code.
- **Interpretations**: patterns or causes you infer, with supporting and contradicting evidence.
- **Assumptions to test**: judgements the evidence does not yet support, with the gap and how to close it.

Deduplicate repeated mentions of the same respondent or the same relayed feedback. Give frequencies with the sample denominator. A qualitative sample does not yield population percentages, and repetition does not prove saturation. Keep contradictory material and segment differences.

### 2. Define the problem and the outcome

Describe the problem as target user, triggering situation, current behaviour and workarounds, obstacle and consequence. Turn a "build feature X" request back into the situation to improve.

Link user value to a business outcome that can be observed. Fill in baseline, target and deadline only when the material supports them; otherwise write `Unknown` or label the value `suggested`. Never present a suggested target as an existing commitment.

If interviews still have to happen, draft open questions about the last real occurrence, the steps taken, failures and workarounds, and what the user invests today. No pitching and no "would you use ..." questions. Deliver the guide and the fields to capture; do not report interviews that did not happen.

### 3. Compare opportunities and solutions

Build the chain `Outcome -> Opportunity O-xx -> Solution S-xx -> Assumption A-xx`. Opportunities describe a need or difficulty, never an internal feature name.

Compare opportunities by known impact, reach, evidence strength and strategic fit. Without reliable numbers, give qualitative reasons; do not score automatically. For the chosen opportunity, compare two or three genuinely different solutions, including process changes and reuse of existing capability.

For each solution state the opportunities it serves, the key trade-offs and dependencies. Record the options not chosen and what would bring them back.

### 4. Design assumption tests

Check value, usability, feasibility and viability assumptions, and start with those that are high-impact and weakly evidenced. Confidence comes from material, not from a score.

Write one test card per key assumption:

- A/O/S IDs, the uncertainty to remove, current evidence and the counter-evidence you expect.
- Method, target population, owner, sample and time needed, and why this method; unknowns stay `To confirm`.
- Observable behaviour, metric definition, pass and fail criteria; proposed thresholds are labelled `suggested`.
- Guardrails, stop conditions, and the next step if the result is inconclusive.

Interviews, prototype tasks and technical spikes test different risks. An A/B design is a draft until split, sample size and analysis plan are confirmed. Stated intent is not behaviour, and missing a threshold is not automatically a failure.

### 5. Deliver

1. Read `references/template.md` (relative to this skill's directory) and keep only the sections the task needs; delete empty sections instead of filling them with placeholders.
2. Save the document as `output/discovery-<slug>.md`, where `<slug>` is a short ASCII, lowercase, hyphenated name for the product or problem. For a revision, write to the same path so the earlier link keeps working.
3. Every test is `Planned` unless the member supplied actual results; then cite them.
4. Before replying, check that conclusions trace to E IDs, counter-evidence is still there, observations and recommendations are separated, and the key unknowns that could overturn the recommendation are listed.
5. Reply in the member's language with: two or three sentences on what the document covers and the decision it supports; the open questions that block the next step (at most five); the download link written exactly as a workspace link, for example `[Download discovery-invoice-approval.md](workspace:output/discovery-invoice-approval.md)`; and one line saying the file is also in the Server Files panel under `output/`.

## Hand-offs

- Requirements for a chosen solution: `write-product-requirements`, carrying the O/S/A IDs and the open questions.
- Several opportunities competing for the same window: `prioritize-roadmap`.
- Defining the outcome metric properly: `define-product-metrics`.

## Provenance

Method adapted from Pawel Huryn's phuryn/pm-skills (MIT). Pinned sources, licence and the EFP additions are listed in `README.md` next to this file.
