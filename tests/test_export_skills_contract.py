from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.export_skills_contract import ContractValidationError, build_contract, main
from scripts.validate_skills import validate_root


def _write_skill(skill_dir: Path, body: str) -> None:
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "skill.md").write_text(body, encoding="utf-8")


def test_build_contract_exports_expected_minimal_skill(tmp_path: Path) -> None:
    _write_skill(
        tmp_path / "review-pull-request",
        """---
name: review-pull-request
description: Review PR skill
version: 1.0.0
owner: engineering-flow-platform
triggers:
  - /review-pr
opencode:
  execution_kind: prompt_only
  compatibility: full
  permission:
    default: ask
  capability_tags:
    - prompt-only
---
Body is ignored.
""",
    )

    contract = build_contract(tmp_path, scope="production")

    assert contract["schema_version"] == "efp.skills.contract.v1"
    assert contract["scope"] == "production"
    assert len(contract["skills"]) == 1
    assert contract["skills"][0]["normalized_opencode_name"] == "review-pull-request"
    assert contract["skills"][0]["python_backed"] is False
    assert contract["skills"][0]["opencode"]["permission_default"] == "ask"


def test_build_contract_exports_tool_mappings(tmp_path: Path) -> None:
    _write_skill(
        tmp_path / "jira-helper",
        """---
name: jira-helper
description: Jira helper
version: 1.0.0
owner: engineering-flow-platform
triggers:
  - /jira
tools:
  - jira_get_issue
task_tools:
  - jira_search
opencode:
  execution_kind: prompt_only
  compatibility: degraded
  permission:
    default: ask
  capability_tags:
    - tools-required
  tool_mappings:
    jira_get_issue: efp_jira_get_issue
    jira_search: efp_jira_search
---
""",
    )

    contract = build_contract(tmp_path, scope="production")
    skill = contract["skills"][0]

    assert skill["tools"] == ["jira_get_issue"]
    assert skill["task_tools"] == ["jira_search"]
    assert skill["opencode"]["tool_mappings"] == {
        "jira_get_issue": "efp_jira_get_issue",
        "jira_search": "efp_jira_search",
    }
    assert contract["stats"]["opencode_tool_required_skill_count"] == 1
    assert contract["stats"]["opencode_tool_mapped_skill_count"] == 1
    assert contract["stats"]["opencode_tool_mapping_count"] == 2


def test_build_contract_is_deterministic(tmp_path: Path) -> None:
    _write_skill(
        tmp_path / "deterministic",
        """---
name: deterministic
description: Stable contract
version: 1.0.0
owner: engineering-flow-platform
trigger: /deterministic
opencode:
  execution_kind: prompt_only
  compatibility: full
  permission:
    default: ask
  capability_tags:
    - prompt-only
---
""",
    )

    first = build_contract(tmp_path, scope="production")
    second = build_contract(tmp_path, scope="production")

    assert first == second
    encoded = json.dumps(first, ensure_ascii=False, sort_keys=True)
    assert str(tmp_path) not in encoded


def test_main_writes_pretty_json(tmp_path: Path) -> None:
    _write_skill(
        tmp_path / "pretty",
        """---
name: pretty
description: Pretty output
version: 1.0.0
owner: engineering-flow-platform
triggers:
  - /pretty
opencode:
  execution_kind: prompt_only
  compatibility: full
  permission:
    default: ask
  capability_tags:
    - prompt-only
---
""",
    )
    output = tmp_path / "out" / "contract.json"

    exit_code = main(["--root", str(tmp_path), "--output", str(output), "--pretty"])

    assert exit_code == 0
    assert output.exists()
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["schema_version"] == "efp.skills.contract.v1"
    content = output.read_text(encoding="utf-8")
    assert "\n" in content
    assert "  \"schema_version\"" in content


def test_main_does_not_write_when_validation_fails(tmp_path: Path) -> None:
    _write_skill(
        tmp_path / "invalid",
        """---
name: invalid
description: Missing opencode metadata
version: 1.0.0
owner: engineering-flow-platform
triggers:
  - /invalid
---
""",
    )
    output = tmp_path / "contract.json"

    exit_code = main(["--root", str(tmp_path), "--output", str(output)])

    assert exit_code == 1
    assert not output.exists()


def test_current_repository_contract_matches_validator_stats() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    exit_code, _, stats = validate_root(repo_root, opencode_compatible=True)
    contract = build_contract(repo_root, scope="production")

    assert exit_code == 0
    assert contract["stats"] == stats
    assert len(contract["skills"]) == stats["total_skill_md_discovered"]
    assert all(skill["opencode"]["permission_default"] != "allow" for skill in contract["skills"])


def test_integration_fixture_contract_allows_deterministic_allow() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    fixture_root = repo_root / "integration" / "fixtures"

    contract = build_contract(fixture_root, scope="integration-fixtures")

    assert contract["scope"] == "integration-fixtures"
    assert len(contract["skills"]) >= 1
    fixture_skill = next(
        skill for skill in contract["skills"] if skill["name"] == "opencode-deterministic-fixture"
    )
    assert fixture_skill["opencode"]["permission_default"] == "allow"


def test_build_contract_rejects_validation_errors(tmp_path: Path) -> None:
    _write_skill(
        tmp_path / "invalid",
        """---
name: invalid
description: Missing opencode metadata
version: 1.0.0
owner: engineering-flow-platform
triggers:
  - /invalid
---
""",
    )

    with pytest.raises(ContractValidationError) as exc:
        build_contract(tmp_path, scope="production")

    assert any("missing or invalid 'opencode' mapping" in err for err in exc.value.errors)


def test_build_contract_rejects_invalid_scope(tmp_path: Path) -> None:
    _write_skill(
        tmp_path / "valid",
        """---
name: valid
description: Valid skill
version: 1.0.0
owner: engineering-flow-platform
triggers:
  - /valid
opencode:
  execution_kind: prompt_only
  compatibility: full
  permission:
    default: ask
  capability_tags:
    - prompt-only
---
""",
    )

    with pytest.raises(ValueError) as exc:
        build_contract(tmp_path, scope="bad-scope")

    assert "invalid scope" in str(exc.value)


def test_build_contract_rejects_missing_root(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    with pytest.raises(FileNotFoundError):
        build_contract(missing, scope="production")


def test_contract_does_not_export_body_reference_body_skill_py_or_absolute_paths(tmp_path: Path) -> None:
    skill_dir = tmp_path / "metadata-only"
    _write_skill(
        skill_dir,
        """---
name: metadata-only
description: Metadata only skill
version: 1.0.0
owner: engineering-flow-platform
triggers:
  - /metadata-only
references:
  - ref.md
opencode:
  execution_kind: programmatic
  compatibility: unsupported
  permission:
    default: deny
  capability_tags:
    - python-backed
---
BODY_SHOULD_NOT_EXPORT
""",
    )
    (skill_dir / "ref.md").write_text("REFERENCE_SHOULD_NOT_EXPORT", encoding="utf-8")
    (skill_dir / "skill.py").write_text("PYTHON_SHOULD_NOT_EXPORT", encoding="utf-8")

    contract = build_contract(tmp_path, scope="production")
    encoded = json.dumps(contract, ensure_ascii=False, sort_keys=True)

    assert "BODY_SHOULD_NOT_EXPORT" not in encoded
    assert "REFERENCE_SHOULD_NOT_EXPORT" not in encoded
    assert "PYTHON_SHOULD_NOT_EXPORT" not in encoded
    assert str(tmp_path) not in encoded

    skill = contract["skills"][0]
    assert skill["python_backed"] is True
    assert skill["references"] == ["ref.md"]
    assert skill["path"] == "metadata-only/skill.md"
