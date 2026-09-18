---
name: analyze-business-process
description: "Model the current (as-is) and proposed (to-be) business process from supplied evidence: steps with actors and hand-offs, business rules as decision tables, exceptions and recovery paths, gaps, and the hand-off to requirements. Use when a BA or PM asks to map or document a business process, clarify business rules and approval logic, or compare the current process with a proposed one."
---

# Analyse a business process

Turn interviews, operating instructions or requirement fragments into a reviewable BA document that connects the current process, the proposed process, the business rules and the exception handling. Tables are enough to express the result; no diagramming tool is needed. Add a Mermaid flowchart only when the member asks for a diagram.

## Non-negotiable rules

1. The deliverable is a Markdown file under `output/` plus a short reply with a download link. Do not paste the whole document into chat.
2. Every step, rule, threshold and owner comes from the member's message, an attached file, or a tool result. Never invent durations, savings, approval authority or policy references. Write `To confirm` and name who can confirm.
3. Keep actual practice, written rules and interviewee suggestions apart, and keep the to-be process apart from current facts. A proposed rule is a proposal until the member says it is approved.
4. Write the document and the reply in the language the member used. Reuse step, rule and requirement IDs from the sources.
5. This skill analyses. It does not create Jira issues or change any business configuration, and it never claims that it did.

## Inputs

- Attached files land under `uploads/` in the workspace; read them with the read tool before quoting anything.
- When the member points at a Jira issue, Confluence page or GitHub file, fetch it through bash with the runtime CLIs (`jira`, `confluence`, `gh`), always with `--json`, and read the `ok` / `data` / `error` envelope. Discover commands with `jira commands --json` or `confluence commands --json`. A source you could not fetch is a missing input.
- Identify the business goal, the start and end events, the roles and systems involved, the current problems and the proposed change. Give unlinked member statements `SRC-01` style IDs.
- With incomplete scope, state the working boundary and analyse what is known; ask only about a gap that affects correctness.
- When the member asks for the current process only, deliver as-is and problems; a proposed process is never an implementation commitment.

## Workflow

### 1. Establish the as-is

List steps as `AS-01`, `AS-02`, ... (or the member's IDs) with trigger, input, actor, action or decision, decider, output and receiver. Unknown people are `To confirm`; do not infer approval rights from a job title.

Mark waits, rework, re-keying, ownership gaps and system boundaries. Without measurements, describe the problem; do not invent times or savings. When the member supplies stage durations or timestamps, separate working time from waiting time per stage and name the single largest wait; otherwise skip this.

### 2. Make business rules explicit

Give each rule a stable `BR-01` ID with scope, condition, outcome, basis and status (`confirmed`, `To confirm`, `proposal`). Use a decision table when several conditions interact, and define the conditions precisely: unit, currency, time zone, and whether bounds are inclusive.

Check every row for overlaps and gaps: when several rules match, which one wins; when none matches, what happens. Distinguish `no`, `unknown` and `not applicable`; a missing input does not mean the condition failed. Thresholds, responsibilities and policy references must come from the material.

### 3. Cover exceptions and recovery

At each hand-off, check returns, cancellations, duplicate submissions, timeouts, system failure and unauthorised actions where they matter for this process. Record trigger, affected state, responsible role, what the user sees, and the recovery or escalation path (`EX-01`, ...). Behaviour with no evidence, such as "exceptions are ignored" or "the system compensates automatically", is `To confirm`, not current practice. Model only the exceptions that matter for the business goal.

### 4. Form the to-be

Propose target steps `TO-01`, ... around the confirmed pain points, mapping each to the as-is steps it keeps, merges, replaces or adds. Explain the business value, affected roles, rule changes, system and data dependencies, and the assumptions still to verify. Compare the proposal with keeping the status quo; expand several options only when the member asks or the trade-off requires it. Define end-to-end success as an observable outcome; baseline, target and window stay `Unknown` until supplied.

### 5. Hand off to requirements

Map every process or rule change that should become a requirement as `step -> BR -> REQ -> acceptance intent`. Keep existing REQ IDs; mark new ones as candidates. Give acceptance intents for normal, boundary and exception behaviour so the PRD, the stories or the test design can pick them up.

### 6. Deliver

1. Read `references/template.md` (relative to this skill's directory); a simple question keeps only the relevant tables.
2. Check that start and end close, every hand-off has a receiver, every rule is decidable, and every to-be change traces to a problem. Parts without evidence are labelled `unverified`; "no issue found" is not "no risk".
3. Save the document as `output/process-<slug>.md`, where `<slug>` is a short ASCII, lowercase, hyphenated name for the process. For a revision, write to the same path so the earlier link keeps working.
4. Reply in the member's language with: two or three sentences on the process and the main gaps; the rules or hand-offs still to confirm (at most five); the download link written exactly as a workspace link, for example `[Download process-expense-claims.md](workspace:output/process-expense-claims.md)`; and one line saying the file is also in the Server Files panel under `output/`.

## Hand-offs

- Requirements for the to-be changes: `write-product-requirements`, carrying the BR and TO IDs.
- A rule change against an existing requirement baseline: `analyze-requirement-change`.
