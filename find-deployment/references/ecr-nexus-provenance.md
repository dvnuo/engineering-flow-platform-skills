# Artifact provenance with ECR and Nexus

The provenance chain answers "is the thing that runs the thing that was built?": **version → Jenkins build → artifact (Nexus) / image (ECR) → digest running in EKS**. Every hop is a command; a hop you cannot make is UNKNOWN, not an assumption.

## The digest chain

1. **Running digest** — what EKS actually pulled, per pod:
   ```bash
   kubectl --context <account>/<cluster> get deploy <name> -n <ns> -o jsonpath='{.spec.template.spec.containers[*].image}'
   kubectl --context <account>/<cluster> get pods -n <ns> -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.containerStatuses[*].imageID}{"\n"}{end}'
   ```
   `.spec...image` is the tag the deployment asked for; `imageID` ends in `@sha256:<digest>` and is what runs. Tag and digest are different facts: a tag can be re-pushed, a digest cannot.
2. **Image in ECR** — resolve the tag, or the digest, to its push time and its other tags:
   ```bash
   aws-auth login --account <registry-account> --json
   aws --profile <registry-account> --region <region> ecr describe-repositories --output json
   aws --profile <registry-account> --region <region> ecr describe-images --repository-name <repo> --image-ids imageTag=<tag> --output json
   aws --profile <registry-account> --region <region> ecr describe-images --repository-name <repo> --image-ids imageDigest=sha256:<digest> --output json
   aws --profile <registry-account> --region <region> ecr describe-images --repository-name <repo> --query 'sort_by(imageDetails,&imagePushedAt)[-10:]' --output json
   ```
   `imageDetails[]` → `imageDigest`, `imagePushedAt`, `imageTags[]`, `imageSizeInBytes`. The repository name is the path after the registry host in the pod's image reference (`<acct>.dkr.ecr.<region>.amazonaws.com/<repo>:<tag>`). The registry account is the one in that hostname; it is often a shared tooling account, not the workload account, so pick it from `aws-auth account list --json` and log in to it separately.
3. **Build in Jenkins** — the build whose parameters or log carry that tag or digest; see [jenkins-deployments.md](jenkins-deployments.md). `imagePushedAt` must fall inside the build's run; if it does not, another build re-pushed the tag.
4. **Artifact in Nexus** — for services deployed from a jar or package, instead of or in addition to an image:
   ```bash
   nexus repo list --json
   nexus component search --repository <repo> --name <artifact> --version <ver> --json
   nexus component search --repository <repo> --repo-format maven2 --maven-group-id <group> --maven-artifact-id <artifact> --maven-base-version <ver> --json
   nexus component search --repository <docker-repo> --repo-format docker --docker-image-name <image> --docker-image-tag <tag> --json
   nexus component get <id> --json
   nexus asset search --repository <repo> --name <artifact> --json
   nexus asset get <id> --json
   ```
   Results page: `data.items[]` and `data.continuation_token`; continue with `--continuation <token>`, or `--all --max-pages 5` once the search is narrow. `component get` lists the component's `assets[]` with `checksum` (`sha1`, `sha256`), `lastModified`, and `downloadUrl`; `--group` narrows by group. `nexus asset download <id> --output <file> --json` returns metadata only, and troubleshooting never needs the file itself.

## Scan findings

```bash
aws --profile <registry-account> --region <region> ecr describe-image-scan-findings --repository-name <repo> --image-id imageTag=<tag> --output json
```

Relevant only when the question is a vulnerability, not a behaviour change. Report `imageScanFindings.findingSeverityCounts`, not the whole list.

## Provenance table

Report the chain as one row per version or workload:

| Version | Jenkins build | Image / artifact | Digest | Pushed | Running pods | Match |
|---|---|---|---|---|---|---|
| 2.4.1 | deploy-payments #812 (SUCCESS, 2026-09-18T09:12Z) | payments-api:2.4.1 | sha256:ab12… | 2026-09-18T09:10Z | 3/3 | yes |
| 2.4.0 | UNKNOWN (no build with IMAGE_TAG=2.4.0 in 7d) | payments-api:2.4.0 | sha256:77fe… | 2026-09-11T14:02Z | 0/3 | — |

"Match" is **yes** only when the digest from `describe-images` equals the digest in every pod's `imageID`. A mixed set of digests across pods is a rollout in progress or a stuck rollout; report both digests and which pods carry each.

## Reading the results

- Tag present in ECR but no pod carries its digest → not deployed, or already replaced; the deployment's events say which.
- Pod digest not found under the tag it was deployed with → the tag was moved after the rollout; the running image is older than the tag suggests.
- `imagePushedAt` after the incident start rules that image out as the trigger.
- `describe-images` answering `ImageNotFoundException` for the deployed tag → the tag is gone (lifecycle policy or manual delete); `ImagePullBackOff` on new pods is the consequence.
- Nexus component found but `assets[].checksum` differs from the deployed artifact's checksum → not the same build; treat the version string as unreliable and say so.

## Never

- `aws ecr put-*`, `batch-delete-image`, `create-repository`, `start-image-scan`, `get-login-password`, or `docker pull`/`push`. The `nexus` CLI has no write or delete commands; do not reach for its raw API.
- Download artifacts or images into the runtime; tags, digests, checksums, and timestamps are the evidence.
- Print registry credentials or Nexus tokens; quote repository names, tags, and digests.
