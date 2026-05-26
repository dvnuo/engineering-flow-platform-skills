from __future__ import annotations

import re
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


def test_delegation_skills_defer_start_feedback_and_final_reply_to_portal() -> None:
    required_fragments = [
        "Portal owns start feedback and final reply delivery",
        "`reply_handled_by_skill: false`",
        '"reply_handled_by_skill": false',
        "final_response",
    ]

    for name in DELEGATION_SKILLS:
        _, content = _load_skill(name)
        for fragment in required_fragments:
            assert fragment in content
        assert "reply_handled_by_skill: true" not in content
        assert '"reply_handled_by_skill": true' not in content


def test_github_delegation_skills_use_gh_cli_and_defer_reactions_to_portal() -> None:
    required_fragments = [
        "gh api",
        "gh pr view",
        "Portal owns start feedback and final reply delivery",
        "reaction_target",
        "input_payload.delegation",
        "final_response",
        "audit_trace",
        "external_actions",
    ]
    forbidden_fragments = [
        "At the very start, add an eyes reaction",
        "add an eyes reaction to the triggering comment",
        "remove the eyes reaction",
        "gh api -X POST /repos/{owner}/{repo}/issues/{pull_number}/reactions",
        "gh api -X POST /repos/{owner}/{repo}/issues/comments/{comment_id}/reactions",
        "gh api -X POST /repos/{owner}/{repo}/pulls/comments/{comment_id}/reactions",
        "gh api -X DELETE /repos/{owner}/{repo}/issues/{pull_number}/reactions",
        "gh api -X DELETE /repos/{owner}/{repo}/issues/comments/{comment_id}/reactions",
        "gh api -X DELETE /repos/{owner}/{repo}/pulls/comments/{comment_id}/reactions",
    ]

    for name in GITHUB_SKILLS:
        _, content = _load_skill(name)
        for fragment in required_fragments:
            assert fragment in content
        for fragment in forbidden_fragments:
            assert fragment not in content
        assert "efp_github_" not in content


def test_github_delegation_skills_document_portal_delivery_targets() -> None:
    _, review_content = _load_skill("delegation-github-pr-review")
    assert "Portal adds/removes the PR start reaction" in review_content
    assert "posts the final PR comment from `final_response`" in review_content

    _, mention_content = _load_skill("delegation-github-pr-mention")
    assert "Portal reacts to the triggering comment" in mention_content
    assert "quote reply to that triggering comment from `final_response`" in mention_content


def test_github_pr_review_prefers_inline_comments_with_suggestions() -> None:
    _, content = _load_skill("delegation-github-pr-review")

    required_fragments = [
        "Inline comments are the preferred/default writeback for line-anchorable findings",
        "Any finding tied to a changed line should normally be posted as an inline PR comment with `gh api`",
        "gh api -X POST /repos/{owner}/{repo}/pulls/{number}/comments",
        "```suggestion",
        "suggestion_provided",
    ]

    for fragment in required_fragments:
        assert fragment in content

    assert "efp_github_" not in content


def test_jira_delegation_skills_defer_status_comments_to_portal() -> None:
    required_fragments = [
        "Portal creates the Jira start/status comment",
        "updates that same comment with `final_response`",
        "reply_handled_by_skill: false",
        "input_payload.delegation",
        "final_response",
        "jira issue get",
        "audit_trace",
        "external_actions",
    ]
    forbidden_fragments = [
        "jira issue comment add",
        "jira issue comment update",
    ]

    for name in JIRA_SKILLS:
        _, content = _load_skill(name)
        for fragment in required_fragments:
            assert fragment in content
        for fragment in forbidden_fragments:
            assert fragment not in content


def test_jira_delegation_skills_assume_preconfigured_private_runtime() -> None:
    required_fragments = [
        "private Jira service",
        "configured EFP `jira` CLI/tool",
        "already configured in the runtime",
        "jira commands --json",
        "jira schema ... --json",
        "environment blocker",
    ]
    forbidden_patterns = [
        r"\baccountId\b",
        r"\bJira Cloud\b",
        r"\blogin\b",
        r"\bcredentials?\b",
        r"\btokens?\b",
        r"\bauth setup\b",
        r"\bauthentication\b",
        r"\bauthorization\b",
    ]

    for name in JIRA_SKILLS:
        _, content = _load_skill(name)
        for fragment in required_fragments:
            assert fragment in content
        for pattern in forbidden_patterns:
            assert not re.search(pattern, content, flags=re.IGNORECASE)


def test_jira_assignee_reassigns_back_to_reporter() -> None:
    _, content = _load_skill("delegation-jira-assignee")

    assert "assign the issue back to the reporter" in content
    assert "jira issue assign" in content
    assert "jira_reassigned_to_reporter" in content
