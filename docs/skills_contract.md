# Skills contract

## 目的

Skills contract 是给 Portal、native runtime、opencode-runtime 和 integration tests 消费的 machine-readable metadata。它不是 runtime adapter：不会执行 skill，不会执行 `skill.py`，也不会生成 `.opencode`。通过 contract，其他仓库不需要复制 `validate_skills.py` 的 frontmatter 解析逻辑。

## Source root

- production root 是 repo root（runtime mount 到 `/app/skills`）。
- integration fixture root 是 `integration/fixtures`。
- 不允许 nested `skills/` 目录。

## Contract schema

顶层字段：
- `schema_version`
- `scope`
- `stats`
- `skills`

固定值：
- `schema_version`: fixed string `efp.skills.contract.v1`
- `scope`: `production` or `integration-fixtures`

每个 skill record 字段：
- `path`
- `directory`
- `name`
- `normalized_opencode_name`
- `description`
- `version`
- `owner`
- `triggers`
- `tools`
- `task_tools`
- `references`
- `python_backed`
- `opencode.execution_kind`
- `opencode.compatibility`
- `opencode.permission_default`
- `opencode.capability_tags`
- `opencode.tool_mappings`

## Commands

Production:

```bash
python scripts/export_skills_contract.py --scope production --pretty
```

Integration fixtures:

```bash
python scripts/export_skills_contract.py --root integration/fixtures --scope integration-fixtures --pretty
```

## Consumer guidance

- Portal 可以使用 contract 做 capability display、skill compatibility display、profile selection。
- native runtime 仍以 `skill.md` 作为 source of truth，不应从 contract 执行 skill。
- opencode-runtime 仍负责把 `/app/skills` 转换为 `.opencode/skills/.../SKILL.md`；contract 仅用于 metadata/smoke/compatibility checks。
- `python_backed=true` 且 `opencode.compatibility=unsupported` 的 skill，不应在 OpenCode 侧作为 full skill 展示。

## Non-goals

- 不检查 Tools repo wrapper 是否真实存在。
- 不执行 `skill.py`。
- 不读取 references 正文。
- 不生成 OpenCode assets。
- 不连接 Kubernetes 或 runtime service。


## Minimal JSON example

```json
{
  "schema_version": "efp.skills.contract.v1",
  "scope": "production",
  "stats": {
    "total_skill_directories": 21,
    "total_skill_md_discovered": 21
  },
  "skills": [
    {
      "path": "review-pull-request/skill.md",
      "directory": "review-pull-request",
      "name": "review-pull-request",
      "normalized_opencode_name": "review-pull-request",
      "description": "...",
      "version": "1.0.0",
      "owner": "engineering-flow-platform",
      "triggers": [],
      "tools": [],
      "task_tools": [],
      "references": [],
      "python_backed": false,
      "opencode": {
        "execution_kind": "prompt_only",
        "compatibility": "full",
        "permission_default": "ask",
        "capability_tags": [],
        "tool_mappings": {}
      }
    }
  ]
}
```

## CLI exit codes

- `0`: contract exported successfully
- `1`: validation failed; no output file is written
- `2`: invalid root or invalid CLI arguments

## Programmatic API

`build_contract(root, scope)` validates before exporting. It raises:
- `FileNotFoundError` when root does not exist or is not a directory
- `ContractValidationError` when validator fails
- `ValueError` when scope is invalid
