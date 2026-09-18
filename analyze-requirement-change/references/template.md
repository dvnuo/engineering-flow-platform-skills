# Requirement change impact template

Trim to the size of the change. Write `To confirm` for unknowns. IDs are format examples; keep the member's existing IDs. Without a complete baseline, label the result a preliminary analysis.

## Baseline and change summary

- Baseline: [name, version or date, status, source]
- Analysis scope: [objects supplied, areas not assessed]
- Change: [ID, requester, reason category, intended outcome]
- Intended effect: [objects or time range, or To confirm]
- Decision status: [proposed / approved with evidence / rejected with evidence / Unknown]

| Source ID | Material and location | Version / date | Reliable range and limits |
|---|---|---|---|
| SRC-01 | [requirement section / member statement] | [version or Unknown] | [limits] |

## Difference table

| Change ID | Object ID | Old behaviour and basis | Proposed behaviour | Type | Reason / evidence | To clarify |
|---|---|---|---|---|---|---|
| CHG-01 | [REQ ID] | [old value, or baseline missing] | [new value] | [added / modified / removed / clarification] | SRC-01 | [question] |

## Trace and impact matrix

| Change | Source object -> target object | Relationship | Impact / proposed action | Status | Evidence or reasoning | Who verifies |
|---|---|---|---|---|---|---|
| CHG-01 | REQ-01 -> ST-01 | [implements] | [change story behaviour] | [confirmed affected / suspected / to verify / confirmed unaffected] | [location] | [role] |
| CHG-01 | ST-01 -> AC-01 | [accepts] | [adjust boundary scenario] | [status] | [location] | [role] |
| CHG-01 | AC-01 -> [test unknown] | [verification, to add] | [add test mapping] | to verify | [material missing] | [role] |

Objects can be business rules, process steps, requirements, stories, acceptance criteria, tests or dependencies; keep only the relevant types.

| Impact area | Specific change / work scope | Evidence or assumption | Estimate and who gave it | Dependency / owner | Open risk |
|---|---|---|---|---|---|
| [data / process / system / operations ...] | [impact] | [location] | [team estimate or to estimate] | [dependency] | [risk] |

Coverage boundary: [which upstream and downstream material exists, which areas were not assessed, which indirect impacts are still to verify].

## Options and recommendation

| Option | Business benefit | Cost and risk | Preconditions / dependencies | Reversibility | Basis |
|---|---|---|---|---|---|
| [accept / phase / defer / keep baseline, as relevant] | [benefit] | [impact or Unknown] | [conditions] | [basis or To confirm] | [source / assumption] |

- Recommendation: [option and conditions]
- Evidence that would change it: [key unknowns or counter-examples]
- Decision owner: [authorised role or To confirm]
- Decision record: [not yet decided, or the actual decision with date, person and reason]

## Proposed updates

| Object / ID | Update | Prerequisite decision | Owner | Status |
|---|---|---|---|---|
| [requirement / rule / story / AC / test / plan] | [specific change] | [decision or condition] | [role] | [proposed / pending decision] |

## Items to confirm

| Question / missing material | Conclusion affected | Who or how to confirm | Analysis scope after update |
|---|---|---|---|
| [question] | [change / object IDs] | [role / method] | [scope] |

This is an impact analysis draft; no external system was updated.
