---
name: find-deployment
description: "Establish what is deployed for a service and where it came from: the Jenkins deploy job and build, its parameters and changes, the artifact in Nexus or the image in ECR, and the image digest actually running in EKS, reported as a provenance chain with the commands as evidence. Use when: the user asks which build is deployed, what version is running, when something was deployed, or whether the running image matches a build. Read-only."
version: 1.0.0
owner: engineering-flow-platform
triggers:
  - /find-deployment
  - which build deployed
  - what version is running
  - when was it deployed
  - find the deployment
output_format: markdown
references:
  - references/jenkins-deployments.md
  - references/ecr-nexus-provenance.md
opencode:
  execution_kind: prompt_only
  compatibility: full
  permission:
    default: ask
  capability_tags:
    - prompt-only
    - troubleshooting
    - jenkins
    - nexus
    - ecr
    - eks
    - read-only
---

# Find a Deployment

Answer "what is deployed, since when, and where did it come from" with a provenance chain, not a guess: **version → Jenkins build → artifact (Nexus) / image (ECR) → digest running in EKS**. Every hop cites the command that established it; a hop you cannot establish is UNKNOWN. The skill is **read-only**: it never triggers a build, pushes an image, or touches the cluster.

## Tooling

Invoke the EFP CLIs through the runtime shell (`bash`). They are terminal binaries in the runtime image, not model function tools. Always pass `--json` and read the `ok` / `data` / `error` envelope; when `ok` is false, act on `error.code` and `error.hint`. `--instance <name>` selects among several configured Jenkins or Nexus instances; start with `<tool> commands --json` or `<tool> help llm --json` when unsure of a flag.

- `jenkins job search`, `build list`, `build params`, `build artifacts`, `build status` — see [references/jenkins-deployments.md](references/jenkins-deployments.md).
- `aws-auth login --account <name> --json`, then `aws --profile <name> --region <region> ecr describe-images ...` — see [references/ecr-nexus-provenance.md](references/ecr-nexus-provenance.md).
- `nexus repo list`, `component search`, `component get`, `asset get` — same reference.
- `aws-auth eks kubeconfig --account <name> --cluster <cluster> --json`, then `kubectl --context <account>/<cluster> get ... -o jsonpath` for the running digest.
- `jq` — shape large JSON before reading it.

Never invent a job path, a build number, a tag, a digest, or a pod name. Resolve each from a real command output.

## Phase 0 — Scope

From the user's message, establish:

1. **Service** and, when given, **environment** (dev/uat/prod) and **version** (tag, semantic version, or commit). If the environment is missing and the service is deployed to several, ask which one; one question at most, otherwise proceed with the most likely reading and say so in the report.
2. **Registry and repository**: from the running image reference in the cluster when the cluster is known, otherwise from the Jenkins build parameters.
3. **The question**: "what runs now" (start from the cluster), "when was version X deployed" (start from Jenkins), or "does the running image match build N" (both ends, meet in the middle).

## Phase 1 — Jenkins: job and build

```bash
jenkins job search --pattern '*<service>*' --max-depth 3 --json
jenkins build list <job> --limit 20 --param ENV=<env> --json
jenkins build list <job> --limit 50 --since 7d --result SUCCESS --json
jenkins build params <job> <build> --json
jenkins build artifacts <job> <build> --json
```

Read one build's `parameters{}` before filtering on a parameter name; names differ per job (`ENV`, `TARGET_ENV`, `VERSION`, `IMAGE_TAG`). Record for each candidate build: number, `result`, `timestamp_iso`, the version or tag parameter, `causes[]` (who or what started it), and `changes[]` (commits). When the version is only in the console, `jenkins build log <job> <build> --json` and search `data.text` for the image reference; do not read it end to end.

## Phase 2 — Artifact and image

```bash
aws-auth login --account <registry-account> --json
aws --profile <registry-account> --region <region> ecr describe-images --repository-name <repo> --image-ids imageTag=<tag> --output json
aws --profile <registry-account> --region <region> ecr describe-images --repository-name <repo> --query 'sort_by(imageDetails,&imagePushedAt)[-10:]' --output json
nexus component search --repository <repo> --name <artifact> --version <ver> --json
nexus component get <id> --json
```

Record `imageDigest`, `imagePushedAt`, and every `imageTags[]` entry for the image; for a Nexus artifact, the component id, `assets[].checksum`, and `lastModified`. `imagePushedAt` must fall inside the build's run; if it does not, another build re-pushed the tag and the tag no longer identifies that build. The registry account is the one in the image hostname and is often not the workload account; pick it from `aws-auth account list --json`.

## Phase 3 — What is running

```bash
aws-auth eks kubeconfig --account <workload-account> --cluster <cluster> --json
kubectl --context <workload-account>/<cluster> get deploy <name> -n <ns> -o jsonpath='{.spec.template.spec.containers[*].image}'
kubectl --context <workload-account>/<cluster> get pods -n <ns> -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.containerStatuses[*].imageID}{"\n"}{end}'
```

Compare the digest in each pod's `imageID` with the digest from ECR. All pods on the build's digest → deployed; a mixed set → rollout in progress or stuck (say which pods carry which digest); no pod on it → not deployed or already replaced. When `describe-images` by digest finds the running image under a different tag, report the image as running under a moved tag.

## Safety

- Never `jenkins job build`, `job build-with-params`, `build stop`, `queue cancel`, or any `job`/`view`/`system` write; deployments are found here, never made or repeated, even when asked to "just re-run it".
- Never `aws ecr put-*`, `batch-delete-image`, `start-image-scan`, or `get-login-password`; never `docker pull`/`push`; never `nexus asset download` unless the user explicitly asks for the file.
- `kubectl` is limited to `get` and `describe`; never `rollout`, `set image`, `scale`, `apply`, `delete`, `exec`, or `get secret`.
- Quote build numbers, tags, digests, and checksums; never credentials, tokens, or registry passwords.

## Output contract

```markdown
## Answer
One paragraph: what is running (version, digest, since when), which build produced it, and confidence (high/medium/low).

## Provenance
| Version | Jenkins build | Image / artifact | Digest / checksum | Pushed | Running pods | Match |
|---|---|---|---|---|---|---|
| <ver> | <job> #<n> (<result>, <timestamp>) | <repo>:<tag> | sha256:<12 chars>… | <time> | <n>/<total> | yes / no / mixed / UNKNOWN |

## Build details
- Started by: <cause> · Parameters: <the ones that matter> · Changes: <count>, newest <commit> "<message>" by <author>

## Evidence
- <finding> — `<command>`

## Unknowns
Links that could not be established, marked UNKNOWN, with the command that failed or returned nothing.
```

## Stop conditions

Stop and report (do not loop) when:

- No deploy job matches the service after searching by service name and by `*deploy*`/`*release*`.
- Jenkins, Nexus, or the registry account is not configured or the login fails after one retry (`config_missing`, `auth_failed`).
- The cluster context cannot list pods; report the Jenkins and registry side of the chain and mark the running side UNKNOWN.
- The user asks to deploy, redeploy, roll back, or retag; describe the job and parameters a human would use instead.
