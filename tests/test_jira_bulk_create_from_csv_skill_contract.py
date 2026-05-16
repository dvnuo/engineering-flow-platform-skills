from __future__ import annotations

import re
from pathlib import Path

from scripts.validate_skills import parse_frontmatter


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "jira_bulk_create_from_csv"
SKILL_PATH = SKILL_DIR / "skill.md"


def _load_skill() -> tuple[dict[str, object], str]:
    content = SKILL_PATH.read_text(encoding="utf-8")
    data, errors = parse_frontmatter(content)
    assert errors == []
    return data, content


def test_jira_bulk_create_from_csv_skill_files_exist() -> None:
    assert SKILL_DIR.is_dir()
    assert SKILL_PATH.is_file()


def test_jira_bulk_create_from_csv_frontmatter_contract() -> None:
    data, _ = _load_skill()

    assert data["name"] == "jira-bulk-create-from-csv"
    assert "jira-bulk-create-from-csv" in data["name"]
    assert data["description"] == (
        "从 CSV 批量创建 Jira issue/test case，参考 example Jira ticket 自动发现字段与自定义字段映射；"
        "先映射和 dry-run，确认后创建。"
    )
    assert data["version"] == "1.0.0"
    assert data["owner"] == "qa-platform"
    assert data["planning_mode"] == "required"
    assert data["execution_style"] == "stepwise"
    assert data["ask_user_policy"] == "before_write"
    assert data["output_format"] == "markdown"

    opencode = data.get("opencode")
    assert isinstance(opencode, dict)
    assert opencode["execution_kind"] == "prompt_only"
    assert opencode["compatibility"] == "full"

    permission = opencode.get("permission")
    assert isinstance(permission, dict)
    assert permission["default"] == "ask"

    assert opencode["capability_tags"] == [
        "jira",
        "csv",
        "bulk-create",
        "test-case",
        "opencode-bash-cli",
        "human-confirmation",
    ]


def test_jira_bulk_create_from_csv_declares_no_native_tools() -> None:
    data, _ = _load_skill()

    assert "tools" not in data
    assert "task_tools" not in data

    opencode = data.get("opencode")
    assert isinstance(opencode, dict)
    assert "tool_mappings" not in opencode


def test_jira_bulk_create_from_csv_body_contains_required_contract_clauses() -> None:
    _, content = _load_skill()

    required_fragments = [
        "jira issue map-csv",
        "jira issue bulk-create",
        "--dry-run",
        "--yes",
        "jira field list",
        "jira issue createmeta --from-issue",
        "--expand names,schema,editmeta",
        "customfield_<id>",
        "Never create Jira issues immediately",
        "explicit confirmation",
    ]

    for fragment in required_fragments:
        assert fragment in content

    assert "status/resolution/comments/worklog/watchers/attachments" in content


def test_jira_bulk_create_from_csv_body_has_no_hardcoded_customfield_ids() -> None:
    _, content = _load_skill()

    assert re.search(r"customfield_\d+", content) is None
