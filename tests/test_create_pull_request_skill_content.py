from __future__ import annotations

from pathlib import Path

from scripts.validate_skills import parse_frontmatter


def test_create_pull_request_frontmatter_and_required_content() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    skill_path = repo_root / "create-pull-request" / "skill.md"
    content = skill_path.read_text(encoding="utf-8")

    data, errors = parse_frontmatter(content)
    assert errors == []

    assert data["tools"] == [
        "run_command",
        "github_get_default_branch",
        "github_create_pull_request",
    ]
    assert data["opencode"]["tool_mappings"] == {
        "run_command": "efp_run_command",
        "github_get_default_branch": "efp_github_get_default_branch",
        "github_create_pull_request": "efp_github_create_pull_request",
    }

    required_phrases = [
        'Repository has been prepared at',
        'Do not run git inspection from `/workspace` unless `/workspace/.git` exists',
        'to <base>',
        'dry_run: false',
        'idempotency_key',
        'Do not use raw curl',
    ]
    for phrase in required_phrases:
        assert phrase in content
