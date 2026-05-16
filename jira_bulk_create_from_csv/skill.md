---
name: jira-bulk-create-from-csv
description: 从 CSV 批量创建 Jira issue/test case，参考 example Jira ticket 自动发现字段与自定义字段映射；先映射和 dry-run，确认后创建。
version: 1.0.0
owner: qa-platform
triggers:
  - 上传 CSV 批量创建 Jira 测试用例
  - 参考某个 Jira ticket 创建
  - 按 example ticket 的字段结构创建 Jira issue
  - testcases.csv 批量导入 Jira
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
15. Do not apply post-create updates unless the user explicitly confirms them after seeing the dry-run output.

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

Review `dry-run.json` before presenting the result. If it reports `planned_post_create_updates` or `post_create_updates_planned_not_applied`, explain that these are fields that cannot be set during initial create and may require post-create update calls after the issue keys exist.

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

If the dry-run reports `planned_post_create_updates` or `post_create_updates_planned_not_applied`, ask whether to apply post-create updates. Only if the user confirms, include `--apply-post-create-updates` in the actual creation command. If the user does not confirm post-create updates, create only the create-meta fields and clearly report which template fields were not applied.

The confirmation prompt must require explicit user confirmation for creation. Mapping confirmation and post-create update application are separate explicit confirmations when those conditions exist. Do not treat silence, implied consent, or a request to "continue" before seeing the dry-run and mapping table as approval for creation.

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

If, and only if, the user has also explicitly confirmed post-create updates after reviewing the dry-run, add `--apply-post-create-updates` to the actual creation command:

```bash
jira issue bulk-create \
  --from-csv <CSV_PATH> \
  --mapping mapping-plan.json \
  --yes \
  --apply-post-create-updates \
  --output created-results.json \
  --json
```

When both conditions apply and the user explicitly confirms both, include both conditional flags in the actual creation command:

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

> 我上传了 testcases.csv，请参考 QA-1234 批量创建 Jira 测试用例，先 dry-run。

Example assistant behavior:

> 我会先读取 CSV、QA-1234、Jira 字段目录和 createmeta，生成字段映射与 dry-run；确认前不会创建。
