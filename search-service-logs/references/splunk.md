# Logs with `splunk`

The `splunk` CLI runs read-only searches against the configured Splunk instance(s) and returns rows as JSON. Every search is bounded: a time range, a result count, and a query shaped to answer one question. Start with `splunk commands --json` or `splunk help llm --json`; `--instance <name>` selects a Splunk when several are configured. Every command takes `--json`.

## Find the index and sourcetype

```bash
splunk index list --json
splunk search oneshot --query "index=<idx> <service> | stats count by sourcetype, source" --earliest -1h --latest now --count 50 --json
```

`index list` → `data.indexes[]` with `name`, `total_event_count`, `earliest_time`, `latest_time`. Service logs usually sit in an index named after the platform or team (`app`, `k8s`, `eks-prod`) with a `sourcetype` per format (`kube:container:<name>`, `json`, `log4j`) and a field naming the service (`service`, `app`, `kubernetes.container_name`, `k8s.container.name`). The `stats count by` probe shows which; do not guess field names into the first real search.

## Shape the query

Narrow first, widen second, never dump:

```bash
# 1. Is there anything in the window, and how much?
splunk search run --query "index=<idx> sourcetype=<st> <service> ERROR | stats count by host" --earliest -1h --latest now --count 100 --json

# 2. The first errors, oldest first, bounded
splunk search run --query "index=<idx> sourcetype=<st> <service> (ERROR OR FATAL OR Exception) | reverse | head 100" --earliest -1h --latest now --count 100 --fields _time,host,level,message --json

# 3. Group the noise into signatures
splunk search run --query 'index=<idx> sourcetype=<st> <service> ERROR | rex field=_raw "(?<sig>[A-Za-z.]+(Exception|Error)[^\n]{0,80})" | stats count, min(_time) as first, max(_time) as last by sig | sort -count' --earliest -1h --latest now --count 50 --json

# 4. Timeline: when did it start?
splunk search run --query "index=<idx> sourcetype=<st> <service> ERROR | timechart span=5m count" --earliest -24h --latest now --count 300 --json
```

Rules:

- `--earliest` and `--latest` are mandatory in practice: pass them on every search (`-15m`, `-1h`, `-24h`, `@d`, or an ISO timestamp). Anchor them on the incident window and widen only after the narrow window answered "nothing here".
- `--count` is capped per instance; ask for what you will read. `data.results_truncated=true` means the cap cut the answer: aggregate (`stats`, `timechart`, `top`) instead of raising the cap.
- `--fields a,b` keeps the rows small; `--output <file>` writes large results to a file inside the workspace so the conversation carries the summary, not the rows.
- `search oneshot` is for quick, small probes; `search run` creates a job and is the default for anything that may take time. For a long job: `splunk search job get <sid> --json`, `splunk search job results <sid> --json`, and `splunk search job cancel <sid> --json` when it is no longer needed.
- Saved searches the team already trusts: `splunk saved list --json`, then `splunk saved run <name> --json`.

## Read the results

`data.results[]` are objects keyed by field (`_time`, `_raw`, `host`, `source`, plus extracted fields); `data.result_count`, `data.results_truncated`, `data.sid`. Report:

1. **First error**: the earliest `_time` of the first signature in the window, with one line of its message.
2. **Count and spread**: how many, on how many hosts or pods, and whether the rate is flat, rising, a burst, or stopped.
3. **Signatures**: the top three distinct messages, each with a count.
4. **The exact query** and time range used, so a human can re-run it.

Never paste raw events into the report. Quote one representative line per signature, with identifiers, tokens, emails, and account numbers replaced by `<redacted>`.

## Common error patterns

| In the logs | Usually means | Confirm with |
|---|---|---|
| `Connection refused`, `UnknownHostException`, `ENOTFOUND` | a dependency is down or its service name changed | `kubectl get svc,endpoints`, the dependency's own logs |
| `timeout`, `ReadTimeout`, `deadline exceeded` | a slow downstream or an exhausted pool | AppDynamics BT response time, `pgsql stat activity` |
| `too many connections`, `pool exhausted`, `remaining connection slots are reserved` | connection leak or a database limit | `pgsql stat activity`, pod restart count |
| `OutOfMemoryError`, `Killed`, `signal 9` | memory limit | `kubectl describe pod` (`OOMKilled`), `kubectl top pods` |
| `401`, `403`, `Unauthorized`, `expired token` | a credential or certificate rotated | the change timeline (Jenkins, configuration), never the secret itself |
| `NoSuchMethodError`, `ClassNotFoundException`, `ModuleNotFoundError` | a bad build or a mismatched dependency | Jenkins build changes, the running image digest |
| `deadlock detected`, `could not serialize access`, `lock timeout` | database contention | `pgsql stat locks --blocked-only` |
| sudden silence (count drops to 0) | the pods stopped logging or stopped running | pod state and events in the same window |

## Error codes

| `error.code` | Meaning | What to do |
|---|---|---|
| `spl_blocked` | the query used a side-effecting command (`delete`, `outputlookup`, `collect`, `sendemail`, `script`, and similar) | reshape the query; never work around the block |
| `instance_required` | several Splunk configured, none chosen | pick from `data.candidates`, pass `--instance` |
| `config_missing` / `auth_failed` | no usable Splunk credentials in the runtime profile | report the gap; stop |
| `permission_denied` | the role cannot read that index | record as UNKNOWN evidence; `index list` shows the readable ones |
| `invalid_args` | flag misuse | read `splunk schema <command> --json` and retry once |

## Never

- Run `delete`, `outputlookup`, `collect`, `sendemail`, `script`, or any command that writes, alerts, or executes; the CLI rejects them and the report says why.
- Search without a time range, or with `--earliest 0` ("all time").
- Paste raw events, stack traces in bulk, or fields that carry personal data into the chat; summarize and redact.
