#!/usr/bin/env python3
"""Describe a PowerPoint template so an agent can write a spec against it.

Usage:
    python inspect_template.py TEMPLATE.pptx|TEMPLATE.potx [--max-text 240] [--quiet]

Prints one JSON document with: slide size, the theme's colour scheme and
fonts, every slide layout with its placeholders, and every sample slide's
title, texts and speaker notes. Enterprise templates carry their "text
examples" as sample slides; this is how the agent reads them without opening
PowerPoint. ``blank_layout`` names the layout build_deck.py will draw on.

Exit codes: 0 ok, 2 file problem, 3 python-pptx missing.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

DRAWINGML_NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
COLOR_SLOTS = ("dk1", "lt1", "dk2", "lt2", "accent1", "accent2", "accent3", "accent4", "accent5", "accent6", "hlink", "folHlink")


def _theme_part(prs):
    from pptx.opc.constants import RELATIONSHIP_TYPE as RT

    for rel in prs.slide_master.part.rels.values():
        if rel.reltype == RT.THEME:
            return rel.target_part
    return None


def read_theme(prs) -> dict[str, Any]:
    """Colour scheme and font scheme of the first master's theme."""
    from lxml import etree

    part = _theme_part(prs)
    if part is None:
        return {}
    root = etree.fromstring(part.blob)
    theme: dict[str, Any] = {"name": root.get("name") or ""}
    scheme = root.find(".//a:clrScheme", DRAWINGML_NS)
    colors: dict[str, str | None] = {}
    if scheme is not None:
        theme["scheme_name"] = scheme.get("name") or ""
        for slot in COLOR_SLOTS:
            node = scheme.find(f"a:{slot}", DRAWINGML_NS)
            if node is None:
                continue
            srgb = node.find("a:srgbClr", DRAWINGML_NS)
            system = node.find("a:sysClr", DRAWINGML_NS)
            if srgb is not None:
                colors[slot] = str(srgb.get("val") or "").upper()
            elif system is not None:
                colors[slot] = str(system.get("lastClr") or "").upper() or None
    theme["colors"] = colors
    fonts: dict[str, str] = {}
    for kind in ("major", "minor"):
        node = root.find(f".//a:fontScheme/a:{kind}Font", DRAWINGML_NS)
        if node is None:
            continue
        for script in ("latin", "ea", "cs"):
            face = node.find(f"a:{script}", DRAWINGML_NS)
            if face is not None and face.get("typeface"):
                fonts[f"{kind}_{script}"] = face.get("typeface")
    theme["fonts"] = fonts
    # Suggested build_deck theme block: dk2 is usually the brand's dark colour.
    suggestion = {
        "primary": colors.get("dk2") or colors.get("accent1"),
        "accent": colors.get("accent2") or colors.get("accent1"),
        "text": colors.get("dk1"),
        "background": colors.get("lt1"),
        "light": colors.get("lt2"),
        "font": fonts.get("minor_latin"),
        "title_font": fonts.get("major_latin"),
        "east_asian_font": fonts.get("minor_ea") or fonts.get("major_ea"),
    }
    theme["build_deck_theme"] = {k: v for k, v in suggestion.items() if v}
    return theme


def _placeholder_type(placeholder) -> str:
    kind = placeholder.placeholder_format.type
    return getattr(kind, "name", str(kind))


def read_layouts(prs) -> list[dict[str, Any]]:
    layouts = []
    for index, layout in enumerate(prs.slide_layouts):
        placeholders = [
            {"idx": ph.placeholder_format.idx, "type": _placeholder_type(ph), "name": ph.name}
            for ph in layout.placeholders
        ]
        decorations = sum(1 for shape in layout.shapes if not shape.is_placeholder)
        layouts.append({"index": index, "name": layout.name, "placeholders": placeholders, "decorations": decorations})
    return layouts


def _blank_layout_name(prs) -> str:
    layouts = list(prs.slide_layouts)
    for layout in layouts:
        if str(layout.name or "").strip().lower() in {"blank", "空白"}:
            return layout.name
    return min(layouts, key=lambda layout: len(layout.placeholders)).name


def read_slides(prs, *, max_text: int) -> list[dict[str, Any]]:
    from pptx.enum.shapes import MSO_SHAPE_TYPE

    slides = []
    for index, slide in enumerate(prs.slides, start=1):
        title_shape = slide.shapes.title
        title = title_shape.text.strip() if title_shape is not None and title_shape.has_text_frame else ""
        texts: list[str] = []
        pictures = tables = charts = 0
        for shape in slide.shapes:
            if title_shape is not None and shape.shape_id == title_shape.shape_id:
                continue
            if getattr(shape, "shape_type", None) == MSO_SHAPE_TYPE.PICTURE:
                pictures += 1
            if getattr(shape, "has_table", False) and shape.has_table:
                tables += 1
            if getattr(shape, "has_chart", False) and shape.has_chart:
                charts += 1
            if shape.has_text_frame:
                text = " ".join(part for part in shape.text_frame.text.split() if part)
                if text:
                    texts.append(text[:max_text])
        notes = ""
        if slide.has_notes_slide:
            notes = slide.notes_slide.notes_text_frame.text.strip()[:max_text]
        if not title and texts:
            # Decks drawn with text boxes (build_deck.py included) have no title
            # placeholder; the first text is the title by construction.
            title = texts.pop(0)
        slides.append(
            {
                "index": index,
                "layout": slide.slide_layout.name,
                "title": title[:max_text],
                "texts": texts,
                "pictures": pictures,
                "tables": tables,
                "charts": charts,
                "notes": notes,
            }
        )
    return slides


def inspect_template(path: Path, *, max_text: int = 240) -> dict[str, Any]:
    from pptx import Presentation
    from pptx.util import Emu

    prs = Presentation(str(path))
    width, height = Emu(prs.slide_width), Emu(prs.slide_height)
    return {
        "ok": True,
        "file": str(path),
        "slide_size_in": [round(width.inches, 3), round(height.inches, 3)],
        "aspect_ratio": round(width / height, 3),
        "masters": len(list(prs.slide_masters)),
        "theme": read_theme(prs),
        "blank_layout": _blank_layout_name(prs),
        "layouts": read_layouts(prs),
        "slides": read_slides(prs, max_text=max_text),
    }


def main(argv: list[str] | None = None) -> int:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):
            pass
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("template", help="Path to a .pptx or .potx file")
    parser.add_argument("--max-text", type=int, default=240, help="Truncate each text to this many characters")
    parser.add_argument("--quiet", action="store_true", help="Single-line JSON output")
    args = parser.parse_args(argv)

    path = Path(args.template).expanduser()
    if not path.is_file():
        print(json.dumps({"ok": False, "errors": [f"template not found: {path}"]}))
        return 2
    try:
        from pptx import Presentation  # noqa: F401
    except ImportError:
        print(json.dumps({"ok": False, "errors": ["python-pptx is not installed; run `python -m pip install --user python-pptx`"]}))
        return 3
    try:
        report = inspect_template(path, max_text=max(20, args.max_text))
    except Exception as exc:
        print(json.dumps({"ok": False, "errors": [f"{exc.__class__.__name__}: {exc}"]}, ensure_ascii=False))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=None if args.quiet else 2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
