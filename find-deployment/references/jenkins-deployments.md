# Deployments with `jenkins`

Jenkins is where a version becomes a deployment. In troubleshooting the `jenkins` CLI is **read-only**: it finds the deploy job, lists the builds that touched an environment, and reads each build's parameters, causes, and changes. It never triggers, replays, stops, or reconfigures a build.

Start with `jenkins commands --json` or `jenkins help llm --json` when unsure of a flag; `--instance <name>` selects a Jenkins when several are configured. Every command takes `--json`.

## Find the deploy job

```bash
jenkins job search --pattern '*<service>*' --max-depth 3 --json
jenkins job search --pattern '*deploy*' --max-depth 3 --json
```

`data.jobs[]` → `name`, `full_name` (folder path), `url`, `buildable`. The folder path is the `<job>` argument for every later command. Search with the service name first, then with `*deploy*`, `*release*`, `*promote*`; when several jobs match, list the last builds of each and keep the one whose parameters name the environment. Raise `--max-depth` only when nothing matches.

## List the builds that touched the environment

```bash
jenkins build list <job> --limit 20 --json
jenkins build list <job> --limit 20 --param ENV=prod --json
jenkins build list <job> --limit 50 --since 24h --json
jenkins build list <job> --limit 50 --result SUCCESS --since 7d --param ENV=prod --json
```

`data.builds[]` → `number`, `result` (`SUCCESS`, `FAILURE`, `UNSTABLE`, `ABORTED`; empty while running), `timestamp_iso`, `duration_ms`, `parameters{}`, `causes[]`, `url`. Filters combine: `--result`, `--since <24h|7d|ISO time>`, `--param NAME=value` (repeatable, matched against the build's own parameters). Parameter names differ per job (`ENV`, `ENVIRONMENT`, `TARGET_ENV`, `VERSION`, `IMAGE_TAG`, `BRANCH`): read one build's `parameters{}` before filtering on a name.

## Read one build

```bash
jenkins build params <job> <build> --json
jenkins build status <job> <build> --json
jenkins build artifacts <job> <build> --json
jenkins build test-report <job> <build> --json
```

`build params` → `data.parameters{}`, `data.causes[]` (who or what started it: a user, an upstream job, an SCM change, a timer), `data.changes[]` with `commit`, `message`, `author`. The deployed version is usually a parameter (`VERSION`, `IMAGE_TAG`, `ARTIFACT_VERSION`) or the newest change's commit; artifact file names from `build artifacts` often carry it too.

`jenkins build log <job> <build> --json` returns the **whole** console text in `data.text`. Use it last, only when parameters and artifacts do not answer the question, and search it for the pushed image reference or the rollout line rather than reading it top to bottom:

```bash
jenkins build log <job> <build> --json | jq -r .data.text | grep -n -E 'sha256:|image:|helm upgrade|set image' | head -n 20
```

## Correlate with the incident window

1. Take the incident start time from Phase 0.
2. From `build list --since ...`, keep the builds for the same environment whose `timestamp_iso` (plus `duration_ms`) lands **before** the first symptom. The nearest one is the prime suspect; later ones are noise or attempted fixes.
3. For the suspect, `build params` gives version, changes, and cause. Compare its version with the image digest running in the cluster (see [ecr-nexus-provenance.md](ecr-nexus-provenance.md)).
4. A successful build whose version does not match the running pods means the rollout did not complete or was rolled back; say which, from pod evidence.
5. A `FAILURE` or `ABORTED` deploy build inside the window is evidence too: it can leave some pods on the new image and some on the old.

## Reading the results

- No build in the window → the change came from elsewhere (configuration, infrastructure, data, a dependency). Say so; do not widen the window silently.
- `causes[]` naming a user tells you whom to ask; an upstream-job cause means read that job's build.
- `changes[]` empty on a deploy build usually means the version was chosen by parameter, not by commit: follow the parameter to Nexus or ECR.
- Quote build numbers and URLs in the report, never credentials or environment values that appear in a console log.

## Error codes

| `error.code` | Meaning | What to do |
|---|---|---|
| `instance_required` | several Jenkins configured, none chosen | pick from `data.candidates`, pass `--instance` |
| `config_missing` / `auth_failed` | no usable Jenkins credentials in the runtime profile | report the gap; stop |
| `not_found` | job path or build number wrong | search again with `job search`; check the folder path |
| `permission_denied` | the read-only account cannot see this job | record as UNKNOWN evidence |
| `invalid_args` | flag misuse | read `jenkins schema <command> --json` and retry once |

## Never

- `job build`, `job build-with-params`, `build stop`, `queue cancel`, `job create/copy/delete/enable/disable`, `job config update`, `system ...`, `api post/put/delete`. Deployments are read here, never triggered or replayed, even when asked to "just re-run it"; name the job and parameters a human would use instead.
- Guess a job path or build number; resolve both from command output.
