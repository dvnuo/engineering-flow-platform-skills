# Traces and health with `appd`

The `appd` CLI reads AppDynamics through its REST API: applications, tiers, nodes, business transactions (BTs), metrics, snapshots, health-rule violations, and events. It is **read-only**: nothing here acknowledges, silences, or changes a rule. Start with `appd commands --json` or `appd help llm --json`; `--instance <name>` selects a controller when several are configured. Every command takes `--json`.

## Find the application and its parts

```bash
appd app list --json
appd tier list --app <app> --json
appd node list --app <app> --json
appd bt list --app <app> --json
```

Applications carry `id` and `name`; the AppDynamics application is usually the service family or the platform, the **tier** is the service (`payments-api`), and there is one **node** per pod or JVM. BTs carry `id`, `name`, `entryPointType`, `tierName`: the BT is the endpoint or job whose latency and errors you care about. Match names from the user's message against these lists; never invent an id.

## Time flags

Every metric, snapshot, violation, and event call takes `--duration-mins N` (relative to now) or `--start-time <t> --end-time <t>` (epoch milliseconds or RFC3339). Use the explicit form when the incident is older than a few hours, and the **same window** on every call so the numbers line up.

## Health at a glance

```bash
appd violation list --app <app> --duration-mins 60 --json
appd event list --app <app> --duration-mins 240 --event-types APPLICATION_DEPLOYMENT,APPLICATION_ERROR --json
appd event list --app <app> --duration-mins 240 --event-types APP_SERVER_RESTART,APPLICATION_CONFIG_CHANGE,POLICY_OPEN_CRITICAL,POLICY_CLOSE_CRITICAL --json
```

Violations carry the health rule `name`, `severity`, `startTimeInMillis`, `endTimeInMillis`, `affectedEntityDefinition` (tier, node, or BT), and `incidentStatus` (`OPEN`, `RESOLVED`). Events carry `type`, `severity`, `eventTime`, `summary`, `affectedEntities[]`. An `APPLICATION_DEPLOYMENT` event marks when something was released into the monitored application; align it with the Jenkins build timeline.

## Metrics

```bash
appd metric preset --app <app> --preset bt-response-time --tier <tier> --bt <bt> --duration-mins 60 --json
appd metric preset --app <app> --preset bt-calls --tier <tier> --bt <bt> --duration-mins 60 --json
appd metric preset --app <app> --preset bt-errors --tier <tier> --bt <bt> --duration-mins 60 --json
appd metric preset --app <app> --preset tier-cpu --tier <tier> --duration-mins 60 --json
appd metric preset --app <app> --preset node-heap --tier <tier> --duration-mins 60 --json
appd metric get --app <app> --path "Overall Application Performance|<tier>|Average Response Time (ms)" --duration-mins 60 --json
```

Presets cover the usual questions; `metric get --path` takes a full AppDynamics metric path (`|`-separated, as the Metric Browser shows it) for anything else, such as `Application Infrastructure Performance|<tier>|JVM|Garbage Collection|GC Time Spent Per Min (ms)` or `Backends|<backend>|Average Response Time (ms)`. Each metric returns `metricPath` and `metricValues[]` with `startTimeInMillis`, `value`, `min`, `max`, `count`, `sum`. Report the baseline (the first third of the window), the peak, and the time of the first sample above baseline.

## Snapshots

```bash
appd snapshot list --app <app> --duration-mins 60 --errors-only --max-results 20 --json
appd snapshot list --app <app> --duration-mins 60 --user-experience ERROR,VERY_SLOW --tier-ids <id> --max-results 50 --json
appd snapshot list --app <app> --duration-mins 60 --bt-ids <id> --max-results 20 --json
appd snapshot get --app <app> --guid <guid> --json
```

Snapshots carry `requestGUID`, `businessTransactionId`, `applicationComponentId` (tier), `applicationComponentNodeId` (node), `userExperience` (`NORMAL`, `SLOW`, `VERY_SLOW`, `STALL`, `ERROR`), `timeTakenInMilliSecs`, `localStartTime`, `errorOccurred`, `summary`. `snapshot get` adds the call graph, the exit calls (HTTP, JDBC, queue) with their timings, and the error details. One well-chosen snapshot from the first minutes of the incident tells you **where** the time or the error is: in the service's own code, in a downstream HTTP call, or in a SQL statement.

## Align deployments with the incident

1. Take the incident window from Phase 0 and the Jenkins deploy builds from Phase 4.
2. `event list --event-types APPLICATION_DEPLOYMENT` for the window plus a few hours before: a deployment event minutes before the first violation or the first rise in `bt-errors` is the strongest "what changed" signal AppDynamics offers.
3. `violation list` gives the first health rule to open and the tier or node it names; `metric preset` shows whether the whole tier degraded or a single node.
4. `snapshot list --errors-only` from the first minutes, then `snapshot get` on one or two: the exit call or exception named there is what to search in Splunk and, for JDBC, what to look at in PostgreSQL.
5. No deployment event, no violation, flat metrics → AppDynamics does not see the problem (agent missing, tier misnamed, or the failure sits before the service, at the ingress or the load balancer). Say so rather than reading noise as signal.

## Reading the results

- A response-time rise with a flat call count points at a dependency; a rise in both points at load.
- Errors on one node only → that pod, its host, or its restart; check its events and logs by pod name.
- `STALL` snapshots with threads waiting on a pool → connection or thread exhaustion; check `pgsql stat activity` and the pool settings in the timeline.
- A health-rule violation is only as good as its rule: quote the rule's name and threshold with the finding.

## Error codes

| `error.code` | Meaning | What to do |
|---|---|---|
| `instance_required` | several controllers configured, none chosen | pick from `data.candidates`, pass `--instance` |
| `config_missing` / `auth_failed` | no usable AppDynamics credentials in the runtime profile | report the gap; stop |
| `not_found` | application, tier, BT, or snapshot id unknown | list again; ids are per controller |
| `permission_denied` | the read-only user cannot see this application | record as UNKNOWN evidence |
| `invalid_args` | flag misuse (missing time window, bad event type) | read `appd schema <command> --json` and retry once |

## Never

- Attempt a controller write: acknowledging or closing violations, editing health rules, actions, or policies, creating or deleting applications. The CLI has no such commands; do not reach for the REST API with `curl`.
- Read more snapshots than the question needs; keep `--max-results` small, then `snapshot get` on the few that matter.
- Paste full call graphs into the chat; name the slow or failing exit call and its timing.
