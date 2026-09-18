# PRD template

Replace the angle-bracket prompts with evidence, a labelled suggestion or `To confirm`. Reuse the IDs the input documents already have.

## Document information

- Product / scope of this version: <name and version>
- Status: Draft / Open items pending / Confirmed (only with a confirmation source)
- Purpose, readers and material cut-off: <known information>
- Change summary: <new, or the changes in this revision and the affected IDs>

## Objectives, users and current state

<Target users, real pain, how it is handled today, the business goal and why now. Separate facts from inference.>

| Objective ID | Expected outcome | Evidence / basis | Success metric and window | Baseline / target / data source |
| --- | --- | --- | --- | --- |
| OBJ-001 | <outcome> | SRC-001 or To verify | <metric definition> | <Unknown, To confirm> |

## Scope and business context

- In scope: <capabilities and roles>
- Explicitly out of scope: <capabilities and boundary>
- Deferred: <original requirement ID, reason, revisit condition>
- Key terms: <one definition each; disambiguate>
- Key journeys / flows (when applicable): <role, entry, actions, completed result, recovery from failure>

## Functional requirements and acceptance

Group by business capability and keep the IDs on every row.

### REQ-001: <capability>

- Linked objective / journey: <ID>
- Status and basis: <decided / suggested / To confirm; SRC or ASSUMP ID>
- Behaviour: <role> can <action> when <condition>, producing <observable result>.
- Business rules: <permissions, state transitions, limits, exceptions and boundaries>
- Explicitly not covered: <exclusions for this requirement, or "none known">

| AC ID | Given | When | Then | Requirement |
| --- | --- | --- | --- | --- |
| AC-001 | <precondition> | <action> | <observable result or boundary> | REQ-001 |

## Non-functional requirements

| ID | Constraint and scope | Metric / threshold | Environment / load / measurement | Source or assumption | AC ID |
| --- | --- | --- | --- | --- | --- |
| NFR-001 | <performance, reliability, security, ...> | <To confirm> | <measurement conditions> | <SRC / ASSUMP> | <AC ID> |

## Dependencies, assumptions and open items

| ID | Type | Content and basis | Affected requirements / AC | Verification or decision | Owner / revisit |
| --- | --- | --- | --- | --- | --- |
| ASSUMP-001 | Assumption | <unverified judgement> | <IDs> | <how to confirm or refute> | <known person or To assign> |
| Q-001 | Open question | <decision needed> | <IDs> | <material or choice needed> | <known person or To assign> |

## Sources and coverage check

| Source ID | Material / version actually checked | Location | Conclusions or requirements supported | Limits / conflicts |
| --- | --- | --- | --- | --- |
| SRC-001 | <file, link or member statement> | <passage or conversation> | <IDs> | <unverified parts> |

- Missing inputs: <material not accessed and its effect; never listed as checked>
- Incomplete acceptance definitions: <REQ / NFR IDs and reason>
- Hand-off notes: <scope boundaries, dependencies, questions to close first>
