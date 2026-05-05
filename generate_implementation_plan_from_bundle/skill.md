---
name: generate_implementation_plan_from_bundle
description: Builds an implementation plan artifact from bundle metadata and available requirements context.
version: 1.0.0
owner: engineering-flow-platform
triggers:
  - /generate_implementation_plan_from_bundle
  - generate implementation plan from bundle
  - create bundle implementation plan yaml
tools: []
output_format: markdown
opencode:
  execution_kind: programmatic
  compatibility: unsupported
  permission:
    default: deny
  capability_tags:
    - native-only
    - programmatic
---
Use this skill to create a structured implementation plan for execution teams from bundle context.

## Inputs expected

- `bundle_ref`: target bundle repo/path/branch reference.
- `manifest_ref` (optional): explicit manifest location.

## Output

- Writes the configured implementation plan YAML artifact in the bundle.
- Returns updated file information and commit SHA.

## Runtime dependencies

Relies on EFP runtime manifest/artifact resolution, optional requirements document loading, LLM synthesis, and GitHub-backed write APIs.
