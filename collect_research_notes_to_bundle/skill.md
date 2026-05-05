---
name: collect_research_notes_to_bundle
description: Collects research findings from configured sources and writes a research-notes artifact into the target bundle.
version: 1.0.0
owner: engineering-flow-platform
triggers:
  - /collect_research_notes_to_bundle
  - collect research notes into bundle
  - summarize research sources for bundle
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
Use this skill to synthesize research findings and open questions from source systems into the bundle research notes artifact.

## Inputs expected

- `bundle_ref`: target bundle repo/path/branch reference.
- `sources`: source map (typically `jira`, `confluence`, `github_docs`; `figma` currently ignored in MVP).
- `manifest_ref` (optional): explicit manifest location.

## Output

- Updates the configured research notes YAML file in the bundle.
- Returns bundle reference, updated file path, commit SHA, and optional warnings.

## Runtime dependencies

Requires EFP runtime context and tools for manifest resolution, source loading, GitHub write operations, and LLM-based synthesis.
