# Skills integration smoke

This smoke script validates the source Skills repository only.

It checks:
- native EFP skill format
- OpenCode-compatible normalized names
- validator unit tests

It does not:
- generate .opencode/skills
- generate SKILL.md files
- run opencode-runtime
- run native EFP runtime
- connect Kubernetes

Run:

    integration/scripts/smoke_skills.sh
