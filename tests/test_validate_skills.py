from __future__ import annotations

from pathlib import Path

from scripts.validate_skills import (
    main,
    normalize_opencode_name,
    parse_frontmatter,
    validate_root,
)

VALID_OPENCODE_BLOCK = """
opencode:
  execution_kind: prompt_only
  compatibility: full
  permission:
    default: ask
  capability_tags:
    - test
"""

VALID_OPENCODE_WITH_TOOL_MAPPING = """
opencode:
  execution_kind: prompt_only
  compatibility: degraded
  permission:
    default: ask
  capability_tags:
    - test
    - tools-required
  tool_mappings:
    jira_get_issue: efp_jira_get_issue
    jira_search: efp_jira_search
"""


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
""" + VALID_OPENCODE_BLOCK + """
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
""" + VALID_OPENCODE_BLOCK + """
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
""" + VALID_OPENCODE_BLOCK + """
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
""" + VALID_OPENCODE_BLOCK + """
---
""",
    )

    exit_code, errors, _ = validate_root(tmp_path, opencode_compatible=True)

    assert exit_code == 0
    assert errors == []


def test_validate_root_requires_tool_mappings_when_tools_present(tmp_path: Path) -> None:
    _write_skill(
        tmp_path,
        "needs-mapping",
        """---
name: needs-mapping
description: sample
version: 1.0.0
owner: test
triggers:
  - x
tools:
  - jira_get_issue
""" + VALID_OPENCODE_BLOCK + """
---
""",
    )
    exit_code, errors, _ = validate_root(tmp_path, opencode_compatible=True)
    assert exit_code == 1
    assert any("opencode.tool_mappings must map every tools/task_tools item" in err for err in errors)


def test_validate_root_rejects_missing_tool_mapping_key(tmp_path: Path) -> None:
    _write_skill(tmp_path, "missing-key", """---
name: missing-key
description: sample
version: 1.0.0
owner: test
triggers:
  - x
tools:
  - jira_get_issue
  - jira_search
opencode:
  execution_kind: prompt_only
  compatibility: degraded
  permission:
    default: ask
  capability_tags:
    - test
  tool_mappings:
    jira_get_issue: efp_jira_get_issue
---
""")
    exit_code, errors, _ = validate_root(tmp_path, opencode_compatible=True)
    assert exit_code == 1
    assert any("opencode.tool_mappings missing mapping for tool 'jira_search'" in err for err in errors)


def test_validate_root_rejects_extra_tool_mapping_key(tmp_path: Path) -> None:
    _write_skill(tmp_path, "extra-key", """---
name: extra-key
description: sample
version: 1.0.0
owner: test
triggers:
  - x
tools:
  - jira_get_issue
opencode:
  execution_kind: prompt_only
  compatibility: degraded
  permission:
    default: ask
  capability_tags:
    - test
  tool_mappings:
    jira_get_issue: efp_jira_get_issue
    jira_search: efp_jira_search
---
""")
    exit_code, errors, _ = validate_root(tmp_path, opencode_compatible=True)
    assert exit_code == 1
    assert any("opencode.tool_mappings contains extra mapping for unknown tool 'jira_search'" in err for err in errors)


def test_validate_root_rejects_noncanonical_opencode_tool_mapping(tmp_path: Path) -> None:
    _write_skill(tmp_path, "bad-map", """---
name: bad-map
description: sample
version: 1.0.0
owner: test
triggers:
  - x
tools:
  - jira_get_issue
opencode:
  execution_kind: prompt_only
  compatibility: degraded
  permission:
    default: ask
  capability_tags:
    - test
  tool_mappings:
    jira_get_issue: jira_get_issue
---
""")
    exit_code, errors, _ = validate_root(tmp_path, opencode_compatible=True)
    assert exit_code == 1
    assert any("opencode.tool_mappings.jira_get_issue='jira_get_issue' must match" in err for err in errors)


def test_validate_root_rejects_wrong_exact_opencode_tool_mapping(tmp_path: Path) -> None:
    _write_skill(tmp_path, "wrong-map", """---
name: wrong-map
description: sample
version: 1.0.0
owner: test
triggers:
  - x
tools:
  - jira_get_issue
opencode:
  execution_kind: prompt_only
  compatibility: degraded
  permission:
    default: ask
  capability_tags:
    - test
  tool_mappings:
    jira_get_issue: efp_wrong_name
---
""")
    exit_code, errors, _ = validate_root(tmp_path, opencode_compatible=True)
    assert exit_code == 1
    assert any("opencode.tool_mappings.jira_get_issue must be 'efp_jira_get_issue'" in err for err in errors)


def test_validate_root_counts_tool_mappings(tmp_path: Path) -> None:
    _write_skill(
        tmp_path,
        "mapping-count",
        """---
name: mapping-count
description: sample
version: 1.0.0
owner: test
triggers:
  - x
tools:
  - jira_get_issue
task_tools:
  - jira_get_issue
  - jira_search
""" + VALID_OPENCODE_WITH_TOOL_MAPPING + """
---
""",
    )
    exit_code, errors, stats = validate_root(tmp_path, opencode_compatible=True)
    assert exit_code == 0
    assert errors == []
    assert stats["opencode_tool_required_skill_count"] == 1
    assert stats["opencode_tool_mapped_skill_count"] == 1
    assert stats["opencode_tool_mapping_count"] == 2


def test_validate_root_rejects_tool_mapping_key_with_whitespace(tmp_path: Path) -> None:
    _write_skill(tmp_path, "bad-key-space", """---
name: bad-key-space
description: sample
version: 1.0.0
owner: test
triggers:
  - x
tools:
  - jira_get_issue
opencode:
  execution_kind: prompt_only
  compatibility: degraded
  permission:
    default: ask
  capability_tags:
    - test
  tool_mappings:
    " jira_get_issue ": efp_jira_get_issue
---
""")
    exit_code, errors, stats = validate_root(tmp_path, opencode_compatible=True)
    assert exit_code == 1
    assert any("must not include leading or trailing whitespace" in err for err in errors)
    assert stats["opencode_tool_mapped_skill_count"] == 0


def test_validate_root_rejects_non_string_tool_items(tmp_path: Path) -> None:
    _write_skill(tmp_path, "bad-tool-item", """---
name: bad-tool-item
description: sample
version: 1.0.0
owner: test
triggers:
  - x
tools:
  - 123
opencode:
  execution_kind: prompt_only
  compatibility: degraded
  permission:
    default: ask
  capability_tags:
    - test
  tool_mappings:
    "123": efp_123
---
""")
    exit_code, errors, _ = validate_root(tmp_path, opencode_compatible=True)
    assert exit_code == 1
    assert any("'tools' items must be non-empty strings" in err for err in errors)


def test_validate_root_rejects_non_string_tool_mapping_key(tmp_path: Path) -> None:
    _write_skill(tmp_path, "bad-map-key-type", """---
name: bad-map-key-type
description: sample
version: 1.0.0
owner: test
triggers:
  - x
tools:
  - jira_get_issue
opencode:
  execution_kind: prompt_only
  compatibility: degraded
  permission:
    default: ask
  capability_tags:
    - test
  tool_mappings:
    123: efp_jira_get_issue
---
""")
    exit_code, errors, _ = validate_root(tmp_path, opencode_compatible=True)
    assert exit_code == 1
    assert any("opencode.tool_mappings keys must be non-empty strings" in err for err in errors)
    assert any("missing mapping for tool 'jira_get_issue'" in err for err in errors)


def test_validate_root_rejects_tool_item_with_whitespace(tmp_path: Path) -> None:
    _write_skill(tmp_path, "bad-tool-space", """---
name: bad-tool-space
description: sample
version: 1.0.0
owner: test
triggers:
  - x
tools:
  - " jira_get_issue "
opencode:
  execution_kind: prompt_only
  compatibility: degraded
  permission:
    default: ask
  capability_tags:
    - test
  tool_mappings:
    jira_get_issue: efp_jira_get_issue
---
Body
""")
    exit_code, errors, stats = validate_root(tmp_path, opencode_compatible=True)
    assert exit_code == 1
    assert any("'tools' item ' jira_get_issue ' must not include leading or trailing whitespace" in err for err in errors)
    assert stats["opencode_tool_mapped_skill_count"] == 0


def test_validate_root_rejects_tool_mapping_value_with_whitespace(tmp_path: Path) -> None:
    _write_skill(tmp_path, "bad-map-value-space", """---
name: bad-map-value-space
description: sample
version: 1.0.0
owner: test
triggers:
  - x
tools:
  - jira_get_issue
opencode:
  execution_kind: prompt_only
  compatibility: degraded
  permission:
    default: ask
  capability_tags:
    - test
  tool_mappings:
    jira_get_issue: " efp_jira_get_issue "
---
Body
""")
    exit_code, errors, stats = validate_root(tmp_path, opencode_compatible=True)
    assert exit_code == 1
    assert any("opencode.tool_mappings.jira_get_issue value ' efp_jira_get_issue ' must not include leading or trailing whitespace" in err for err in errors)
    assert stats["opencode_tool_mapped_skill_count"] == 0
    assert stats["opencode_tool_mapping_count"] == 0


def test_validate_root_rejects_duplicate_tool_mapping_key(tmp_path: Path) -> None:
    _write_skill(tmp_path, "duplicate-tool-mapping", """---
name: duplicate-tool-mapping
description: sample
version: 1.0.0
owner: test
triggers:
  - x
tools:
  - jira_get_issue
opencode:
  execution_kind: prompt_only
  compatibility: degraded
  permission:
    default: ask
  capability_tags:
    - test
  tool_mappings:
    jira_get_issue: efp_wrong
    jira_get_issue: efp_jira_get_issue
---
Body
""")
    exit_code, errors, stats = validate_root(tmp_path, opencode_compatible=True)
    assert exit_code == 1
    assert any(
        ("duplicate key" in err or "duplicate frontmatter key" in err)
        and "jira_get_issue" in err
        for err in errors
    )
    assert stats["opencode_tool_mapped_skill_count"] == 0
    assert stats["opencode_tool_mapping_count"] == 0


def test_validate_root_rejects_duplicate_top_level_frontmatter_key(tmp_path: Path) -> None:
    _write_skill(tmp_path, "duplicate-top-level", """---
name: duplicate-top-level
name: duplicate-top-level-again
description: sample
version: 1.0.0
owner: test
triggers:
  - x
opencode:
  execution_kind: prompt_only
  compatibility: full
  permission:
    default: ask
  capability_tags:
    - test
---
Body
""")
    exit_code, errors, _ = validate_root(tmp_path, opencode_compatible=True)
    assert exit_code == 1
    assert any(
        ("duplicate key" in err or "duplicate frontmatter key" in err)
        and "name" in err
        for err in errors
    )


def test_current_repository_passes_t13_opencode_validation() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    exit_code, errors, stats = validate_root(repo_root, opencode_compatible=True)

    assert exit_code == 0, "\n".join(errors)
    assert errors == []

    # Skills are distributed on per-role branches, each shipping a subset, so
    # the absolute count is a property of the branch rather than of the
    # contract. Assert what must hold everywhere: every skill directory carries
    # a skill.md, and every discovered skill gets OpenCode metadata.
    on_disk = sum(
        1
        for entry in repo_root.iterdir()
        if entry.is_dir() and (entry / "skill.md").is_file()
    )
    assert on_disk > 0, "a branch with no skills is not a valid skill pack"
    assert stats["total_skill_directories"] == on_disk
    assert stats["total_skill_md_discovered"] == on_disk
    assert stats["opencode_normalized_skill_names"] == on_disk
    assert stats["opencode_metadata_count"] == on_disk
    assert stats["opencode_compatible_enabled"] == 1

    # Every remaining counter is derived from the skills actually present, the
    # same way opencode_tool_mapping_count already was. That still exercises the
    # validator's counting -- it just no longer encodes how many skills happen
    # to be on this branch.
    expected_permission: dict[str, int] = {}
    expected_execution_kind: dict[str, int] = {}
    expected_compatibility: dict[str, int] = {}
    expected_mapping_count = 0
    expected_tool_required = 0
    expected_tool_mapped = 0
    expected_python_backed = 0
    # Top-level only, matching what validate_root counts. rglob would also pull
    # in integration/fixtures, which is validated separately with its own root.
    for entry in sorted(repo_root.iterdir()):
        skill_md = entry / "skill.md"
        if not (entry.is_dir() and skill_md.is_file()):
            continue
        data, fm_errors = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        assert fm_errors == []
        opencode = data.get("opencode") if isinstance(data.get("opencode"), dict) else {}

        permission = opencode.get("permission") if isinstance(opencode.get("permission"), dict) else {}
        default = str(permission.get("default") or "")
        if default:
            expected_permission[default] = expected_permission.get(default, 0) + 1

        execution_kind = str(opencode.get("execution_kind") or "")
        if execution_kind:
            expected_execution_kind[execution_kind] = expected_execution_kind.get(execution_kind, 0) + 1

        compatibility = str(opencode.get("compatibility") or "")
        if compatibility:
            expected_compatibility[compatibility] = expected_compatibility.get(compatibility, 0) + 1

        if (skill_md.parent / "skill.py").exists():
            expected_python_backed += 1

        # Mirror _collect_legacy_tool_names: tools and task_tools together,
        # deduplicated. Counting only `tools` happened to agree with today's
        # data and would break on the first task_tools-only skill.
        required_tools: list[str] = []
        for field_name in ("tools", "task_tools"):
            values = data.get(field_name)
            if not isinstance(values, list):
                continue
            for item in values:
                if isinstance(item, str) and item.strip() and item.strip() not in required_tools:
                    required_tools.append(item.strip())
        if required_tools:
            expected_tool_required += 1

        mappings = opencode.get("tool_mappings") if isinstance(opencode.get("tool_mappings"), dict) else {}
        # "Mapped" means the mapping covers every required tool, not merely that
        # some mapping exists.
        if required_tools and len(mappings) == len(required_tools):
            expected_tool_mapped += 1
        expected_mapping_count += len(mappings)

    assert stats["opencode_permission_default_allow_count"] == expected_permission.get("allow", 0)
    assert stats["opencode_permission_default_ask_count"] == expected_permission.get("ask", 0)
    assert stats["opencode_permission_default_deny_count"] == expected_permission.get("deny", 0)
    assert stats["opencode_execution_kind_prompt_only_count"] == expected_execution_kind.get("prompt_only", 0)
    assert stats["opencode_execution_kind_programmatic_count"] == expected_execution_kind.get("programmatic", 0)
    assert stats["opencode_execution_kind_hybrid_count"] == expected_execution_kind.get("hybrid", 0)
    assert stats["opencode_compatibility_full_count"] == expected_compatibility.get("full", 0)
    assert stats["opencode_compatibility_degraded_count"] == expected_compatibility.get("degraded", 0)
    assert stats["opencode_compatibility_unsupported_count"] == expected_compatibility.get("unsupported", 0)
    assert stats["python_backed_skills_count"] == expected_python_backed
    assert stats["opencode_tool_required_skill_count"] == expected_tool_required
    assert stats["opencode_tool_mapped_skill_count"] == expected_tool_mapped
    assert stats["opencode_tool_mapping_count"] == expected_mapping_count


def test_validate_root_rejects_nested_skills_directory(tmp_path: Path) -> None:
    (tmp_path / "skills").mkdir()

    exit_code, errors, _ = validate_root(tmp_path, opencode_compatible=True)

    assert exit_code == 1
    assert any("nested skills/ directory is not allowed" in err for err in errors)


def test_validate_root_rejects_generated_opencode_artifacts(tmp_path: Path) -> None:
    (tmp_path / ".opencode").mkdir()
    (tmp_path / "skills-index.json").write_text("{}", encoding="utf-8")

    exit_code, errors, _ = validate_root(tmp_path, opencode_compatible=True)

    assert exit_code == 1
    assert any("generated OpenCode artifacts" in err for err in errors)
    assert any("skills-index.json" in err for err in errors)


def test_validate_root_counts_legacy_root_markdown_skill(tmp_path: Path) -> None:
    (tmp_path / "legacy.md").write_text(
        """---
name: legacy-skill
description: legacy root skill
version: 1.0.0
owner: test
triggers:
  - legacy
tools: []
""" + VALID_OPENCODE_BLOCK + """
---
Body
""",
        encoding="utf-8",
    )

    exit_code, errors, stats = validate_root(tmp_path, opencode_compatible=True)

    assert exit_code == 0
    assert errors == []
    assert stats["total_skill_directories"] == 0
    assert stats["total_skill_md_discovered"] == 1
    assert stats["opencode_normalized_skill_names"] == 1


def test_main_accepts_explicit_root(tmp_path: Path) -> None:
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
""" + VALID_OPENCODE_BLOCK + """
---
Body
""",
    )

    assert main(["--root", str(tmp_path), "--opencode-compatible"]) == 0


def test_main_returns_2_for_missing_root(tmp_path: Path) -> None:
    missing = tmp_path / "missing"

    assert main(["--root", str(missing), "--opencode-compatible"]) == 2


def test_validate_root_requires_opencode_metadata_in_opencode_mode(tmp_path: Path) -> None:
    _write_skill(
        tmp_path,
        "missing-opencode",
        """---
name: missing-opencode
description: sample
version: 1.0.0
owner: test
triggers:
  - x
tools: []
---
""",
    )
    exit_code, errors, _ = validate_root(tmp_path, opencode_compatible=True)
    assert exit_code == 1
    assert any("missing or invalid 'opencode' mapping" in err for err in errors)


def test_validate_root_rejects_invalid_opencode_permission_default(tmp_path: Path) -> None:
    _write_skill(tmp_path, "bad-permission", f"""---
name: bad-permission
description: sample
version: 1.0.0
owner: test
triggers:
  - x
tools: []
opencode:
  execution_kind: prompt_only
  compatibility: full
  permission:
    default: sometimes
  capability_tags:
    - test
---
""")
    exit_code, errors, _ = validate_root(tmp_path, opencode_compatible=True)
    assert exit_code == 1
    assert any("opencode.permission.default must be one of" in err for err in errors)


def test_validate_root_rejects_invalid_opencode_execution_kind(tmp_path: Path) -> None:
    _write_skill(tmp_path, "bad-kind", f"""---
name: bad-kind
description: sample
version: 1.0.0
owner: test
triggers:
  - x
tools: []
opencode:
  execution_kind: script
  compatibility: full
  permission:
    default: ask
  capability_tags:
    - test
---
""")
    exit_code, errors, _ = validate_root(tmp_path, opencode_compatible=True)
    assert exit_code == 1
    assert any("opencode.execution_kind must be one of" in err for err in errors)


def test_validate_root_rejects_invalid_opencode_compatibility(tmp_path: Path) -> None:
    _write_skill(tmp_path, "bad-compat", f"""---
name: bad-compat
description: sample
version: 1.0.0
owner: test
triggers:
  - x
tools: []
opencode:
  execution_kind: prompt_only
  compatibility: partial
  permission:
    default: ask
  capability_tags:
    - test
---
""")
    exit_code, errors, _ = validate_root(tmp_path, opencode_compatible=True)
    assert exit_code == 1
    assert any("opencode.compatibility must be one of" in err for err in errors)


def test_validate_root_rejects_python_backed_skill_claiming_prompt_only(tmp_path: Path) -> None:
    _write_skill(tmp_path, "py-skill", f"""---
name: py-skill
description: sample
version: 1.0.0
owner: test
triggers:
  - x
tools: []
{VALID_OPENCODE_BLOCK}
---
""")
    (tmp_path / "py-skill" / "skill.py").write_text("", encoding="utf-8")
    exit_code, errors, _ = validate_root(tmp_path, opencode_compatible=True)
    assert exit_code == 1
    assert any("Python-backed skill cannot use opencode.execution_kind=prompt_only" in err for err in errors)


def test_validate_root_rejects_python_backed_skill_claiming_full_compatibility(tmp_path: Path) -> None:
    _write_skill(tmp_path, "py-full", """---
name: py-full
description: sample
version: 1.0.0
owner: test
triggers:
  - x
tools: []
opencode:
  execution_kind: programmatic
  compatibility: full
  permission:
    default: ask
  capability_tags:
    - test
---
""")
    (tmp_path / "py-full" / "skill.py").write_text("", encoding="utf-8")
    exit_code, errors, _ = validate_root(tmp_path, opencode_compatible=True)
    assert exit_code == 1
    assert any("Python-backed skill cannot claim opencode.compatibility=full" in err for err in errors)


def test_validate_root_rejects_unsupported_skill_without_deny_permission(tmp_path: Path) -> None:
    _write_skill(tmp_path, "bad-unsupported", """---
name: bad-unsupported
description: sample
version: 1.0.0
owner: test
triggers:
  - x
tools: []
opencode:
  execution_kind: programmatic
  compatibility: unsupported
  permission:
    default: ask
  capability_tags:
    - test
---
""")
    exit_code, errors, _ = validate_root(tmp_path, opencode_compatible=True)
    assert exit_code == 1
    assert any("unsupported OpenCode skill must use opencode.permission.default=deny" in err for err in errors)


def test_validate_root_rejects_invalid_opencode_capability_tags(tmp_path: Path) -> None:
    _write_skill(tmp_path, "bad-tags", """---
name: bad-tags
description: sample
version: 1.0.0
owner: test
triggers:
  - x
tools: []
opencode:
  execution_kind: prompt_only
  compatibility: full
  permission:
    default: ask
  capability_tags: []
---
""")
    exit_code, errors, _ = validate_root(tmp_path, opencode_compatible=True)
    assert exit_code == 1
    assert any("opencode.capability_tags must be a non-empty list of strings" in err for err in errors)


def test_integration_fixture_passes_opencode_validation() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    fixture_root = repo_root / "integration" / "fixtures"
    exit_code, errors, stats = validate_root(fixture_root, opencode_compatible=True)
    assert exit_code == 0, "\n".join(errors)
    assert stats["total_skill_md_discovered"] >= 1
    assert stats["opencode_permission_default_allow_count"] == 1
