from __future__ import annotations

from pathlib import Path

from scripts.validate_skills import parse_frontmatter


REPO_ROOT = Path(__file__).resolve().parents[1]
DELEGATION_SKILLS = [
    "delegation-github-pr-review",
    "delegation-github-pr-mention",
    "delegation-jira-assignee",
    "delegation-jira-mention",
]
GITHUB_SKILLS = [
    "delegation-github-pr-review",
    "delegation-github-pr-mention",
]
JIRA_SKILLS = [
    "delegation-jira-assignee",
    "delegation-jira-mention",
]


def _load_skill(name: str) -> tuple[dict[str, object], str]:
    path = REPO_ROOT / name / "skill.md"
    content = path.read_text(encoding="utf-8")
    data, errors = parse_frontmatter(content)
    assert errors == []
    return data, content


def test_delegation_skill_files_exist() -> None:
    for name in DELEGATION_SKILLS:
        assert (REPO_ROOT / name).is_dir()
        assert (REPO_ROOT / name / "skill.md").is_file()


def test_delegation_frontmatter_names_match_directories() -> None:
    for name in DELEGATION_SKILLS:
        data, _ = _load_skill(name)
        assert data["name"] == name


def test_delegation_skills_are_prompt_only_opencode_compatible() -> None:
    for name in DELEGATION_SKILLS:
        data, _ = _load_skill(name)

        assert "tools" not in data
        assert "task_tools" not in data

        opencode = data.get("opencode")
        assert isinstance(opencode, dict)
        assert opencode["execution_kind"] == "prompt_only"
        assert opencode["compatibility"] == "full"
        assert "tool_mappings" not in opencode


def test_github_delegation_skills_use_gh_cli_and_reactions() -> None:
    required_fragments = [
        "gh api",
        "gh pr view",
        "eyes reaction",
        "reaction_target",
        "input_payload.delegation",
        "final_response",
        "audit_trace",
        "external_actions",
    ]

    for name in GITHUB_SKILLS:
        _, content = _load_skill(name)
        for fragment in required_fragments:
            assert fragment in content
        assert "efp_github_" not in content


def test_jira_delegation_skills_manage_comment_writeback() -> None:
    required_fragments = [
        "jira issue comment add",
        "jira issue comment update",
        "reply_handled_by_skill: true",
        "input_payload.delegation",
        "final_response",
        "audit_trace",
        "external_actions",
    ]

    for name in JIRA_SKILLS:
        _, content = _load_skill(name)
        for fragment in required_fragments:
            assert fragment in content


def test_jira_assignee_reassigns_back_to_reporter() -> None:
    _, content = _load_skill("delegation-jira-assignee")

    assert "assign the issue back to the reporter" in content
    assert "jira issue assign" in content
    assert "jira_reassigned_to_reporter" in content
