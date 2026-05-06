# Skills integration smoke

This smoke script validates the source Skills repository only.

It checks:
- production root native EFP skill format
- production root OpenCode-compatible metadata and normalized names
- integration fixtures OpenCode-compatible metadata
- validator and contract exporter unit tests
- machine-readable contract export for production and fixtures to a temporary directory

Integration fixture note:
- `integration/fixtures/opencode-deterministic-fixture/skill.md` is intentionally not part of production skills.
- It may use `permission.default=allow` because it is deterministic and only used by smoke/integration checks.
- It must not call tools and must return `EFP_SKILL_FIXTURE_OK` when invoked by future runtime-level smoke tests.

It does not:
- generate .opencode/skills
- generate SKILL.md files
- run opencode-runtime
- run native EFP runtime
- generate .opencode artifacts
- connect Kubernetes

Run:

    integration/scripts/smoke_skills.sh


Contract export in smoke is metadata-only: it does not generate `.opencode/` and does not run any runtime adapter.
