"""The pptx-brand skill: knowledge in the skill, assets catalogued and small."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from scripts.validate_skills import parse_frontmatter, validate_root

from tests._skill_presence import require_skill


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "pptx-brand"
REFERENCES = SKILL_DIR / "references"
ASSETS = SKILL_DIR / "assets"
STYLE_NAMES = {"formal", "review", "keynote", "training"}
ICON_NAMES = {
    "target", "chart-up", "shield", "gear", "users", "clock", "check", "warning",
    "cloud", "lock", "bolt", "flag", "document", "server", "globe", "bulb",
}
MAX_ASSET_BYTES = 3 * 1024 * 1024


def _load_skill() -> tuple[dict[str, object], str]:
    content = require_skill("pptx-brand").read_text(encoding="utf-8")
    data, errors = parse_frontmatter(content)
    assert errors == []
    return data, content


def _engine():
    require_skill("pptx")
    spec = importlib.util.spec_from_file_location("pptx_build_deck_for_brand", REPO_ROOT / "pptx" / "scripts" / "build_deck.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_brand_skill_frontmatter_contract() -> None:
    data, _ = _load_skill()

    assert data["name"] == "pptx-brand"
    assert data["version"] == "1.0.0"
    assert data["owner"] == "engineering-flow-platform"
    assert "/pptx-brand" in data["triggers"]
    assert any("PPT" in str(trigger) for trigger in data["triggers"])
    assert data["references"] == [
        "references/style-guide.md",
        "references/assets.md",
        "references/text-examples.md",
        "references/styles.json",
    ]
    opencode = data["opencode"]
    assert opencode["execution_kind"] == "prompt_only"
    assert opencode["compatibility"] == "full"
    assert opencode["permission"]["default"] == "ask"
    assert "brand" in opencode["capability_tags"]
    assert "tools" not in data and "task_tools" not in data


def test_brand_skill_body_points_at_the_engine_and_absolute_assets() -> None:
    _, content = _load_skill()
    for fragment in (
        "/app/skills/pptx/scripts/build_deck.py",
        "--list-styles",
        "\"style\": \"formal\"",
        "\"styles_file\": \"/app/skills/pptx-brand/references/styles.json\"",
        "/app/skills/pptx-brand/assets/",
        "cat /app/skills/pptx-brand/references/style-guide.md",
        "inspect_template.py",
        "slice_icons.py",
        "workspace:output/",
        "icons/navy/",
        "icons/white/",
    ):
        assert fragment in content, fragment


def test_styles_file_loads_and_every_path_resolves() -> None:
    require_skill("pptx-brand")
    engine = _engine()

    document, errors = engine.load_styles(REFERENCES / "styles.json")

    assert errors == []
    assert document["default_style"] == "formal"
    assert set(document["styles"]) == STYLE_NAMES
    for name, style in document["styles"].items():
        assert style["description"], name
        theme = style["theme"]
        for key in ("primary", "accent", "text", "muted", "background", "light"):
            assert engine._is_hex(theme[key]), (name, key)
        assert theme["east_asian_font"], name
        paths = [style.get("template"), style["logo"]["light"], style["logo"]["dark"]]
        for raw in style["backgrounds"].values():
            paths.append(raw["image"] if isinstance(raw, dict) else raw)
        for raw in paths:
            if raw:
                assert engine.resolve_asset(raw, [REFERENCES]) is not None, (name, raw)
        # A style either uses the brand template or the plain page; both are covered.
    assert {bool(style.get("template")) for style in document["styles"].values()} == {True, False}
    dark = document["styles"]["keynote"]["theme"]
    assert dark["background"].upper() != "FFFFFF" and dark["hero_text"]


def test_assets_are_catalogued_and_small() -> None:
    require_skill("pptx-brand")
    catalogue = (REFERENCES / "assets.md").read_text(encoding="utf-8")
    style_guide = (REFERENCES / "style-guide.md").read_text(encoding="utf-8")

    for background in sorted((ASSETS / "backgrounds").glob("*.jpg")):
        assert background.name in catalogue, background.name
    for logo in ("logo-primary.png", "logo-white.png"):
        assert (ASSETS / "logo" / logo).is_file(), logo
        assert logo in catalogue
    assert "efp-brand-template.pptx" in catalogue
    for name in ICON_NAMES:
        assert f"`{name}`" in catalogue, name
        assert (ASSETS / "icons" / "navy" / f"{name}.png").is_file(), name
        assert (ASSETS / "icons" / "white" / f"{name}.png").is_file(), name
    manifest = json.loads((ASSETS / "icons" / "navy" / "icons.json").read_text(encoding="utf-8"))
    assert {entry["name"] for entry in manifest["icons"]} == ICON_NAMES
    assert (ASSETS / "icons" / "navy" / "contact-sheet.png").is_file()
    assert (ASSETS / "icons" / "icon-sheet.png").is_file()
    for name in STYLE_NAMES:
        assert f"`{name}`" in style_guide, name

    total = sum(path.stat().st_size for path in ASSETS.rglob("*") if path.is_file())
    assert total < MAX_ASSET_BYTES, total


def test_brand_skill_passes_repo_validator() -> None:
    require_skill("pptx-brand")
    _exit_code, errors, _stats = validate_root(REPO_ROOT, opencode_compatible=True)
    assert [error for error in errors if "pptx-brand" in error] == []
