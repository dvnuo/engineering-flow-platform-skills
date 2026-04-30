---
name: generate_runbook_from_bundle
description: Produces an operational runbook artifact from bundle context for rollout, rollback, and monitoring readiness.
version: 1.0.0
owner: engineering-flow-platform
triggers:
  - /generate_runbook_from_bundle
  - generate runbook from bundle
  - create operational runbook yaml
tools: []
output_format: markdown
---
Use this skill to generate operational guidance from requirement bundle context.

## Inputs expected

- `bundle_ref`: target bundle repo/path/branch reference.
- `manifest_ref` (optional): explicit manifest location.

## Output

- Writes the configured runbook YAML artifact.
- Returns updated file metadata and commit SHA.

## Runtime dependencies

Requires runtime-provided bundle helpers, LLM execution, and repository write capabilities from engineering-flow-platform runtime.
