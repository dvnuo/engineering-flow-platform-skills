from __future__ import annotations

from pathlib import Path

from scripts.validate_skills import parse_frontmatter, validate_root

from tests._skill_presence import require_skill


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "pptx"
SKILL_PATH = SKILL_DIR / "skill.md"


def _load_skill() -> tuple[dict[str, object], str]:
    content = require_skill("pptx").read_text(encoding="utf-8")
    data, errors = parse_frontmatter(content)
    assert errors == []
    return data, content


def test_pptx_skill_files_exist() -> None:
    require_skill("pptx")
    assert SKILL_DIR.is_dir()
    assert SKILL_PATH.is_file()
    assert (SKILL_DIR / "scripts" / "build_deck.py").is_file()
    assert (SKILL_DIR / "references" / "layout-guide.md").is_file()
    assert (SKILL_DIR / "references" / "spec-example.json").is_file()


def test_pptx_frontmatter_contract() -> None:
    data, _ = _load_skill()

    assert data["name"] == "pptx"
    assert data["version"] == "1.0.0"
    assert data["owner"] == "engineering-flow-platform"
    assert data["output_format"] == "markdown"

    triggers = data["triggers"]
    assert isinstance(triggers, list)
    assert "/pptx" in triggers
    # The skill is meant to be reachable from Chinese requests as well.
    assert any("PPT" in str(trigger) for trigger in triggers)

    assert data["references"] == ["references/layout-guide.md", "references/spec-example.json"]

    opencode = data.get("opencode")
    assert isinstance(opencode, dict)
    assert opencode["execution_kind"] == "prompt_only"
    assert opencode["compatibility"] == "full"

    permission = opencode.get("permission")
    assert isinstance(permission, dict)
    assert permission["default"] == "ask"

    assert "pptx" in opencode["capability_tags"]
    assert "opencode-bash-cli" in opencode["capability_tags"]


def test_pptx_declares_no_native_tools() -> None:
    data, _ = _load_skill()

    assert "tools" not in data
    assert "task_tools" not in data

    opencode = data.get("opencode")
    assert isinstance(opencode, dict)
    assert "tool_mappings" not in opencode


def test_pptx_body_contains_required_contract_clauses() -> None:
    _, content = _load_skill()

    required_fragments = [
        "scripts/build_deck.py",
        "--validate-only",
        "--print-example",
        "--template",
        ".efp/pptx/",
        "output/",
        "workspace:output/",
        "Server Files",
        "east_asian_font",
        "Never invent",
    ]
    for fragment in required_fragments:
        assert fragment in content, fragment


def test_pptx_skill_passes_repo_validator() -> None:
    require_skill("pptx")
    _exit_code, errors, _stats = validate_root(REPO_ROOT, opencode_compatible=True)
    assert [error for error in errors if "pptx" in error] == []
