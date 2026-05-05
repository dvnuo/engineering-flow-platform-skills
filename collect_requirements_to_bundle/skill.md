---
name: collect_requirements_to_bundle
description: Collects requirement signals from configured sources and writes requirements.yaml into the target requirement bundle.
version: 1.0.0
owner: engineering-flow-platform
triggers:
  - /collect_requirements_to_bundle
  - collect requirements into bundle
  - build requirements yaml from jira and docs
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
Use this skill to aggregate requirement context from Jira, Confluence, and GitHub document sources into a normalized requirements artifact.

## Inputs expected

- `bundle_ref`: target bundle repo/path/branch reference.
- `sources`: source map (for example `jira`, `confluence`, `github_docs`; `figma` is accepted but ignored in MVP).
- `manifest_ref` (optional): explicit manifest location.

## Output

- Updates the bundle requirements file (typically `requirements.yaml`) through runtime asset writers.
- Returns metadata such as updated files, commit SHA, and warnings.

## Runtime dependencies

This skill relies on EFP runtime-provided integrations and context (GitHub channel, bundle manifest helpers, source loaders, and LLM execution utilities).
