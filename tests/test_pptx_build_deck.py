"""Behaviour of pptx/scripts/build_deck.py.

Spec validation and the CLI contract need only the standard library; the
rendering test runs when python-pptx happens to be installed.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from tests._skill_presence import require_skill


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "pptx" / "scripts" / "build_deck.py"
EXAMPLE = REPO_ROOT / "pptx" / "references" / "spec-example.json"


def _python_pptx_installed() -> bool:
    """True only for the real library.

    With the repo root on sys.path the skill directory ``pptx/`` is importable
    as an empty namespace package, so ``find_spec("pptx")`` is not enough.
    """
    try:
        module = importlib.import_module("pptx")
    except ImportError:
        return False
    return hasattr(module, "Presentation")


needs_python_pptx = pytest.mark.skipif(not _python_pptx_installed(), reason="python-pptx is not installed")


def _load_module():
    require_skill("pptx")
    spec = importlib.util.spec_from_file_location("pptx_build_deck", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def _example() -> dict:
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def test_example_spec_validates_clean() -> None:
    module = _load_module()

    errors, warnings = module.validate_spec(_example(), EXAMPLE.parent)

    assert errors == []
    assert warnings == []


def test_validate_spec_reports_errors_and_warnings(tmp_path: Path) -> None:
    module = _load_module()
    spec = {
        "title": "Broken deck",
        "theme": {"primary": "not-a-colour"},
        "slides": [
            {"type": "chart", "title": "t", "chart": {"kind": "radar", "categories": ["a"], "series": [{"values": [1, 2]}]}},
            {"type": "image", "title": "i", "image": "missing.png"},
            {"type": "bullets", "title": "b", "bullets": [{"text": "x", "level": 5}] + [f"bullet {i}" for i in range(9)]},
            {"type": "kpi", "title": "k", "metrics": [{"value": "1"}]},
            {"type": "quote"},
            {"type": "unknown", "title": "u"},
            "not-an-object",
        ],
    }

    errors, warnings = module.validate_spec(spec, tmp_path)

    joined = "\n".join(errors)
    assert "chart.kind must be one of" in joined
    assert "has 2 values for 1 categories" in joined
    assert "image not found: missing.png" in joined
    assert "level must be 0, 1 or 2" in joined
    assert "metrics[0] needs 'value' and 'label'" in joined
    assert "'quote' text is required" in joined
    assert "unknown type 'unknown'" in joined
    assert "slides[6]: must be an object" in joined

    joined_warnings = "\n".join(warnings)
    assert "theme.primary is not a 6-digit hex colour" in joined_warnings
    assert "10 bullets on one slide" in joined_warnings


def test_validate_spec_rejects_non_object_and_empty_slides() -> None:
    module = _load_module()

    assert module.validate_spec([], None)[0] == ["spec must be a JSON object"]
    errors, _ = module.validate_spec({"title": "x", "slides": []}, None)
    assert "'slides' must be a non-empty list" in errors


def test_resolve_output_path_defaults_and_extension() -> None:
    module = _load_module()

    assert module.resolve_output_path({"title": "Q3 Platform Review"}, None) == Path("output/Q3-Platform-Review.pptx")
    assert module.resolve_output_path({"title": "季度复盘 / 汇报"}, None) == Path("output/季度复盘-汇报.pptx")
    assert module.resolve_output_path({}, None) == Path("output/deck.pptx")
    assert module.resolve_output_path({"output": "output/x.ppt"}, None) == Path("output/x.pptx")
    assert module.resolve_output_path({"output": "output/x.pptx"}, "custom/y.pptx") == Path("custom/y.pptx")


def test_resolve_theme_keeps_valid_overrides_only() -> None:
    module = _load_module()

    theme = module.resolve_theme({"theme": {"primary": "#123abc", "accent": "nope", "east_asian_font": "Noto Sans CJK SC"}})

    assert theme["primary"] == "123ABC"
    assert theme["accent"] == module.DEFAULT_THEME["accent"]
    assert theme["east_asian_font"] == "Noto Sans CJK SC"
    assert theme["title_font"] == theme["font"]


def test_cli_validate_only_prints_json(capsys: pytest.CaptureFixture[str]) -> None:
    module = _load_module()

    exit_code = module.main([str(EXAMPLE), "--validate-only", "--quiet"])

    payload = json.loads(capsys.readouterr().out.strip())
    assert exit_code == 0
    assert payload["ok"] is True
    assert payload["validated"] is True
    assert payload["slides"] == len(_example()["slides"])


def test_cli_reports_invalid_spec_with_exit_code_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    module = _load_module()
    spec_path = tmp_path / "bad.json"
    spec_path.write_text(json.dumps({"title": "x", "slides": [{"type": "quote"}]}), encoding="utf-8")

    exit_code = module.main([str(spec_path), "--quiet"])

    payload = json.loads(capsys.readouterr().out.strip())
    assert exit_code == 2
    assert payload["ok"] is False
    assert any("'quote' text is required" in error for error in payload["errors"])


def test_cli_print_example_matches_reference(capsys: pytest.CaptureFixture[str]) -> None:
    module = _load_module()

    assert module.main(["--print-example"]) == 0
    assert json.loads(capsys.readouterr().out) == _example()


@needs_python_pptx
def test_build_example_deck_renders_every_slide(tmp_path: Path) -> None:
    module = _load_module()
    output = tmp_path / "out" / "deck.pptx"

    summary = module.build_deck(_example(), output, base_dir=EXAMPLE.parent)

    assert summary["ok"] is True
    assert summary["warnings"] == []
    # The example has no explicit title slide, so one is generated first.
    assert summary["slides"] == len(_example()["slides"]) + 1
    assert output.is_file() and output.stat().st_size > 0

    from pptx import Presentation

    presentation = Presentation(str(output))
    slides = list(presentation.slides)
    assert len(slides) == summary["slides"]
    first_texts = [shape.text_frame.text for shape in slides[0].shapes if shape.has_text_frame]
    assert "Q3 Platform Review" in first_texts
    agenda = slides[1]
    assert agenda.has_notes_slide
    assert "under a minute" in agenda.notes_slide.notes_text_frame.text
    assert presentation.core_properties.title == "Q3 Platform Review"


@needs_python_pptx
def test_build_keeps_every_shape_inside_the_slide(tmp_path: Path) -> None:
    """Layout maths is relative to the slide size; nothing may hang off the edge."""
    module = _load_module()
    spec = _example()
    spec["theme"]["east_asian_font"] = "Microsoft YaHei"
    spec["slides"].insert(
        1,
        {
            "type": "kpi",
            "title": "六个指标",
            "metrics": [{"value": str(i), "label": f"指标 {i}"} for i in range(6)],
        },
    )
    output = tmp_path / "bounds.pptx"

    summary = module.build_deck(spec, output, base_dir=EXAMPLE.parent)
    assert summary["ok"] is True

    from pptx import Presentation

    presentation = Presentation(str(output))
    width, height = presentation.slide_width, presentation.slide_height
    for index, slide in enumerate(presentation.slides, start=1):
        for shape in slide.shapes:
            assert shape.left >= 0 and shape.top >= 0, (index, shape.name)
            assert shape.left + shape.width <= width, (index, shape.name)
            assert shape.top + shape.height <= height, (index, shape.name)
