"""Companion scripts of the pptx skill: slice_icons.py and inspect_template.py."""

from __future__ import annotations

import importlib
import importlib.util
import json
from pathlib import Path

import pytest

from tests._skill_presence import require_skill


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "pptx" / "scripts"
BRAND_TEMPLATE = REPO_ROOT / "pptx-brand" / "assets" / "template" / "efp-brand-template.pptx"


def _load(name: str):
    require_skill("pptx")
    spec = importlib.util.spec_from_file_location(f"pptx_{name}", SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def _has(module_name: str, attribute: str) -> bool:
    try:
        return hasattr(importlib.import_module(module_name), attribute)
    except ImportError:
        return False


needs_pillow = pytest.mark.skipif(not _has("PIL.Image", "new"), reason="Pillow is not installed")
needs_python_pptx = pytest.mark.skipif(not _has("pptx", "Presentation"), reason="python-pptx is not installed")


def test_slice_helpers_are_pure() -> None:
    module = _load("slice_icons")

    assert module.parse_grid("4x6") == (4, 6)
    assert module.parse_grid(" 2 X 3 ") == (2, 3)
    assert module.parse_grid(None) is None
    with pytest.raises(ValueError):
        module.parse_grid("4-6")
    assert module.slugify("Chart Up!", "icon-01") == "chart-up"
    assert module.slugify("   ", "icon-02") == "icon-02"
    # Runs of ink split by gaps shorter than min_gap are merged; tiny runs dropped.
    profile = [False] * 3 + [True] * 10 + [False] * 2 + [True] * 10 + [False] * 8 + [True] * 10 + [False] * 5 + [True]
    assert module.bands(profile, min_gap=4) == [(3, 25), (33, 43)]


def _make_sheet(path: Path, *, rows: int = 2, cols: int = 3, cell: int = 40, gap: int = 12):
    from PIL import Image, ImageDraw

    sheet = Image.new("RGBA", (cols * cell + (cols + 1) * gap, rows * cell + (rows + 1) * gap), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sheet)
    for index in range(rows * cols):
        x = gap + (index % cols) * (cell + gap)
        y = gap + (index // cols) * (cell + gap)
        draw.rectangle((x + 4, y + 4, x + cell - 4, y + cell - 4), fill=(20, 40, 80, 255))
    sheet.save(path)
    return sheet.size


@needs_pillow
def test_slice_icons_auto_detects_cells_and_writes_manifest(tmp_path: Path) -> None:
    module = _load("slice_icons")
    sheet = tmp_path / "sheet.png"
    _make_sheet(sheet)

    summary = module.slice_sheet(sheet, tmp_path / "out", names=["alpha", "beta", "Gamma Ray"], size=64)

    assert summary["ok"] is True
    assert (summary["rows"], summary["cols"], summary["icons"]) == (2, 3, 6)
    assert summary["names"] == ["alpha", "beta", "gamma-ray", "icon-04", "icon-05", "icon-06"]
    manifest = json.loads((tmp_path / "out" / "icons.json").read_text(encoding="utf-8"))
    assert [entry["row"] for entry in manifest["icons"]] == [1, 1, 1, 2, 2, 2]
    assert [entry["col"] for entry in manifest["icons"]] == [1, 2, 3, 1, 2, 3]
    assert (tmp_path / "out" / "contact-sheet.png").is_file()

    from PIL import Image

    icon = Image.open(tmp_path / "out" / "alpha.png")
    assert icon.size == (64, 64) and icon.mode == "RGBA"
    assert icon.getpixel((0, 0))[3] == 0  # padding stays transparent
    assert icon.getpixel((32, 32))[3] == 255


@needs_pillow
def test_slice_icons_grid_mode_and_opaque_background(tmp_path: Path) -> None:
    module = _load("slice_icons")
    sheet = tmp_path / "sheet.png"
    _make_sheet(sheet, rows=1, cols=2)
    from PIL import Image

    opaque = Image.open(sheet).convert("RGBA")
    flat = Image.new("RGBA", opaque.size, (255, 255, 255, 255))
    flat.paste(opaque, (0, 0), opaque)
    flat.convert("RGB").save(tmp_path / "flat.png")

    summary = module.slice_sheet(tmp_path / "flat.png", tmp_path / "grid", grid=(1, 2), size=32)

    assert summary["ok"] is True and summary["icons"] == 2
    assert sorted(p.name for p in (tmp_path / "grid").glob("icon-*.png")) == ["icon-01.png", "icon-02.png"]


@needs_pillow
def test_slice_icons_cli_reports_errors(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    module = _load("slice_icons")

    assert module.main([str(tmp_path / "missing.png"), "--out", str(tmp_path)]) == 2
    assert "sheet not found" in capsys.readouterr().out
    sheet = tmp_path / "sheet.png"
    _make_sheet(sheet)
    assert module.main([str(sheet), "--out", str(tmp_path / "o"), "--grid", "bad"]) == 2
    assert "ROWSxCOLS" in capsys.readouterr().out


@needs_python_pptx
@pytest.mark.skipif(not BRAND_TEMPLATE.is_file(), reason="pptx-brand template is not on this branch")
def test_inspect_template_reads_theme_layouts_and_sample_slides() -> None:
    module = _load("inspect_template")

    report = module.inspect_template(BRAND_TEMPLATE, max_text=80)

    assert report["ok"] is True
    assert report["slide_size_in"] == [13.333, 7.5]
    assert report["blank_layout"] == "Blank"
    colors = report["theme"]["colors"]
    assert colors["dk2"] == "0B2545" and colors["accent2"] == "E8590C" and colors["lt1"] == "FFFFFF"
    assert report["theme"]["fonts"]["minor_ea"] == "Microsoft YaHei"
    assert report["theme"]["build_deck_theme"]["primary"] == "0B2545"
    assert report["theme"]["build_deck_theme"]["east_asian_font"] == "Microsoft YaHei"
    assert any(layout["name"] == "Blank" for layout in report["layouts"])
    assert len(report["slides"]) == 11
    assert all(slide["title"] for slide in report["slides"])
    assert any(slide["notes"] for slide in report["slides"])
    assert sum(slide["charts"] for slide in report["slides"]) == 1
    assert sum(slide["tables"] for slide in report["slides"]) == 1


@needs_python_pptx
def test_inspect_template_cli_handles_missing_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    module = _load("inspect_template")

    assert module.main([str(tmp_path / "nope.pptx")]) == 2
    assert "template not found" in capsys.readouterr().out
