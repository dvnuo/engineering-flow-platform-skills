"""Contract checks for the PM / BA analysis and requirements skills.

These skills are prompt-only and run in the native EFP agent, where only
``name`` and ``description`` drive activation and the deliverable is a file
under ``output/`` announced with a ``workspace:`` link. The checks below keep
the eight skills on that contract: English skill text, a description that says
when to use the skill, the shared deliverable clauses, and a provenance README
that pins the upstream commit.
"""
from __future__ import annotations

import re
from pathlib import Path

from scripts.validate_skills import parse_frontmatter, validate_root

from tests._skill_presence import require_skills

REPO_ROOT = Path(__file__).resolve().parents[1]

# skill name -> deliverable prefix under output/
PM_BA_SKILLS: dict[str, str] = {
    "product-discovery": "discovery",
    "prioritize-roadmap": "roadmap",
    "define-product-metrics": "metrics",
    "write-product-requirements": "prd",
    "break-down-user-stories": "stories",
    "review-requirements-readiness": "readiness",
    "analyze-business-process": "process",
    "analyze-requirement-change": "change",
}

CJK = re.compile(r"[一-鿿]")
PINNED_SHA = re.compile(r"\b[0-9a-f]{40}\b")

# Clauses every PM / BA skill body must carry, in the wording the native agent
# and the Portal rely on (see pptx/skill.md for the precedent).
SHARED_CLAUSES = [
    "output/",
    "workspace:output/",
    "Server Files",
    "Never invent",
    "references/template.md",
    "uploads/",
    "language the member used",
    "`jira`",
    "`confluence`",
    "`gh`",
    "--json",
    "## Hand-offs",
    "## Provenance",
]


def _present() -> list[str]:
    return require_skills(list(PM_BA_SKILLS))


def _split(content: str) -> str:
    """Return the body after the YAML frontmatter."""

    assert content.startswith("---\n"), "skill.md must start with frontmatter"
    end = content.index("\n---\n", 4)
    return content[end + len("\n---\n") :]


def _load(name: str) -> tuple[dict[str, object], str]:
    content = (REPO_ROOT / name / "skill.md").read_text(encoding="utf-8")
    data, errors = parse_frontmatter(content)
    assert errors == [], (name, errors)
    return data, _split(content)


def test_pm_ba_skill_files_exist() -> None:
    for name in _present():
        skill_dir = REPO_ROOT / name
        assert (skill_dir / "skill.md").is_file(), name
        assert (skill_dir / "README.md").is_file(), name
        assert (skill_dir / "references" / "template.md").is_file(), name
        licence = skill_dir / "references" / "LICENSE.upstream.txt"
        assert licence.is_file(), name
        assert licence.read_text(encoding="utf-8").startswith("MIT License"), name
    assert (REPO_ROOT / "docs" / "pm-ba-skills-adoption.md").is_file()


def test_pm_ba_frontmatter_contract() -> None:
    for name in _present():
        data, _ = _load(name)

        assert data["name"] == name
        assert data["version"] == "1.0.0", name
        assert data["owner"] == "engineering-flow-platform", name
        assert data["output_format"] == "markdown", name

        triggers = data["triggers"]
        assert isinstance(triggers, list), name
        assert f"/{name}" in triggers, name
        # Reachable from Chinese requests too, as the pptx skill is.
        assert any(CJK.search(str(trigger)) for trigger in triggers), name

        # Only the template is a reference the skill reads; the licence file
        # stays in the directory but is not model context.
        assert data["references"] == ["references/template.md"], name

        assert data.get("tools", []) == [], name
        assert "task_tools" not in data, name

        opencode = data["opencode"]
        assert isinstance(opencode, dict), name
        assert opencode["execution_kind"] == "prompt_only", name
        assert opencode["compatibility"] == "full", name
        assert opencode["permission"]["default"] == "ask", name
        assert "prompt-only" in opencode["capability_tags"], name
        assert "deliverable" in opencode["capability_tags"], name
        assert "tool_mappings" not in opencode, name


def test_pm_ba_description_says_what_and_when() -> None:
    for name in _present():
        data, _ = _load(name)
        description = str(data["description"])
        # The native agent selects skills from the description alone.
        assert "Use when" in description, name
        assert not CJK.search(description), name
        assert len(description) <= 420, (name, len(description))


def test_pm_ba_skill_text_is_english() -> None:
    for name in _present():
        _, body = _load(name)
        assert not CJK.search(body), f"{name}: skill.md body must be English"
        for relative in ("README.md", "references/template.md"):
            text = (REPO_ROOT / name / relative).read_text(encoding="utf-8")
            assert not CJK.search(text), f"{name}/{relative} must be English"


def test_pm_ba_body_carries_deliverable_contract() -> None:
    for name in _present():
        _, body = _load(name)
        for clause in SHARED_CLAUSES:
            assert clause in body, (name, clause)
        prefix = PM_BA_SKILLS[name]
        assert f"output/{prefix}-<slug>.md" in body, name
        assert f"workspace:output/{prefix}-" in body, name
        if name == "break-down-user-stories":
            assert "output/stories-<slug>.csv" in body
            assert "jira_bulk_create_from_csv" in body


def test_pm_ba_readme_pins_upstream_sources() -> None:
    for name in _present():
        readme = (REPO_ROOT / name / "README.md").read_text(encoding="utf-8")
        assert "## Provenance" in readme, name
        assert "MIT" in readme, name
        assert PINNED_SHA.search(readme), f"{name}: README must pin an upstream commit"
        assert "LICENSE.upstream.txt" in readme, name


def test_pm_ba_skills_pass_repo_validator() -> None:
    present = _present()
    _exit_code, errors, _stats = validate_root(REPO_ROOT, opencode_compatible=True)
    related = [error for error in errors if any(name in error for name in present)]
    assert related == []
