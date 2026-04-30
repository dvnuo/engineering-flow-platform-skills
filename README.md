# engineering-flow-platform-skills

This repository is the standalone skills source for Engineering Flow Platform (EFP).

## Runtime mount model

Portal checks out this repository into each agent runtime container at:

`/app/skills`

EFP runtime loads skills from that path using `SkillRegistry(project_skills_dir="/app/skills")` and discovers:

- `*.md` at skills root (legacy)
- `<skill_dir>/skill.md` (preferred)

> Important: the repository root **is** the skills root. Do **not** create a nested `skills/` directory.

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
---
Body instructions...
```

## Local validation

Run:

```bash
python scripts/validate_skills.py
```

The script verifies:

- Every skill directory containing `skill.py` or `skill.md` has a `skill.md`
- `skill.md` includes required frontmatter fields
- skill names are unique
- referenced files listed in frontmatter `references` exist (best-effort)
- validator fails if a nested `skills/` directory is present
