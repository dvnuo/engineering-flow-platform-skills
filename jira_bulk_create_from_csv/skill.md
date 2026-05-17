---
name: jira-bulk-create-from-csv
description: Bulk create Jira issues/test cases from CSV, using an example Jira ticket to auto-discover field and custom-field mappings; perform mapping and dry-run first, then create after confirmation.
version: 1.0.0
owner: qa-platform
triggers:
  - Upload CSV to bulk create Jira test cases
  - Create by referencing a Jira ticket
  - Create Jira issues using the field structure from an example ticket
  - Bulk import testcases.csv into Jira
  - CSV to Jira issues
  - bulk create Jira test cases from CSV
planning_mode: required
execution_style: stepwise
ask_user_policy: before_write
output_format: markdown
opencode:
  execution_kind: prompt_only
  compatibility: full
  permission:
    default: ask
  capability_tags:
    - jira
    - csv
    - bulk-create
    - test-case
    - opencode-bash-cli
    - human-confirmation
---

# Jira Bulk Create From CSV

Use this skill when the user wants to bulk create Jira issues or test cases from an uploaded CSV, especially when they provide an example Jira issue whose field structure should guide discovery and mapping.

This skill fixes the safe workflow and command order only. It must not hardcode Jira custom fields, project, issue type, templates, issue keys, or CSV column mappings. Field discovery, mapping, dry-run, and creation are performed by the generic `jira` CLI through OpenCode Bash. The LLM may explain results, summarize ambiguity, and ask the user to choose among ambiguous mappings.

## Non-Negotiable Rules

1. Never create Jira issues immediately.
2. Never infer customfield IDs from memory.
3. Never use Jira custom field display names in create payload. Custom fields must be written by `customfield_<id>`.
4. Always inspect:
   - uploaded CSV columns and sample rows
   - example Jira issue
   - global Jira field catalog
   - project + issue type create metadata
   - edit metadata when needed
5. Always run mapping and dry-run first.
6. Always show mapping table and dry-run preview.
7. Ask for explicit user confirmation before actual creation.
8. Only after explicit confirmation, run `jira issue bulk-create ... --yes`.
9. If any mapping confidence is low/ambiguous, ask the user to choose rather than creating.
10. If required fields are missing, stop and ask for missing values/defaults.
11. If a field is present in example issue but absent from create metadata, do not put it in create payload. It may only be proposed as a post-create update if editmeta allows it.
12. Do not copy system fields/status/resolution/comments/worklog/watchers/attachments from the template unless user explicitly asks.
13. If `mapping-plan.json` contains `requires_confirmation` or `ambiguous_columns`, do not run actual creation until the user explicitly confirms the mapping choices.
14. Do not add `--confirm-mapping` automatically just because the user asked to create. The user must have reviewed the mapping table.
15. Do not apply post-create updates unless the user explicitly confirms creation and accepts the planned post-create updates after seeing the dry-run output.

## System fields and post-create updates

Reporter is a Jira system user field. It is commonly not accepted in the initial create payload, even when the CSV contains a Reporter column and the user expects the value to be set.

If the CSV includes Reporter and dry-run reports it as `planned_post_create_update`, explain that Reporter will be set after issue creation by the `jira issue bulk-create` workflow. Do not ask the user to troubleshoot Reporter manually or use raw Jira API calls unless the CLI create/update flow fails.

The final explicit user confirmation can cover both issue creation and planned post-create updates when the mapping table and dry-run summary clearly show those updates, including the Reporter update phase. After that confirmation, include `--apply-post-create-updates` automatically when `planned_post_create_updates` are present and accepted.

## Required Command Sequence

Follow these steps in order. Do not skip ahead to creation, and do not create anything before the user explicitly confirms the dry-run.

### A. Locate CSV

- Inspect attached files and runtime context.
- Prefer the `workspace_path` returned by runtime upload.
- If no usable local path is known, search `/workspace/uploads`.
- If the CSV path is still ambiguous, ask the user.
- If multiple CSVs exist, ask which file to use.

### B. Inspect CSV

Use shell or Python only to summarize columns and sample rows if needed, or rely on `jira issue map-csv` later. Must not create anything at this step.

### C. Test Jira Auth

```bash
jira auth test --json
```

### D. Inspect CLI Capabilities

```bash
jira commands --json
jira schema issue.map-csv --json
jira schema issue.bulk-create --json
```

### E. Inspect Example Ticket

```bash
jira issue get <EXAMPLE> --fields '*all' --expand names,schema,editmeta --json
```

### F. Inspect Field Catalog

```bash
jira field list --json
```

### G. Inspect Create Metadata

```bash
jira issue createmeta --from-issue <EXAMPLE> --json
```

### H. Generate Mapping

```bash
jira issue map-csv \
  --from-csv <CSV_PATH> \
  --template-issue <EXAMPLE> \
  --output mapping-plan.json \
  --json
```

### I. Dry-Run

```bash
jira issue bulk-create \
  --from-csv <CSV_PATH> \
  --mapping mapping-plan.json \
  --dry-run \
  --output dry-run.json \
  --json
```

Review `dry-run.json` before presenting the result. If it reports `planned_post_create_updates` or `post_create_updates_planned_not_applied`, explain that these are fields that cannot be set during initial create and can be applied by the CLI after the issue keys exist. If Reporter appears there, explain that Reporter is a system user field and will be set after issue creation when the planned post-create updates are accepted.

### J. Present To User

Present a concise markdown summary containing:

- CSV row count
- target Jira instance if known
- target project and issue type inferred from example
- mapping table with:
  - CSV column
  - Jira field id
  - Jira field display name
  - type
  - confidence
  - reason
  - phase
- unmapped columns
- ambiguous columns
- required fields missing
- blocked fields from template
- dry-run preview first 3 rows
- exact command that will run after confirmation

If `mapping-plan.json` contains `requires_confirmation` or `ambiguous_columns`, include the ambiguous or low-confidence choices in the summary and ask the user to explicitly confirm the selected mapping choices. Actual creation may include `--confirm-mapping` only after the user has confirmed both the dry-run and the field mapping.

If the dry-run reports `planned_post_create_updates` or `post_create_updates_planned_not_applied`, clearly include those updates in the table or summary and ask for final explicit confirmation to create the issues with the planned post-create updates. This final confirmation can cover both creation and post-create updates if the user has seen the updates and accepts them. After confirmation, include `--apply-post-create-updates` automatically when planned post-create updates are present and accepted. If the user declines post-create updates, create only the create-meta fields and clearly report which fields were not applied.

The confirmation prompt must require explicit user confirmation for creation. It may also include the planned post-create updates in the same final confirmation when the table clearly shows those updates. Mapping confirmation still requires explicit acceptance when `requires_confirmation` or `ambiguous_columns` are present. Do not treat silence, implied consent, or a request to "continue" before seeing the dry-run and mapping table as approval for creation.

### K. Create Only After Confirmation

Only after explicit confirmation, run the base creation command when `mapping-plan.json` has no `requires_confirmation` or `ambiguous_columns`:

```bash
jira issue bulk-create \
  --from-csv <CSV_PATH> \
  --mapping mapping-plan.json \
  --yes \
  --output created-results.json \
  --json
```

If the user has explicitly confirmed ambiguous or low-confidence mappings after reviewing the mapping table, run creation with `--confirm-mapping`:

```bash
jira issue bulk-create \
  --from-csv <CSV_PATH> \
  --mapping mapping-plan.json \
  --yes \
  --confirm-mapping \
  --output created-results.json \
  --json
```

If the final explicit confirmation accepts planned post-create updates after the user reviews the dry-run and update table, add `--apply-post-create-updates` to the actual creation command:

```bash
jira issue bulk-create \
  --from-csv <CSV_PATH> \
  --mapping mapping-plan.json \
  --yes \
  --apply-post-create-updates \
  --output created-results.json \
  --json
```

When mapping confirmation and planned post-create updates both apply, include both conditional flags after the user explicitly accepts both conditions. A single final confirmation may cover them if the mapping choices and planned updates are clearly shown:

```bash
jira issue bulk-create \
  --from-csv <CSV_PATH> \
  --mapping mapping-plan.json \
  --yes \
  --confirm-mapping \
  --apply-post-create-updates \
  --output created-results.json \
  --json
```

### L. Final Response

After the create command finishes, report:

- created count
- failed count
- created issue keys
- failed rows and reasons
- whether post-create updates were applied
- any post-create update failures
- path to `mapping-plan.json`
- path to `dry-run.json`
- path to `created-results.json`

## Field Mapping Rules

- Do not include any concrete custom field id in instructions, examples, or payloads except the generic literal pattern `customfield_<id>`.
- Do not say a specific CSV column maps to a fixed Jira field. Mapping must be discovered every run.
- Create payloads must use field ids accepted by Jira create metadata.
- Custom fields must use the `customfield_<id>` id form, never only a display name.
- Required fields must come from createmeta and the generated mapping plan, not assumptions.
- If create metadata excludes a field found on the template issue, keep it out of the create payload.
- If edit metadata allows a blocked template field after creation, propose it as a separate post-create update and ask for confirmation before any update.
- Do not copy system fields, status, resolution, comments, worklog, watchers, or attachments from the template unless the user explicitly asks.

## Example

Example user request:

> I uploaded testcases.csv. Please reference QA-1234 to bulk create Jira test cases, and run a dry-run first.

Example assistant behavior:

> I will first read the CSV, QA-1234, Jira field catalog, and createmeta to generate field mappings and a dry-run; nothing will be created before your confirmation.
