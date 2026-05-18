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
        "Bulk create Jira issues/test cases from CSV, using an example Jira ticket to "
        "auto-discover field and custom-field mappings; perform mapping and dry-run "
        "first, then create after confirmation."
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
        "--confirm-mapping",
        "--apply-post-create-updates",
        "requires_confirmation",
        "ambiguous_columns",
        "planned_post_create_updates",
        "--metadata-mode auto",
        "editmeta-degraded",
        "editmeta_degraded",
        "createmeta unavailable",
        "System fields and post-create updates",
        "Reporter is a Jira system user field",
    ]

    for fragment in required_fragments:
        assert fragment in content

    assert "status/resolution/comments/worklog/watchers/attachments" in content


def test_jira_bulk_create_from_csv_confirm_mapping_is_conditional() -> None:
    _, content = _load_skill()

    assert (
        "Actual creation may include `--confirm-mapping` only after the user has confirmed"
        in content
    )
    assert (
        "Do not add `--confirm-mapping` automatically just because the user asked to create"
        in content
    )
    assert "always include `--confirm-mapping`" not in content.lower()


def test_jira_bulk_create_from_csv_post_create_updates_require_confirmation() -> None:
    _, content = _load_skill()

    assert (
        "Do not apply post-create updates unless the user explicitly confirms creation"
        in content
    )
    assert (
        "include `--apply-post-create-updates` automatically when planned post-create updates are present and accepted"
        in content
    )
    assert (
        "This final confirmation can cover both creation and post-create updates"
        in content
    )


def test_jira_bulk_create_from_csv_reporter_post_create_guidance() -> None:
    _, content = _load_skill()

    required_fragments = [
        "Reporter is a Jira system user field",
        "If the CSV includes Reporter and dry-run reports it as `planned_post_create_update`",
        "Reporter will be set after issue creation",
        "Do not ask the user to troubleshoot Reporter manually or use raw Jira API calls unless the CLI create/update flow fails",
    ]

    for fragment in required_fragments:
        assert fragment in content

    assert (
        "Raw `jira api put` is only a last-resort troubleshooting step if the CLI bulk-create/update flow fails"
        in content
    )


def test_jira_bulk_create_from_csv_createmeta_unavailable_fallback() -> None:
    _, content = _load_skill()

    required_fragments = [
        "If `jira issue createmeta --from-issue <EXAMPLE> --json` fails with 404",
        "do not stop the workflow",
        "Do not stop the workflow if issue get succeeded",
        "continue to mapping with CLI metadata fallback",
        "jira issue map-csv --metadata-mode auto",
        "Jira createmeta is unavailable in this instance",
        "create payload contains only project, issuetype, and summary",
        "actual creation requires `--apply-post-create-updates` after user confirmation",
    ]

    for fragment in required_fragments:
        assert fragment in content


def test_jira_bulk_create_from_csv_normal_path_uses_cli_metadata_auto() -> None:
    _, content = _load_skill()

    required_fragments = [
        "jira issue map-csv",
        "jira issue bulk-create",
        "--metadata-mode auto",
        "--dry-run",
        "--yes",
        "explicit confirmation",
        "planned_post_create_updates",
        "--apply-post-create-updates",
    ]

    for fragment in required_fragments:
        assert fragment in content

    assert "The normal path is `jira issue map-csv --metadata-mode auto`" in content


def test_jira_bulk_create_from_csv_editmeta_degraded_declined_updates_stop_create() -> None:
    _, content = _load_skill()

    required_fragments = [
        "If metadata_mode is editmeta_degraded",
        "do not create",
        "post_create_updates_required",
        "--apply-post-create-updates",
        "Do not run the base `jira issue bulk-create ... --yes` command",
        "If the user rejects updates, stop and summarize what would not be applied",
    ]

    for fragment in required_fragments:
        assert fragment in content

    assert (
        "If the user declines post-create updates, create only the create-meta fields"
        not in content
    )


def test_jira_bulk_create_from_csv_body_has_no_hardcoded_customfield_ids() -> None:
    _, content = _load_skill()

    assert re.search(r"customfield_\d+", content) is None


def test_jira_bulk_create_from_csv_body_has_no_hardcoded_example_issue_key() -> None:
    _, content = _load_skill()

    assert re.search(r"\b[A-Z][A-Z0-9]+-\d+\b", content) is None
