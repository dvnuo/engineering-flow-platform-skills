---
name: design_test_cases_from_bundle
description: Generates structured test cases from bundle requirements and writes the bundle test-cases artifact.
version: 1.0.0
owner: engineering-flow-platform
triggers:
  - /design_test_cases_from_bundle
  - design test cases from requirement bundle
  - generate test-cases yaml from requirements
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
Use this skill to transform requirement bundle context into actionable test case definitions.

## Inputs expected

- `bundle_ref`: target bundle repo/path/branch reference.
- `manifest_ref` (optional): explicit manifest location.

## Output

- Generates and writes the configured test-cases YAML artifact.
- Returns updated file metadata and commit SHA.

## Runtime dependencies

Depends on EFP runtime bundle readers/writers and LLM execution context for deriving test design output from `requirements.yaml`.
