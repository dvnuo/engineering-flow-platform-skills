# Epics and stories template

Replace the example IDs with the source document's IDs. Fill fields with actual information or `To confirm`; do not add assumed project facts.

## Scope of this breakdown

- Product / version / goal of this round: <scope>
- Inputs checked: <source IDs, files or links, versions and locations>
- Missing material and its effect: <material not checked>
- Key decisions / assumptions: <listed separately with their basis>
- Explicitly excluded this round: <original requirement ID, reason, decision source>

## Requirement list

| Requirement ID | Type | Requirement and constraints | Source location | Status |
| --- | --- | --- | --- | --- |
| REQ-001 | Functional / business rule | <actual requirement> | <SRC ID and passage> | <confirmed / To confirm> |
| NFR-001 | Non-functional | <threshold and measurement or To confirm> | <source> | <status> |

## Epics

| Epic ID | User or business outcome | Requirement IDs | Dependencies and scope boundary |
| --- | --- | --- | --- |
| EPIC-001 | <what becomes possible when done> | <REQ / NFR / UX IDs> | <prerequisite capabilities and exclusions> |

## Stories in dependency order

### ST-001: <behaviour and result>

- Epic / type: <EPIC ID; user story or enabler task>
- Role, goal, value: As a <role>, I want <capability>, so that <outcome>.
- Sources and constraints: <requirement IDs; without a direct source, the assumption and its status>
- In this story: <boundary>
- Not in this story: <exclusions and seams>
- Prerequisites: <existing capability / earlier story / external dependency and its availability>
- Blockers: <"none found", or the block; incomplete material never means "all blockers cleared">
- Size judgement: <whether a further split is needed and why; no invented days or points>

| AC ID | Given | When | Then | Requirement / rule |
| --- | --- | --- | --- | --- |
| AC-001 | <precondition> | <action> | <observable result> | <REQ / NFR / UX ID> |

## Two-way coverage matrix

| Requirement ID | Epic / story IDs | AC IDs | Coverage | Uncovered part / exclusion reason |
| --- | --- | --- | --- | --- |
| REQ-001 | <IDs, or none> | <AC IDs> | complete / partial / uncovered / explicitly excluded | <constraint or reason> |

Mark `complete` only when every constraint has an AC. Add the reverse check (story -> source) and list scope additions without an upstream source separately.

## Gaps, dependencies and open items

| Issue ID | Requirement / story | Gap or conflict | Delivery impact | Next step | Owner / closing condition |
| --- | --- | --- | --- | --- | --- |
| GAP-001 | <ID> | <specific issue> | <blocking or not> | <actionable step> | <known value or To assign> |

- Dependency check: <cycles, dependencies on later stories, unavailable external dependencies and suggested handling>
- Coverage statistics (only with a complete list): <total, complete, partial, uncovered, excluded; denominator stated>
- Revision summary (if applicable): <changed IDs, scope and dependency effects>
- Hand-off conclusion: <what can be refined or implemented, what needs evidence or a decision first>

## CSV companion

`output/stories-<slug>.csv`, one row per story: `Story ID, Epic, Summary, Issue Type, Description, Acceptance Criteria, Requirement IDs, Depends On, Priority, Labels`. Multi-line acceptance criteria are quoted; `Priority` and `Labels` stay empty unless supplied.
