# Business process analysis template

Trim to the task. Square brackets are prompts; write `To confirm` for unknowns and say who or what can confirm. The IDs below are format examples, not existing requirements or facts.

## Scope and evidence

- Business goal: [expected business outcome]
- Start / end: [trigger event] -> [completion condition]
- Scope and exclusions: [roles, systems, business scenarios]
- Status: [draft / pending business confirmation]; analysis baseline: [material version or date]

| Source ID | Material and location | Date / version | Type of fact | Limits or conflicts |
|---|---|---|---|---|
| SRC-01 | [interview passage / document section] | [known value or Unknown] | [actual practice / written rule / suggestion] | [limits] |

## As-is process and roles

| Step ID | Trigger / input | Actor | Action / decision | Decider | Output, receiver, next step | Source | Issue |
|---|---|---|---|---|---|---|---|
| AS-01 | [input] | [role] | [action] | [role or n/a] | [result and next step] | SRC-01 | [observation / inference] |

Working versus waiting time (only when durations or timestamps were supplied): [per-stage working time, waiting time, largest wait].

## Business rules and decision table

| Rule ID | Scenario | Conditions and bounds | Outcome / next step | Source | Status |
|---|---|---|---|---|---|
| BR-01 | [scenario] | [conditions] | [outcome] | SRC-01 | [confirmed / To confirm / proposal] |

| Row | Condition A | Condition B | Action / outcome | Linked rule |
|---|---|---|---|---|
| D-01 | [explicit value range] | [yes / no / unknown / n/a] | [outcome or undecided] | BR-01 |

- Match policy: [single match / evidenced precedence / To confirm]
- No-match handling: [outcome / To confirm]
- Missing-input handling: [evidenced behaviour such as request the value or route to a person, or To confirm]
- Boundaries and conflicts: [overlaps, gaps, threshold definitions, who confirms]

## Exceptions and recovery

| Exception ID | Steps / rules involved | Trigger | Business state / user result | Recovery or escalation | Responsible role | Source / to verify |
|---|---|---|---|---|---|---|
| EX-01 | AS-01 / BR-01 | [trigger] | [result] | [path] | [role] | [basis] |

## To-be process and differences

| To-be step | As-is step | Change type | Proposed action / hand-off | Problem addressed | Rule change | Dependencies and assumptions |
|---|---|---|---|---|---|---|
| TO-01 | AS-01 | [keep / replace / merge / add] | [action] | [problem and source] | [rule ID] | [dependencies] |

| Measure | Definition / window | Baseline and source | Target and basis | Responsible role |
|---|---|---|---|---|
| [business outcome] | [definition] | [value or Unknown] | [value or to negotiate] | [role or To confirm] |

## Requirement hand-off and open items

| To-be step / rule | Existing or candidate requirement ID | Acceptance intent | Dependencies | Status |
|---|---|---|---|---|
| TO-01 / BR-01 | [REQ ID or candidate] | [observable normal / boundary / exception behaviour] | [dependencies] | [draft] |

| Open question | Why it affects the conclusion | Evidence / conflict | Who or how to confirm | Objects to update after the decision |
|---|---|---|---|---|
| [question] | [effect] | [source] | [role / method] | [step / rule / requirement IDs] |
