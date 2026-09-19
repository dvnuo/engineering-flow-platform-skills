# EKS with `aws-auth eks` and `kubectl`

## Get a context

```bash
aws-auth eks list --account <name> [--region <region>] --json
aws-auth eks kubeconfig --account <name> --cluster <cluster> [--region <region>] --json
```

`eks kubeconfig` writes a kubectl context named `<account>/<cluster>` into the managed kubeconfig (`KUBECONFIG`, outside the workspace) and reports `data.can_list_pods`. The context authenticates with the account's AWS profile through `aws eks get-token`, so an expired AWS session shows up as a kubectl authentication error: run `aws-auth login --account <name> --json` again.

`can_list_pods=false` means the read-only role is not mapped into that cluster (no access entry / RBAC binding). Report it as an access gap; do not try other credentials.

## Always pass the context

Every kubectl command names the context and the namespace:

```bash
kubectl --context <account>/<cluster> get pods -n <ns> -o wide
```

## Read-only verbs

Allowed: `get`, `describe`, `logs`, `events`, `top`, `explain`, `api-resources`, `version`, `auth can-i`, `config get-contexts`, `config current-context`.

Forbidden: `apply`, `create`, `delete`, `edit`, `patch`, `replace`, `scale`, `rollout`, `exec`, `attach`, `port-forward`, `cp`, `label`, `annotate`, `drain`, `cordon`, `uncordon`, `taint`, `set`, and anything with `--force`. Never `get secret`/`get secrets`, and never print `env` blocks that look like credentials.

## Triage sequence

1. **Workloads and images** — which version is running and whether the rollout completed:
   ```bash
   kubectl --context <ctx> get deploy,sts,ds -n <ns> -o wide
   kubectl --context <ctx> get deploy <name> -n <ns> -o jsonpath='{.spec.template.spec.containers[*].image}'
   kubectl --context <ctx> get pods -n <ns> -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.containerStatuses[*].imageID}{"\n"}{end}'
   ```
2. **Pod state** — restarts, waiting/terminated reasons, probe failures:
   ```bash
   kubectl --context <ctx> get pods -n <ns> -o wide
   kubectl --context <ctx> describe pod <pod> -n <ns>
   ```
   `OOMKilled` → memory limit; `CrashLoopBackOff`/`Error` → read the previous container log; `ImagePullBackOff` → image tag/digest and ECR; `Pending` → events for scheduling reasons.
3. **Events** — the cluster's own narrative for the window:
   ```bash
   kubectl --context <ctx> get events -n <ns> --sort-by=.lastTimestamp | tail -n 50
   ```
4. **Logs** — bounded, from the failing window:
   ```bash
   kubectl --context <ctx> logs <pod> -n <ns> --tail=200 --since=1h
   kubectl --context <ctx> logs <pod> -n <ns> --previous --tail=200
   kubectl --context <ctx> logs deploy/<name> -n <ns> --all-containers --tail=100
   ```
   Always cap with `--tail` and/or `--since`; summarize the first error and its timestamp instead of pasting the log.
5. **Resources** — pressure and limits:
   ```bash
   kubectl --context <ctx> top pods -n <ns>
   kubectl --context <ctx> top nodes
   ```
   `top` needs the metrics API; when it is unavailable, say so and rely on `describe` and events.
6. **Networking** — only when symptoms point there:
   ```bash
   kubectl --context <ctx> get svc,endpoints,ingress -n <ns>
   kubectl --context <ctx> describe svc <name> -n <ns>
   ```

## Reading the results

- Compare the running image digest with what should be deployed; a mismatch or a mixed set across pods is a rollout problem.
- A restart storm that started at a specific time usually aligns with an event (new image, config change, node pressure). Put that time in the report's timeline.
- Probe failures with a healthy process point at readiness thresholds or downstream dependencies, not the pod itself.
- Record every command that returned an error as UNKNOWN evidence rather than filling the gap with assumptions.
