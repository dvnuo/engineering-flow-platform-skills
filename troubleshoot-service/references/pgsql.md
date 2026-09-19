# Data layer with `pgsql`

The `pgsql` CLI queries the configured PostgreSQL instance(s) inside a **read-only transaction with a statement timeout**. Writes, DDL, and side-effecting functions are rejected with `read_only_violation`; no flag lifts that. Start with `pgsql commands --json` or `pgsql help llm --json`; `--instance <name>` selects a database when several are configured. Every command takes `--json`.

## Connect

```bash
pgsql instance list --json
pgsql auth test --json
```

`instance list` names the configured databases (`name`, `host`, `database`, `default`), never their passwords. `auth test` proves the credentials and reports the server version and the role; quote the role in the report. When `auth test` fails, report the runtime profile gap and stop; do not ask for a password.

## Schema first

```bash
pgsql schema tables --schema public --json
pgsql schema describe <table> --json
```

`schema describe` → columns (`name`, `type`, `nullable`, `default`), primary key, indexes, foreign keys, and the row estimate. Read it before writing a query: it gives the real column names, which columns are indexed (so a bounded query stays cheap), and which columns hold personal data (`email`, `phone`, `name`, `address`, `dob`, `ssn`, `card`, `token`, `password_hash`) so you can leave them out of `select`.

## Bounded queries

```bash
pgsql query --sql "select count(*) from orders where created_at >= now() - interval '1 hour'" --limit 200 --timeout-sec 30 --json
pgsql query --sql "select status, count(*) from orders where created_at >= now() - interval '1 hour' group by status order by 2 desc" --limit 200 --timeout-sec 30 --json
pgsql query --sql "select id, status, updated_at from orders where status = 'STUCK' order by updated_at desc" --limit 50 --timeout-sec 30 --json
pgsql explain --sql "select id from orders where customer_ref = 'abc'" --json
```

- Always pass `--limit` and `--timeout-sec`. Rows come back as objects keyed by column (`data.rows[]`), with `data.row_count` and `data.rows_truncated`.
- Name the columns; never `select *` on a table you have not described.
- Filter on an indexed column and a time range; run `pgsql explain` before any query on a large table (a `Seq Scan` over millions of rows is a query to rewrite, not to run).
- Aggregate (`count`, `group by`, `min`/`max` of timestamps) before fetching rows; fetch rows only to show a representative case, and then only the columns needed.
- Ask questions the data can answer: "how many orders are stuck since 09:00", "when was the last successful row", "does the reference the log complains about exist".
- A statement that exceeds `--timeout-sec` comes back as an error whose `hint` says so: narrow the filter, add an indexed predicate, or aggregate; do not raise the timeout past 60 seconds.

## Server state

```bash
pgsql stat activity --state active --min-duration-sec 5 --json
pgsql stat locks --blocked-only --json
pgsql stat slow --limit 20 --json
pgsql stat tables --sort n_dead_tup --json
pgsql db size --json
```

- `stat activity` → `pid`, `usename`, `application_name`, `client_addr`, `state`, `wait_event_type`, `wait_event`, `duration_sec`, `query` (truncated). Many `active` rows with the same query and a growing `duration_sec` is a slow statement; many `idle in transaction` rows is a leak in the application; a count near `max_connections` explains `too many connections` in the logs.
- `stat locks --blocked-only` → the blocked `pid`, the blocking `pid`, the lock type, the relation, and both queries. A long `ALTER TABLE`, a batch job, or an `idle in transaction` session holding a lock are the usual blockers; report the blocker's `application_name` and start time, not just the victim.
- `stat slow` reads `pg_stat_statements` (`calls`, `mean_exec_time_ms`, `total_exec_time_ms`, `rows`, normalized `query`); `has_report=false` means the extension is not installed: say so and fall back to `stat activity`.
- `stat tables --sort n_dead_tup` → bloat and autovacuum lag (`n_dead_tup`, `n_live_tup`, `last_autovacuum`, `last_analyze`); millions of dead tuples and an old `last_autovacuum` explain a sudden plan change.
- `db size` → database and largest-table sizes; compare with the volume when the symptom is `No space left on device`.

## PII discipline

- Describe the schema, then select only the columns the question needs; leave personal-data columns out unless the question is about that column, and then aggregate (`count`, `min`, `max`, `length`) instead of reading values.
- Never paste rows that contain names, emails, phone numbers, addresses, national ids, card numbers, tokens, or hashes into the chat, a file in the workspace, or a commit. Summarize: "12 rows, all created between 09:02 and 09:04, all in status PENDING".
- When a single row must be shown, show the technical columns (`id`, `status`, timestamps, foreign keys) and replace the rest with `<redacted>`.
- Do not copy query results into `output/` files unless the user asked for an export and the columns are free of personal data.

## Error codes

| `error.code` | Meaning | What to do |
|---|---|---|
| `read_only_violation` | the statement writes, changes schema, or calls a side-effecting function | reshape as a read; never retry with a different form of the same write |
| `instance_required` | several databases configured, none chosen | pick from `data.candidates`, pass `--instance` |
| `config_missing` / `auth_failed` | no usable database credentials in the runtime profile | report the gap; stop |
| `permission_denied` | the read-only role cannot read this relation | record as UNKNOWN evidence |
| `invalid_args` | flag misuse (missing `--sql`, bad `--limit`) | read `pgsql schema <command> --json` and retry once |

## Never

- `insert`, `update`, `delete`, `truncate`, `create`, `alter`, `drop`, `grant`, `vacuum`, `analyze`, `reindex`, `refresh materialized view`, `copy`, `set`/`reset` of session settings, `select ... for update`, `pg_terminate_backend`, `pg_cancel_backend`, `pg_sleep`, `nextval`, `setval`, `lo_*`, or any function that writes, even when asked to "just try". The CLI rejects them, and the report names the human action needed instead.
- `select *`, unbounded queries, or queries without `--limit` and `--timeout-sec`.
- Paste rows with personal data anywhere.
