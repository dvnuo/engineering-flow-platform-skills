---
name: search-service-logs
description: "Search a service's logs in Splunk over a bounded time window, starting narrow (index, sourcetype, service, head or stats) and widening carefully, and report the first error, the count, the time span, the top signatures, and the exact query used, without dumping raw events. Use when: the user asks what the logs say, wants errors found in Splunk, or needs a log search for an incident window. Read-only."
version: 1.0.0
owner: engineering-flow-platform
triggers:
  - /search-logs
  - search logs
  - what do the logs say
  - find errors in splunk
output_format: markdown
references:
  - references/splunk.md
opencode:
  execution_kind: prompt_only
  compatibility: full
  permission:
    default: ask
  capability_tags:
    - prompt-only
    - troubleshooting
    - splunk
    - logs
    - read-only
---

# Search Service Logs

Answer "what do the logs say" with a summary a human can act on and re-run: the first error and when it happened, how many, on how many hosts, the top signatures, and the exact SPL with its time range. Every search is bounded by an explicit time window and a result count. The skill is **read-only** and never runs side-effecting SPL.

## Tooling

Invoke the `splunk` CLI through the runtime shell (`bash`). It is a terminal binary in the runtime image, not a model function tool. Always pass `--json` and read the `ok` / `data` / `error` envelope; when `ok` is false, act on `error.code` and `error.hint`. `--instance <name>` selects among several configured Splunk instances; start with `splunk commands --json` or `splunk help llm --json` when unsure of a flag. See [references/splunk.md](references/splunk.md) for query shaping, caps, and common error patterns.

Never invent an index, a sourcetype, or a field name. Resolve each from `index list` and a `stats count by` probe.

## Phase 0 — Scope

From the user's message, establish:

1. **Service**, as it appears in the logs (container name, `service` field, or application name).
2. **Time window**. Default to the last hour when the user gives none, and say so; for an incident, anchor on its start and take 15 minutes before it.
3. **What to look for**: errors (default), a specific message or exception, a request or correlation id, or a count over time.
4. **Index and sourcetype** when the user knows them; otherwise find them in Phase 1.

Ask one question at most; otherwise proceed with the most likely reading and state the assumption in the report.

## Phase 1 — Find the index and sourcetype

```bash
splunk index list --json
splunk search oneshot --query "index=<idx> <service> | stats count by sourcetype, source" --earliest -1h --latest now --count 50 --json
```

Pick the index whose name matches the platform or team and whose `latest_time` is recent; the probe shows which sourcetype and which field carries the service name. Zero results in the probe: try the next candidate index or a looser service string (`*<service>*`) before widening the time range.

## Phase 2 — Narrow first search

```bash
splunk search run --query "index=<idx> sourcetype=<st> <service> ERROR | stats count by host" --earliest <start> --latest <end> --count 100 --json
splunk search run --query "index=<idx> sourcetype=<st> <service> (ERROR OR FATAL OR Exception) | reverse | head 100" --earliest <start> --latest <end> --count 100 --fields _time,host,level,message --json
```

One question per query: first "how many and where", then "the earliest hundred". `--earliest`/`--latest` are always passed; `--count` stays at or below what you will read; `--fields` keeps rows small. When `data.results_truncated` is true, aggregate instead of raising the count.

## Phase 3 — Widen carefully

Only when the narrow search answered "nothing" or "not enough":

```bash
splunk search run --query 'index=<idx> sourcetype=<st> <service> ERROR | rex field=_raw "(?<sig>[A-Za-z.]+(Exception|Error)[^\n]{0,80})" | stats count, min(_time) as first, max(_time) as last by sig | sort -count' --earliest <start> --latest <end> --count 50 --json
splunk search run --query "index=<idx> sourcetype=<st> <service> ERROR | timechart span=5m count" --earliest -24h --latest now --count 300 --json
splunk search run --query "index=<idx> sourcetype=<st> <service> WARN | head 50" --earliest <start> --latest <end> --count 50 --json
```

Widen one dimension at a time: the time range (hour → day), the level (ERROR → WARN), or the service filter (exact → wildcard). Say which dimension was widened and why. Large results go to `--output <file>` inside the workspace; the chat gets the summary.

## Phase 4 — Summarize

Report:

1. **First error**: the earliest `_time` in the window, the host or pod, and one redacted line of the message.
2. **Count and spread**: total, hosts affected, and the shape over time (flat, rising, burst, stopped).
3. **Top signatures**: up to three distinct messages with counts.
4. **The exact query** (SPL, `--earliest`, `--latest`, `--count`, instance) behind every number quoted, so a human can re-run it.

Never paste raw events. One representative line per signature, with identifiers, tokens, emails, and account numbers replaced by `<redacted>`.

## Safety

- Never run side-effecting SPL (`delete`, `outputlookup`, `collect`, `sendemail`, `script`, `dump`, and similar); the CLI rejects them with `spl_blocked`, and the answer is to reshape the query, not to work around the block. A backtick macro is refused the same way, because Splunk expands it after the check: write the search out in full.
- Never search without `--earliest` and `--latest`, and never with `--earliest 0` ("all time").
- Cap every search with `--count` and summarize; do not dump thousands of rows into the conversation.
- Treat events as personal data until proven otherwise; redact before quoting.

## Output contract

```markdown
## Summary
One paragraph: what the logs show for <service> between <start> and <end>, and confidence (high/medium/low).

## First error
- <time> · <host/pod> · `<redacted line>` — `<query>`

## Counts
- <total> events on <n> hosts; <shape over time> — `<query>`

## Signatures
| Signature | Count | First | Last |
|---|---|---|---|

## Queries used
- `splunk search run --query "<spl>" --earliest <start> --latest <end> --count <n> --json`

## Unknowns
Indexes or fields that could not be resolved and searches that returned nothing, marked UNKNOWN, with the query that failed.
```

## Stop conditions

Stop and report (do not loop) when:

- Splunk is not configured or the login fails after one retry (`config_missing`, `auth_failed`).
- No index contains the service in the window after two candidate indexes and one wildcard probe; say which were tried.
- A search returns `spl_blocked` or `permission_denied`; report the query and the code rather than trying variants.
- The user asks for something beyond a search (an alert, a saved-search change, a lookup update); describe what a human would do in Splunk instead.
