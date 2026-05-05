# engineering-flow-platform-skills

This repository is the standalone skills source for Engineering Flow Platform (EFP).

## Runtime mount model

Portal checks out this repository into each agent runtime container at:

`/app/skills`

EFP runtime loads skills from that path using `SkillRegistry(project_skills_dir="/app/skills")` and discovers:

- `*.md` at skills root (legacy)
- `<skill_dir>/skill.md` (preferred)

> Important: the repository root **is** the skills root. Do **not** create a nested `skills/` directory.


## OpenCode compatibility model

This repository remains the EFP source skills root.

OpenCode runtime consumes this repository indirectly:
- Portal checks out this repo to /app/skills.
- opencode-runtime reads /app/skills.
- opencode-runtime generates /workspace/.opencode/skills/<normalized-name>/SKILL.md.
- generated .opencode assets must not be committed back to this repo.

Skill names with underscores are allowed as EFP names. The runtime converter normalizes them to OpenCode-compatible hyphen names, for example:

    collect_requirements_to_bundle -> collect-requirements-to-bundle

Every production `skill.md` frontmatter must include the base OpenCode metadata:

```yaml
opencode:
  execution_kind: prompt_only | programmatic | hybrid
  compatibility: full | degraded | unsupported
  permission:
    default: allow | ask | deny
  capability_tags:
    - ...
```

Every skill that declares `tools` or `task_tools` must also declare `opencode.tool_mappings`.

Every skill that declares `tools` or `task_tools` must additionally declare:

```yaml
opencode:
  tool_mappings:
    <native_tool_name>: efp_<native_tool_name>
```

Example:

```yaml
opencode:
  execution_kind: prompt_only
  compatibility: degraded
  permission:
    default: ask
  capability_tags:
    - prompt-only
    - tools-required
  tool_mappings:
    github_get_pr: efp_github_get_pr
    jira_search: efp_jira_search
```

Rules:
- `tools` and `task_tools` keep native EFP tool names.
- `opencode.tool_mappings` maps each native EFP tool name to its OpenCode wrapper name.
- The wrapper name must currently be `efp_<native_tool_name>`.
- This repo does not decide whether the wrapper is enabled at runtime; the Tools repo and opencode-runtime decide availability.
- Skills using tool_mappings should generally keep `opencode.compatibility: degraded` unless the runtime has verified full parity.

- Production skills should not use `permission.default=allow`.
- Prompt-only and tools-required production skills should default to `ask`.
- Native-only / unsupported skills must use `deny`.
- `allow` is reserved for the deterministic integration fixture under `integration/fixtures`.

Python-backed skills (skills that include `skill.py`) execute in native EFP runtime, but OpenCode converter currently does not execute `skill.py`. Therefore those skills must be marked:

```yaml
opencode:
  execution_kind: programmatic
  compatibility: unsupported
  permission:
    default: deny
```

Integration fixtures:
- live under `integration/fixtures`
- are not part of production skills
- support dual-runtime smoke coverage
- may use `permission.default=allow` for deterministic test behavior

## Required repository structure

```text
/app/skills/
  <skill-name>/skill.md
  <skill-name>/skill.py        # optional, for Python-backed legacy/programmatic skills
  shared_bundle_source_loaders.py
  decorator.py
```

- `skill.md` is the SkillRegistry discovery entrypoint.
- `skill.py` is optional implementation code.
- Python-backed skills may import EFP runtime modules such as `src.*` because those are provided by the `engineering-flow-platform` runtime image at execution time.

## Updating skills in deployed agents

After changing skill files in this repo, apply the new code by either:

1. Updating the agent's skill branch/version in Portal, or
2. Restarting the K8s deployment so `/app/skills` is checked out again.

## Minimal `skill.md` template

```yaml
---
name: example-skill
description: Short description
version: 1.0.0
owner: engineering-flow-platform
triggers:
  - /example-skill
  - natural language trigger
tools: []
output_format: markdown
opencode:
  execution_kind: prompt_only
  compatibility: full
  permission:
    default: ask
  capability_tags:
    - prompt-only
---
Body instructions...
```

## Local validation

Run:

```bash
python scripts/validate_skills.py
python scripts/validate_skills.py --opencode-compatible
python scripts/validate_skills.py --root integration/fixtures --opencode-compatible
```

The script verifies:

- Every skill directory containing `skill.py` or `skill.md` has a `skill.md`
- `skill.md` includes required frontmatter fields
- skill names are unique
- referenced files listed in frontmatter `references` exist (best-effort)
- validator fails if a nested `skills/` directory is present


OpenCode compatibility mode (`--opencode-compatible`) also verifies:

- normalized OpenCode skill-name collisions
- `tools`/`task_tools` must be lists (if present)
- `opencode` metadata exists and is a mapping
- `opencode.execution_kind` is one of `prompt_only`, `programmatic`, `hybrid`
- `opencode.compatibility` is one of `full`, `degraded`, `unsupported`
- `opencode.permission.default` is one of `allow`, `ask`, `deny`
- `opencode.capability_tags` is a non-empty list of non-empty strings
- `opencode.tool_mappings` must cover every `tools` / `task_tools` item when those fields are non-empty
- tool mapping values must follow the canonical `efp_<native_tool_name>` wrapper naming rule
- Python-backed skills cannot declare `execution_kind: prompt_only`
- Python-backed skills cannot claim `compatibility: full`
- unsupported skills must use `opencode.permission.default: deny`

Underscore skill names are allowed in this repository; runtime converter normalization maps them to hyphen-form names.


## T13 acceptance commands

Required Skills repo checks:

```bash
python scripts/validate_skills.py
python scripts/validate_skills.py --opencode-compatible
python scripts/validate_skills.py --root integration/fixtures --opencode-compatible
python -m pytest -q
integration/scripts/smoke_skills.sh
```

The T13 CI stage for this repo must pass `python scripts/validate_skills.py --opencode-compatible`.

## Do not commit generated OpenCode assets

Do not commit:
- .opencode/
- .opencode/skills/*/SKILL.md
- skills-index.json

These files are generated by opencode-runtime inside the runtime container.
