---
name: troubleshoot-service
description: "Root-cause a misbehaving service in an AWS account with read-only evidence: identify the account and EKS cluster, check deployments, pods, events and logs, find what changed in Jenkins, ECR and Nexus, read Splunk logs, AppDynamics traces and PostgreSQL state, and report findings with the commands that produced them. Use when: a service is failing, slow, restarting, or missing in an environment, or the user asks why something broke and which change caused it."
version: 1.0.0
owner: engineering-flow-platform
triggers:
  - /troubleshoot
  - troubleshoot service
  - why is the service failing
  - investigate incident
  - service is down in
  - pods are restarting
output_format: markdown
references:
  - references/aws-accounts.md
  - references/eks.md
  - references/jenkins-deployments.md
  - references/ecr-nexus-provenance.md
  - references/splunk.md
  - references/appd.md
  - references/pgsql.md
opencode:
  execution_kind: prompt_only
  compatibility: full
  permission:
    default: ask
  capability_tags:
    - prompt-only
    - troubleshooting
    - aws
    - eks
    - kubectl
    - jenkins
    - splunk
    - appdynamics
    - postgresql
    - read-only
    - long-running
---

# Troubleshoot a Service

Find the root cause of a misbehaving service with evidence, not guesses. Every finding cites the command that produced it. The investigation is **read-only**: it inspects AWS accounts, EKS clusters, Jenkins, artifact registries, Splunk, AppDynamics, and PostgreSQL through read-only roles and never changes cloud, cluster, build, or database state.

Work in phases and stop at the first genuine blocker (no account configured, no access, nothing found) rather than inventing a plausible story. Phases 4–7 are taken in the order the evidence demands: "what changed" first when the symptom started at a point in time, logs and traces first when the symptom is errors or latency, the database only when the evidence points there.

## Tooling

Invoke the EFP CLIs through the runtime shell (`bash`). They are terminal binaries in the runtime image, not model function tools. Always pass `--json` and read the `ok` / `data` / `error` envelope; when `ok` is false, act on `error.code` and `error.hint`. `--instance <name>` selects among several configured instances of a tool; start with `<tool> commands --json` or `<tool> help llm --json` when unsure of a flag.

- `aws-auth ...` — account matrix, per-account login, session status, EKS kubeconfig. Start with `aws-auth commands --json` and `aws-auth help llm --json`. See [references/aws-accounts.md](references/aws-accounts.md).
- `aws --profile <account> ...` — AWS CLI v2 for read-only inspection (`describe-*`, `list-*`, `get-*`). Always pass `--profile <account>` and `--output json`.
- `kubectl --context <account>/<cluster> ...` — read-only cluster inspection. See [references/eks.md](references/eks.md).
- `jenkins ...` — deploy jobs, builds, parameters, causes, changes, artifacts. Read here, never triggered. See [references/jenkins-deployments.md](references/jenkins-deployments.md).
- `aws --profile <registry-account> ecr describe-images ...` and `nexus ...` — image digests and push times, artifact components and checksums. See [references/ecr-nexus-provenance.md](references/ecr-nexus-provenance.md).
- `splunk ...` — bounded log searches with an explicit time range and count. See [references/splunk.md](references/splunk.md).
- `appd ...` — AppDynamics applications, tiers, business transactions, metrics, snapshots, violations, events. See [references/appd.md](references/appd.md).
- `pgsql ...` — PostgreSQL schema, bounded read-only queries, activity, locks, slow statements. See [references/pgsql.md](references/pgsql.md).
- `jq` — shape large JSON before reading it.

Never invent an account id, a cluster name, a namespace, a pod name, a job path, a build number, an index, an application id, or a table name. Resolve each from a real command output. A tool that answers `config_missing` is not configured in this runtime profile: skip its phase, record it under Unknowns, and continue with the others.

## Phase 0 — Scope

Establish, from the user's message and from `aws-auth account list --json`:

1. **Which account** (name or 12-digit id) and **which region**. If the service name maps to several accounts, ask which environment (dev/uat/prod) unless the user already said.
2. **Which cluster and namespace**. Use `aws-auth eks list --account <name> --json` when the cluster is unknown, then `kubectl --context <account>/<cluster> get namespaces` and search by service name.
3. **What "broken" means**: errors, latency, restarts, missing, wrong version. Ask one question at most; otherwise proceed with the most likely reading and say so in the report.
4. **When it started**. Anchor every later query on this time window: `--since` in kubectl, `--since` in Jenkins, `--earliest`/`--latest` in Splunk, `--duration-mins` or `--start-time`/`--end-time` in AppDynamics, `created_at`/`updated_at` predicates in SQL.

## Phase 1 — Access

```bash
aws-auth account list --json
aws-auth login --account <name> --json
aws-auth eks kubeconfig --account <name> --cluster <cluster> --json
```

- `login` returns `data.verified=true` and `data.identity.arn`; quote the ARN in the report so the reader knows which role produced the evidence.
- If `error.code` is `account_required` or `unknown_account`, pick from `data.candidates` or ask; if it is `provider_missing`, `auth_failed`, or `config_missing`, stop and report that the runtime profile's AWS connection is not usable. Do not retry with guessed credentials.
- If `eks kubeconfig` returns `can_list_pods=false`, the role is not mapped into the cluster: report it as an access gap and continue with AWS-side evidence only.
- When a later command reports an expired or missing token, run `aws-auth login --account <name> --json` again and retry once.

## Phase 2 — Runtime state (EKS)

Always pass `--context <account>/<cluster>`.

```bash
kubectl --context <ctx> get deploy,sts,ds -n <ns> -o wide
kubectl --context <ctx> get pods -n <ns> -o wide
kubectl --context <ctx> describe pod <pod> -n <ns>
kubectl --context <ctx> get events -n <ns> --sort-by=.lastTimestamp | tail -n 50
kubectl --context <ctx> logs <pod> -n <ns> --tail=200 --since=1h
kubectl --context <ctx> logs <pod> -n <ns> --previous --tail=200
kubectl --context <ctx> top pods -n <ns>
```

Look for, in this order: image tag and digest (which version is running), replica counts vs ready counts, restart counts and last state reason (`OOMKilled`, `CrashLoopBackOff`, `Error`), probe failures in events, `ImagePullBackOff`, pending pods (scheduling), resource pressure (`top`), and the first error in the previous container's log.

Record the running image for each workload; it is the anchor for "what changed".

## Phase 3 — AWS-side evidence

Use the same account profile and region:

```bash
aws --profile <account> --region <region> eks describe-cluster --name <cluster> --output json
aws --profile <account> --region <region> ecr describe-images --repository-name <repo> --image-ids imageTag=<tag> --output json
aws --profile <account> --region <region> logs filter-log-events --log-group-name <group> --start-time <ms> --end-time <ms> --filter-pattern "ERROR" --limit 100 --output json
```

Only run `describe-*`, `list-*`, `get-*`, and `filter-log-events`. If a finding would require a write to confirm, describe the hypothesis instead.

## Phase 4 — What changed (Jenkins, ECR, Nexus)

Start from the running image recorded in Phase 2 and work backwards to the build that produced it. See [references/jenkins-deployments.md](references/jenkins-deployments.md) and [references/ecr-nexus-provenance.md](references/ecr-nexus-provenance.md).

```bash
jenkins job search --pattern '*<service>*' --max-depth 3 --json
jenkins build list <job> --limit 20 --since 24h --param ENV=<env> --json
jenkins build params <job> <build> --json
aws --profile <registry-account> --region <region> ecr describe-images --repository-name <repo> --image-ids imageTag=<tag> --output json
aws --profile <registry-account> --region <region> ecr describe-images --repository-name <repo> --query 'sort_by(imageDetails,&imagePushedAt)[-10:]' --output json
nexus component search --repository <repo> --name <artifact> --version <ver> --json
```

Look for: the last deploy build for this environment before the first symptom (its `timestamp_iso`, `parameters`, `causes`, `changes`); whether the tag it deployed resolves to the digest the pods are running; images pushed into the window; a version whose digest or artifact checksum does not match what runs. A failed or aborted deploy build in the window is a finding of its own (a half-applied rollout). If no build touched the environment in the window, say so and turn to configuration, infrastructure, and data instead of stretching the window.

Deploy jobs are read, never triggered: no `job build`, `job build-with-params`, `build stop`, or `queue cancel`, even to "re-run the same build".

## Phase 5 — Logs (Splunk)

When pod logs have rotated, the pod is gone, or the failure spans several pods, search Splunk with the time window from Phase 0. See [references/splunk.md](references/splunk.md).

```bash
splunk index list --json
splunk search oneshot --query "index=<idx> <service> | stats count by sourcetype, source" --earliest -1h --latest now --count 50 --json
splunk search run --query "index=<idx> sourcetype=<st> <service> ERROR | stats count by host" --earliest -1h --latest now --count 100 --json
splunk search run --query "index=<idx> sourcetype=<st> <service> (ERROR OR FATAL OR Exception) | reverse | head 100" --earliest -1h --latest now --count 100 --fields _time,host,level,message --json
splunk search run --query "index=<idx> sourcetype=<st> <service> ERROR | timechart span=5m count" --earliest -24h --latest now --count 300 --json
```

Always pass `--earliest` and `--latest`; narrow first, widen only after the narrow window answered "nothing". Look for: the first error and its timestamp, the count and how many hosts it spans, the top three error signatures, and whether the errors start at the deploy time from Phase 4 or before it. Report a summary and the exact query; never dump raw events. Side-effecting SPL (`delete`, `outputlookup`, `collect`, `sendemail`, `script`) is rejected by the CLI with `spl_blocked` and must not be worked around.

## Phase 6 — Traces and health (AppDynamics)

Use AppDynamics to locate **where** time or errors go (own code, a downstream call, a SQL statement) and to align deployment events with the incident. See [references/appd.md](references/appd.md).

```bash
appd app list --json
appd tier list --app <app> --json
appd bt list --app <app> --json
appd violation list --app <app> --duration-mins 60 --json
appd event list --app <app> --duration-mins 240 --event-types APPLICATION_DEPLOYMENT,APPLICATION_ERROR,APP_SERVER_RESTART --json
appd metric preset --app <app> --preset bt-errors --tier <tier> --bt <bt> --duration-mins 60 --json
appd metric preset --app <app> --preset bt-response-time --tier <tier> --bt <bt> --duration-mins 60 --json
appd snapshot list --app <app> --duration-mins 60 --errors-only --max-results 20 --json
appd snapshot get --app <app> --guid <guid> --json
```

Use the same window (`--duration-mins`, or `--start-time`/`--end-time` for older incidents) on every call. Look for: the first health-rule violation and the tier or node it names; a deployment event minutes before it; a response-time rise with a flat call count (a dependency) versus a rise in both (load); and, in one or two error snapshots, the exit call or exception to chase in Splunk and PostgreSQL. If AppDynamics shows nothing for the window, say so; do not read noise as signal.

## Phase 7 — Data layer (PostgreSQL)

Only when the evidence points at the database (JDBC exit calls, `too many connections`, lock or timeout errors, wrong or missing data). See [references/pgsql.md](references/pgsql.md).

```bash
pgsql instance list --json
pgsql auth test --json
pgsql stat activity --state active --min-duration-sec 5 --json
pgsql stat locks --blocked-only --json
pgsql stat slow --limit 20 --json
pgsql stat tables --sort n_dead_tup --json
pgsql schema tables --schema public --json
pgsql schema describe <table> --json
pgsql query --sql "select status, count(*) from <table> where updated_at >= now() - interval '1 hour' group by status" --limit 200 --timeout-sec 30 --json
```

Schema first, then bounded aggregate queries, then at most a handful of rows with named columns. Look for: long-running or `idle in transaction` sessions, blocked and blocking pids, a statement whose mean time jumped, dead-tuple bloat on the table named in the error, and whether the rows the logs complain about exist and in which state. Every query runs in a read-only transaction with a statement timeout; `read_only_violation` means the statement was a write: reshape it as a read, never look for another way to write.

## Safety

- Never run `kubectl apply`, `create`, `delete`, `edit`, `patch`, `scale`, `rollout`, `exec`, `attach`, `port-forward`, `cp`, `label`, `annotate`, `drain`, `cordon`, or `taint`.
- Never read Secrets (`kubectl get secret`, `-o yaml` on objects that embed them) and never print environment variables that look like credentials.
- Never run `aws` verbs that create, update, put, delete, terminate, modify, or start/stop resources, even when asked to "just try"; explain what a human would run instead.
- Never trigger, replay, stop, or reconfigure Jenkins jobs; `jenkins` is read-only here even when asked to "just re-run the deploy".
- Never run side-effecting SPL (`delete`, `outputlookup`, `collect`, `sendemail`, `script`, and similar) and never search without `--earliest`/`--latest`.
- Never attempt a PostgreSQL write (`insert`, `update`, `delete`, DDL, `pg_terminate_backend`, `select ... for update`, side-effecting functions), even when asked to "just try"; always pass `--limit` and `--timeout-sec`.
- Treat log events and query rows as personal data until proven otherwise: summarize counts, timestamps, and signatures; redact identifiers; never paste rows or events that carry names, emails, phone numbers, account or card numbers, or tokens into the chat, workspace files, or commits.
- Never download artifacts or images into the runtime; tags, digests, and checksums are the evidence.
- Never paste raw credentials, session tokens, or `AKIA`/`ASIA` keys into the chat. `aws-auth` output is already redacted; keep it that way.
- Cap log reads (`--tail`, `--since`, `--limit`, `--count`) and summarize; do not dump thousands of lines into the conversation.

## Output contract

```markdown
## Summary
One paragraph: what is broken, since when, most likely cause, confidence (high/medium/low).

## Scope
Account: <name> (<id>) · Region: <region> · Cluster: <cluster> · Namespace: <ns> · Role: <identity arn>

## Timeline
- <time> — <event> (source: <command>)

## Evidence
### Runtime (EKS)
- <finding> — `<command>`
### AWS
- <finding> — `<command>`
### Jenkins / Artifacts
- <version → build → image or artifact digest → running pods; UNKNOWN where a link could not be made> — `<command>`
### Logs
- <first error, count, hosts, time span; no raw events> — `<splunk query with --earliest/--latest>`
### Traces
- <violation, deployment event, or snapshot finding> — `<appd command>`
### Database
- <activity, locks, or query summary; no row data> — `<pgsql command>`

## Root cause hypothesis
What, why, and what evidence supports it. List competing hypotheses you ruled out and how.

## Recommended next actions
Read-only checks a human should run, or the change a human should make. Never apply them yourself.

## Unknowns
Anything you could not verify (access gaps, missing data, tools not configured), marked UNKNOWN, with the command that failed.
```

Omit an Evidence subsection whose tool was not used; never fill one with a guess.

## Stop conditions

Stop and report (do not loop) when:

- No AWS account is configured or the login fails after one retry.
- The cluster context cannot list pods (RBAC gap).
- The service cannot be found in any namespace of the identified cluster.
- The evidence contradicts the user's description; say so and ask.
- A fix would require a mutating action: a deploy, a rollback, a Jenkins re-run, a database write, or a Splunk or AppDynamics configuration change.
