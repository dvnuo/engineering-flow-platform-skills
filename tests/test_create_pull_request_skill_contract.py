from __future__ import annotations

from pathlib import Path

from scripts.validate_skills import parse_frontmatter


def _load_skill() -> tuple[dict[str, object], str]:
    path = Path(__file__).resolve().parents[1] / "create-pull-request" / "skill.md"
    content = path.read_text(encoding="utf-8")
    data, errors = parse_frontmatter(content)
    assert errors == []
    return data, content


def test_create_pull_request_frontmatter_tools_and_mappings() -> None:
    data, _ = _load_skill()

    tools = data.get("tools")
    task_tools = data.get("task_tools")
    assert isinstance(tools, list)
    assert isinstance(task_tools, list)

    assert "git_clone" in tools
    assert "run_command" in tools
    assert "github_get_default_branch" in tools
    assert "github_create_pull_request" in tools

    assert "git_clone" in task_tools
    assert "run_command" in task_tools

    opencode = data.get("opencode")
    assert isinstance(opencode, dict)
    permission = opencode.get("permission")
    assert isinstance(permission, dict)
    assert permission.get("default") == "ask"

    tool_mappings = opencode.get("tool_mappings")
    assert isinstance(tool_mappings, dict)
    assert tool_mappings.get("git_clone") == "efp_git_clone"
    assert tool_mappings.get("run_command") == "efp_run_command"
    assert tool_mappings.get("github_get_default_branch") == "efp_github_get_default_branch"
    assert tool_mappings.get("github_create_pull_request") == "efp_github_create_pull_request"

    combined = set(tools) | set(task_tools)
    assert combined.issubset(set(tool_mappings.keys()))


def test_create_pull_request_body_contains_required_contract_clauses() -> None:
    _, content = _load_skill()

    assert "Phase 0" in content
    assert "git repo <url>" in content
    assert "git_clone" in content
    assert "dry_run=false" in content
    assert "prepared_repo_path" in content
    assert "Do not ask for local checkout path when repo_url is provided" in content
    assert "Do not use raw curl" in content
    assert "Do not use gh CLI" in content


def test_create_pull_request_body_preserves_user_base_branch_rule() -> None:
    _, content = _load_skill()

    assert "do not override user-provided base" in content
    assert "to develop" in content
