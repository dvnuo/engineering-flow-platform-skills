from __future__ import annotations

from pathlib import Path

from scripts.validate_skills import (
    normalize_opencode_name,
    parse_frontmatter,
    validate_root,
)


def test_normalize_opencode_name_examples() -> None:
    assert (
        normalize_opencode_name("collect_requirements_to_bundle", "x")
        == "collect-requirements-to-bundle"
    )
    assert normalize_opencode_name("review-pull-request", "x") == "review-pull-request"
    assert normalize_opencode_name(" My Skill__Name!! ", "x") == "my-skill-name"


def test_parse_frontmatter_tools_empty_list() -> None:
    content = """---
name: sample
description: sample
version: 1.0.0
owner: test
triggers:
  - sample
tools: []
task_tools: []
---
"""
    data, errors = parse_frontmatter(content)
    assert errors == []
    assert data["tools"] == []
    assert data["task_tools"] == []


def test_parse_frontmatter_tools_list() -> None:
    content = """---
name: sample
description: sample
version: 1.0.0
owner: test
triggers:
  - sample
tools:
  - jira_get_issue
  - jira_search
---
"""
    data, errors = parse_frontmatter(content)
    assert errors == []
    assert isinstance(data["tools"], list)
    assert data["tools"] == ["jira_get_issue", "jira_search"]


def test_parse_frontmatter_quoted_description_with_colon() -> None:
    content = """---
name: sample
description: "带中文或冒号: 的内容"
version: 1.0.0
owner: test
triggers:
  - sample
---
"""
    data, errors = parse_frontmatter(content)
    assert errors == []
    assert data["description"] == "带中文或冒号: 的内容"


def test_parse_frontmatter_nested_metadata_does_not_fail() -> None:
    content = """---
name: sample
description: sample
version: 1.0.0
owner: test
triggers:
  - sample
metadata:
  emoji: 🛠️
  requires:
    bins: [python3]
---
"""
    _, errors = parse_frontmatter(content)
    assert errors == []


def _write_skill(root: Path, dirname: str, body: str) -> None:
    skill_dir = root / dirname
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "skill.md").write_text(body, encoding="utf-8")


def test_validate_root_detects_normalized_conflict(tmp_path: Path) -> None:
    _write_skill(
        tmp_path,
        "foo_bar",
        """---
name: foo_bar
description: a
version: 1.0.0
owner: test
triggers:
  - x
---
""",
    )
    _write_skill(
        tmp_path,
        "foo-bar",
        """---
name: foo-bar
description: b
version: 1.0.0
owner: test
triggers:
  - y
---
""",
    )

    exit_code, errors, _ = validate_root(tmp_path, opencode_compatible=True)

    assert exit_code == 1
    assert any("duplicate OpenCode normalized skill name" in err for err in errors)


def test_validate_root_rejects_scalar_tools(tmp_path: Path) -> None:
    _write_skill(
        tmp_path,
        "bad",
        """---
name: bad
description: bad
version: 1.0.0
owner: test
triggers:
  - x
tools: jira_get_issue
---
""",
    )

    exit_code, errors, _ = validate_root(tmp_path, opencode_compatible=True)

    assert exit_code == 1
    assert any("'tools' must be a list or omitted" in err for err in errors)


def test_validate_root_allows_missing_task_tools(tmp_path: Path) -> None:
    _write_skill(
        tmp_path,
        "ok",
        """---
name: ok
description: ok
version: 1.0.0
owner: test
triggers:
  - x
tools: []
---
""",
    )

    exit_code, errors, _ = validate_root(tmp_path, opencode_compatible=True)

    assert exit_code == 0
    assert errors == []
