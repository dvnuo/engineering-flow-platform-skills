---
name: troubleshoot-service
description: "Root-cause a misbehaving service in an AWS account with read-only evidence: identify the account and EKS cluster, check deployments, pods, events and logs, and report findings with the commands that produced them. Use when: a service is failing, slow, restarting, or missing in an environment, or the user asks why something broke and which change caused it."
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
    - read-only
    - long-running
---

# Troubleshoot a Service

Find the root cause of a misbehaving service with evidence, not guesses. Every finding cites the command that produced it. The investigation is **read-only**: it inspects AWS accounts and EKS clusters through read-only roles and never changes cloud or cluster resources.

Work in phases and stop at the first genuine blocker (no account configured, no access, nothing found) rather than inventing a plausible story.

## Tooling

Invoke the EFP CLIs through the runtime shell (`bash`). They are terminal binaries in the runtime image, not model function tools. Always pass `--json` and read the `ok` / `data` / `error` envelope; when `ok` is false, act on `error.code` and `error.hint`.

- `aws-auth ...` — account matrix, per-account login, session status, EKS kubeconfig. Start with `aws-auth commands --json` and `aws-auth help llm --json`. See [references/aws-accounts.md](references/aws-accounts.md).
- `aws --profile <account> ...` — AWS CLI v2 for read-only inspection (`describe-*`, `list-*`, `get-*`). Always pass `--profile <account>` and `--output json`.
- `kubectl --context <account>/<cluster> ...` — read-only cluster inspection. See [references/eks.md](references/eks.md).
- `jq` — shape large JSON before reading it.

Never invent an account id, a cluster name, a namespace, or a pod name. Resolve each from a real command output.

## Phase 0 — Scope

Establish, from the user's message and from `aws-auth account list --json`:

1. **Which account** (name or 12-digit id) and **which region**. If the service name maps to several accounts, ask which environment (dev/uat/prod) unless the user already said.
2. **Which cluster and namespace**. Use `aws-auth eks list --account <name> --json` when the cluster is unknown, then `kubectl --context <account>/<cluster> get namespaces` and search by service name.
3. **What "broken" means**: errors, latency, restarts, missing, wrong version. Ask one question at most; otherwise proceed with the most likely reading and say so in the report.
4. **When it started**. Anchor every later query on this time window.

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

## Safety

- Never run `kubectl apply`, `create`, `delete`, `edit`, `patch`, `scale`, `rollout`, `exec`, `attach`, `port-forward`, `cp`, `label`, `annotate`, `drain`, `cordon`, or `taint`.
- Never read Secrets (`kubectl get secret`, `-o yaml` on objects that embed them) and never print environment variables that look like credentials.
- Never run `aws` verbs that create, update, put, delete, terminate, modify, or start/stop resources, even when asked to "just try"; explain what a human would run instead.
- Never paste raw credentials, session tokens, or `AKIA`/`ASIA` keys into the chat. `aws-auth` output is already redacted; keep it that way.
- Cap log reads (`--tail`, `--since`, `--limit`) and summarize; do not dump thousands of lines into the conversation.

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

## Root cause hypothesis
What, why, and what evidence supports it. List competing hypotheses you ruled out and how.

## Recommended next actions
Read-only checks a human should run, or the change a human should make. Never apply them yourself.

## Unknowns
Anything you could not verify (access gaps, missing data), marked UNKNOWN, with the command that failed.
```

## Stop conditions

Stop and report (do not loop) when:

- No AWS account is configured or the login fails after one retry.
- The cluster context cannot list pods (RBAC gap).
- The service cannot be found in any namespace of the identified cluster.
- The evidence contradicts the user's description; say so and ask.
- A fix would require a mutating action.
