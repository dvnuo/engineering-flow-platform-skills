---
name: analyze-requirement-change
description: "Assess a proposed requirement change against a supplied baseline: the exact differences, the trace to affected rules, stories, acceptance criteria, tests and dependencies, the impact per area, decision options, and the list of artefacts to update once decided. Use when a BA or PM asks for change impact analysis, scope change assessment, or what a requirement change affects."
---

# Analyse a requirement change

Compare a change request with the requirement baseline the member supplies and deliver a reviewable impact analysis: what changes, who and what is affected, which options exist, and what must be updated once a decision is made. Inputs can be document fragments, requirement tables, stories or acceptance criteria.

## Non-negotiable rules

1. The deliverable is a Markdown file under `output/` plus a short reply with a download link. Do not paste the whole analysis into chat.
2. Every difference and impact comes from the member's message, an attached file, or a tool result. Never invent baseline content, affected services, tests, owners, estimates or dates. An area without material is `not assessed`, never "no impact".
3. Keep "confirmed affected", "suspected", "to verify" and "confirmed unaffected" apart, and keep the recommendation apart from the approval record.
4. Write the document and the reply in the language the member used. Reuse existing IDs; draft IDs are labelled and are not Jira keys.
5. This skill analyses. It does not modify Jira, schedules or remote documents and it sends no notifications, and it never claims that it did.

## Inputs

- Attached files land under `uploads/` in the workspace; read them with the read tool before quoting anything.
- When the member points at a Jira issue, Confluence page or GitHub file, fetch it through bash with the runtime CLIs (`jira`, `confluence`, `gh`), always with `--json`, and read the `ok` / `data` / `error` envelope. Discover commands with `jira commands --json` or `confluence commands --json`. A source you could not fetch is a missing input.
- Record the baseline's name, version or date, status and source. Use "latest" or "approved" only when the material says so. With fragments only, state the coverage and label the result a preliminary analysis.
- For each change, record old behaviour, proposed behaviour, reason, requester and intended effective scope. Classify the reason: defect fix, clarification, new stakeholder requirement, technical limitation found during implementation, misunderstanding of the original requirement, or strategic change.
- Approval status and analysis completeness are recorded separately.

## Workflow

### 1. Diff the baseline

Classify each change as added, modified, removed or to clarify across business rules, roles, inputs and outputs, and acceptance behaviour. Check wording shifts that change obligations or boundaries: optional to mandatory, working days to calendar days, greater-than to greater-or-equal. When materials conflict, keep both statements with their sources; neither file order nor stronger wording decides. With an unknown baseline, describe the proposed behaviour and the items to check; do not claim a before-and-after comparison.

### 2. Build the trace chain

Follow `change -> requirement -> business rule or process step -> story -> acceptance criterion -> test or dependency`. Mark each link `confirmed affected`, `suspected`, `to verify` or `confirmed unaffected` with its evidence or reasoning, and separate direct changes from downstream effects and unverified indirect effects. Missing acceptance criteria, tests or dependency material are coverage gaps; not found is not the same as not existing. Stop at a stable boundary and name the systems and teams outside it.

### 3. Assess the impact

Check, as relevant: user behaviour, process and responsibilities, data and history (does the new rule apply to historical objects, in-flight cases or new ones only; do not guess a migration strategy), interfaces and upstream or downstream systems, permissions, reporting and operations. For acceptance and tests, list what stays, changes, is added or retired, and whether regression is needed. Record benefits, risks, work items and dependency owners. Estimates and dates come from the team, with their assumptions; without them, describe the work to estimate and the uncertainties. "Unaffected" always states the evidence it rests on.

### 4. Compare the options

Compare only the meaningful options among accept, reduce or phase, defer and keep the baseline. For each: business benefit, cost and risk, dependencies, reversibility and preconditions, all on the same basis. Give a recommendation with its conditions and the evidence that would change it. Distinguish who decides scope and priority, who supplies cost and technical judgement, and who signs off; unknown roles are `To confirm`. Existing authorisations are recorded as evidence, not re-created as a new approval process.

### 5. List the updates

List the requirements, rules, stories, acceptance criteria, tests, documentation and delivery plans to update once decided, with owners, and flag what needs re-confirmation. Everything stays `proposed` until the decision is recorded. Note the effective boundary, rollback needs and who must be informed (informing them is not done here). Keep the old baseline reference and the decision record so the next analysis can see the version difference.

### 6. Deliver

1. Read `references/template.md` (relative to this skill's directory); a small change keeps the diff, impact and recommendation sections only.
2. Check that every conclusion traces to evidence or a labelled assumption, and that the unassessed areas and the gaps that could overturn the recommendation are visible.
3. Save the document as `output/change-<slug>.md`, where `<slug>` is a short ASCII, lowercase, hyphenated name for the change. For a revision, write to the same path so the earlier link keeps working.
4. Reply in the member's language with: two or three sentences on the change and its main impact; the decisions and verifications still needed (at most five); the download link written exactly as a workspace link, for example `[Download change-refund-window.md](workspace:output/change-refund-window.md)`; and one line saying the file is also in the Server Files panel under `output/`.

## Hand-offs

- An accepted change: `write-product-requirements` in revise mode and `break-down-user-stories`, carrying the CHG IDs.
- Jira updates go through the existing Jira flows after the decision, not through this skill.
