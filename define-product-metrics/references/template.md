# Metrics and measurement plan template

Label actual values and suggested values separately. Without data, keep `Unknown`; never fill in illustrative numbers as current values.

## Decision and metric structure

- User value and business goal:
- Decision this plan supports:
- Source material and dates:
- Outcome metrics and why they were chosen:
- Driver metrics and the expected relationship (labelled hypothesis):
- Guardrail and business metrics:

## Metric dictionary

One entry per M ID. Remove a field only when it clearly does not apply, and say why.

| Field | Definition |
|---|---|
| M ID, name, type | |
| Business meaning, decision supported | |
| Analysis entity, unit, grain | |
| Formula, numerator, denominator | ; count metrics write `no denominator` |
| Eligible population and event conditions | |
| Window, time zone, start / end rule, cohort definition | |
| Deduplication key, repeat / retry rule | |
| Exclusions and segments | |
| Data source, fields, availability | Unknown |
| Refresh frequency and latency | Unknown |
| Zero denominator, missing data, late / partial window handling | |
| Existing baseline, observation period, evidence | Unknown |
| Target, deadline, basis / suggested status | Unknown |
| Linked guardrail M IDs | |
| Definition owner, consumers | Unknown |

## Instrumentation map

| M ID | Source / event | Business meaning of the trigger | Required attributes / object IDs | Deduplication | Evidence or proposal status | Who confirms |
|---|---|---|---|---|---|---|
| M-01 | | | | | To verify | Unknown |

## Instrumentation acceptance scenarios

| Scenario | Input events / conditions | Expected numerator / denominator / count | Data quality state | Status |
|---|---|---|---|---|
| Success / failure / retry and other applicable cases | | | | Planned |

Give boundary examples for windows, identity deduplication and late data; sample data is labelled synthetic.

## Review and response

| M ID | View / segments | Availability and review cadence | Investigation trigger and basis | Suggested owner | First check / follow-up decision |
|---|---|---|---|---|---|
| M-01 | | Unknown | Unknown / suggested | Unknown | |

Product anomalies and collection-quality anomalies are listed separately. Without a threshold basis, record the next step to establish a baseline.

## Open questions

| Question | Affected M IDs | Evidence or confirmation needed | Suggested owner |
|---|---|---|---|
| | | | Unknown |

Status: metrics and instrumentation draft. No events, dashboards or alerts were deployed.
