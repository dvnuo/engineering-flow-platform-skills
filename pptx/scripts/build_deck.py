#!/usr/bin/env python3
"""Build a PowerPoint (.pptx) deck from a JSON spec with python-pptx.

Usage:
    python build_deck.py SPEC.json [--output PATH] [--template FILE.pptx]
                         [--validate-only] [--print-example] [--quiet]

The spec format is documented in ../references/layout-guide.md; a complete
example lives in ../references/spec-example.json (``--print-example`` prints
it). The script writes a JSON summary to stdout so an agent can read the
result without opening the file:

    {"ok": true, "output": "output/deck.pptx", "slides": 9, "warnings": [...]}

Exit codes: 0 built, 1 render failed, 2 spec invalid (errors listed in the
JSON), 3 python-pptx missing, 4 template unreadable.

Only the standard library is needed to validate a spec; python-pptx is imported
lazily when a deck is actually built.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

SLIDE_TYPES = {
    "title",
    "section",
    "bullets",
    "two_column",
    "image",
    "table",
    "chart",
    "kpi",
    "quote",
    "closing",
}
CHART_KINDS = {"bar", "column", "line", "pie", "doughnut"}
FONT_KEYS = {"font", "title_font", "east_asian_font"}
DEFAULT_THEME = {
    "primary": "1F3A5F",
    "accent": "E07A1F",
    "text": "1F2933",
    "muted": "6B7280",
    "background": "FFFFFF",
    "light": "F3F4F6",
    "font": "Calibri",
    "title_font": "",
    "east_asian_font": "",
}
SERIES_PALETTE = ["1F3A5F", "E07A1F", "2E8B57", "8E44AD", "C0392B", "16A085", "7F8C8D"]

MAX_BULLETS_PER_SLIDE = 8
MAX_BULLET_CHARS = 120
MAX_TITLE_CHARS = 70
MAX_TABLE_ROWS = 12
MAX_TABLE_COLS = 8
MAX_KPI_METRICS = 6

_HEX_RE = re.compile(r"^[0-9A-Fa-f]{6}$")


# --------------------------------------------------------------------------- #
# Spec validation (stdlib only)
# --------------------------------------------------------------------------- #


def _is_str(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _bullet_text(item: Any) -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        return str(item.get("text", ""))
    return ""


def _check_bullets(bullets: Any, where: str, errors: list[str], warnings: list[str]) -> None:
    if not isinstance(bullets, list) or not bullets:
        errors.append(f"{where}: 'bullets' must be a non-empty list")
        return
    for index, item in enumerate(bullets):
        if isinstance(item, str):
            text = item
        elif isinstance(item, dict) and _is_str(item.get("text")):
            text = str(item["text"])
            level = item.get("level", 0)
            if isinstance(level, bool) or not isinstance(level, int) or level < 0 or level > 2:
                errors.append(f"{where}: bullet {index} level must be 0, 1 or 2")
        else:
            errors.append(f"{where}: bullet {index} must be a string or {{'text': ..., 'level': n}}")
            continue
        if len(text) > MAX_BULLET_CHARS:
            warnings.append(
                f"{where}: bullet {index} is {len(text)} chars; keep bullets under "
                f"{MAX_BULLET_CHARS} or move detail to speaker notes"
            )
    if len(bullets) > MAX_BULLETS_PER_SLIDE:
        warnings.append(
            f"{where}: {len(bullets)} bullets on one slide; split the slide (max {MAX_BULLETS_PER_SLIDE})"
        )


def _check_column(column: Any, where: str, errors: list[str], warnings: list[str]) -> None:
    if not isinstance(column, dict):
        errors.append(f"{where}: must be an object with 'heading', 'text' and/or 'bullets'")
        return
    has_content = _is_str(column.get("text")) or isinstance(column.get("bullets"), list)
    if not has_content:
        errors.append(f"{where}: needs 'text' or 'bullets'")
    if column.get("bullets") is not None:
        _check_bullets(column.get("bullets"), where, errors, warnings)


def _resolve_asset(path_value: str, base_dir: Path) -> Path | None:
    candidate = Path(path_value).expanduser()
    options = [candidate] if candidate.is_absolute() else [Path.cwd() / candidate, base_dir / candidate]
    for option in options:
        if option.is_file():
            return option
    return None


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_spec(spec: Any, base_dir: Path | None = None) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for a deck spec. Errors block the build."""

    base_dir = base_dir or Path.cwd()
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(spec, dict):
        return ["spec must be a JSON object"], warnings

    slides = spec.get("slides")
    if not isinstance(slides, list) or not slides:
        errors.append("'slides' must be a non-empty list")
        slides = []

    if not _is_str(spec.get("title")) and not any(
        isinstance(s, dict) and s.get("type") == "title" and _is_str(s.get("title")) for s in slides
    ):
        warnings.append("no deck 'title' and no title slide; the file name will fall back to 'deck'")

    theme = spec.get("theme")
    if theme is not None:
        if not isinstance(theme, dict):
            errors.append("'theme' must be an object")
        else:
            for key in ("primary", "accent", "text", "muted", "background", "light"):
                value = theme.get(key)
                if value is None:
                    continue
                if not isinstance(value, str) or not _HEX_RE.match(value.lstrip("#")):
                    warnings.append(f"theme.{key} is not a 6-digit hex colour; using the default")

    for index, slide in enumerate(slides):
        where = f"slides[{index}]"
        if not isinstance(slide, dict):
            errors.append(f"{where}: must be an object")
            continue
        slide_type = slide.get("type")
        if slide_type not in SLIDE_TYPES:
            errors.append(f"{where}: unknown type {slide_type!r}; expected one of {sorted(SLIDE_TYPES)}")
            continue
        title = slide.get("title")
        if slide_type not in {"title", "quote", "closing"} and not _is_str(title):
            errors.append(f"{where}: '{slide_type}' slide needs a non-empty 'title'")
        if _is_str(title) and len(title) > MAX_TITLE_CHARS:
            warnings.append(f"{where}: title is {len(title)} chars; keep titles under {MAX_TITLE_CHARS}")
        notes = slide.get("notes")
        if notes is not None and not isinstance(notes, str):
            errors.append(f"{where}: 'notes' must be a string")

        if slide_type == "bullets":
            _check_bullets(slide.get("bullets"), where, errors, warnings)
        elif slide_type == "two_column":
            _check_column(slide.get("left"), f"{where}.left", errors, warnings)
            _check_column(slide.get("right"), f"{where}.right", errors, warnings)
        elif slide_type == "image":
            image = slide.get("image")
            if not _is_str(image):
                errors.append(f"{where}: 'image' path is required")
            elif _resolve_asset(image, base_dir) is None:
                errors.append(f"{where}: image not found: {image}")
        elif slide_type == "table":
            headers = slide.get("headers")
            rows = slide.get("rows")
            if not isinstance(headers, list) or not headers:
                errors.append(f"{where}: 'headers' must be a non-empty list")
            if not isinstance(rows, list) or not rows:
                errors.append(f"{where}: 'rows' must be a non-empty list of lists")
            elif isinstance(headers, list) and headers:
                for row_index, row in enumerate(rows):
                    if not isinstance(row, list):
                        errors.append(f"{where}: rows[{row_index}] must be a list")
                    elif len(row) != len(headers):
                        warnings.append(
                            f"{where}: rows[{row_index}] has {len(row)} cells but there are {len(headers)} headers"
                        )
                if len(rows) > MAX_TABLE_ROWS:
                    warnings.append(
                        f"{where}: {len(rows)} rows; split the table across slides (max {MAX_TABLE_ROWS})"
                    )
                if len(headers) > MAX_TABLE_COLS:
                    warnings.append(f"{where}: {len(headers)} columns will be hard to read (max {MAX_TABLE_COLS})")
        elif slide_type == "chart":
            chart = slide.get("chart")
            if not isinstance(chart, dict):
                errors.append(f"{where}: 'chart' must be an object")
            else:
                kind = chart.get("kind", "column")
                if kind not in CHART_KINDS:
                    errors.append(f"{where}: chart.kind must be one of {sorted(CHART_KINDS)}")
                categories = chart.get("categories")
                series = chart.get("series")
                if not isinstance(categories, list) or not categories:
                    errors.append(f"{where}: chart.categories must be a non-empty list")
                if not isinstance(series, list) or not series:
                    errors.append(f"{where}: chart.series must be a non-empty list")
                else:
                    for series_index, item in enumerate(series):
                        if not isinstance(item, dict) or not isinstance(item.get("values"), list):
                            errors.append(f"{where}: chart.series[{series_index}] needs a 'values' list")
                            continue
                        values = item["values"]
                        if isinstance(categories, list) and len(values) != len(categories):
                            errors.append(
                                f"{where}: chart.series[{series_index}] has {len(values)} values "
                                f"for {len(categories)} categories"
                            )
                        if not all(_is_number(v) for v in values):
                            errors.append(f"{where}: chart.series[{series_index}] values must be numbers")
                    if kind in {"pie", "doughnut"} and len(series) > 1:
                        warnings.append(f"{where}: pie charts show only the first series")
        elif slide_type == "kpi":
            metrics = slide.get("metrics")
            if not isinstance(metrics, list) or not metrics:
                errors.append(f"{where}: 'metrics' must be a non-empty list of {{'value', 'label'}}")
            else:
                for metric_index, metric in enumerate(metrics):
                    valid = (
                        isinstance(metric, dict)
                        and _is_str(str(metric.get("value", "")))
                        and _is_str(metric.get("label"))
                    )
                    if not valid:
                        errors.append(f"{where}: metrics[{metric_index}] needs 'value' and 'label'")
                if len(metrics) > MAX_KPI_METRICS:
                    errors.append(f"{where}: at most {MAX_KPI_METRICS} metrics per slide")
        elif slide_type == "quote":
            if not _is_str(slide.get("quote")):
                errors.append(f"{where}: 'quote' text is required")

    if len(slides) > 40:
        warnings.append(f"{len(slides)} slides; consider trimming or splitting into an appendix")
    return errors, warnings


# --------------------------------------------------------------------------- #
# Output path and theme helpers
# --------------------------------------------------------------------------- #


def _slug(value: str) -> str:
    text = re.sub(r"[^\w\-]+", "-", str(value or "").strip(), flags=re.UNICODE).strip("-_")
    text = re.sub(r"-{2,}", "-", text)
    return text[:80] or "deck"


def resolve_output_path(spec: dict[str, Any], output_arg: str | None) -> Path:
    raw = output_arg or spec.get("output") or f"output/{_slug(spec.get('title', ''))}.pptx"
    path = Path(str(raw)).expanduser()
    if path.suffix.lower() != ".pptx":
        path = path.with_suffix(".pptx")
    return path


def resolve_theme(spec: dict[str, Any]) -> dict[str, str]:
    theme = dict(DEFAULT_THEME)
    raw = spec.get("theme") if isinstance(spec.get("theme"), dict) else {}
    for key, value in raw.items():
        if key not in DEFAULT_THEME or not isinstance(value, str) or not value.strip():
            continue
        if key in FONT_KEYS:
            theme[key] = value.strip()
            continue
        cleaned = value.strip().lstrip("#").upper()
        if _HEX_RE.match(cleaned):
            theme[key] = cleaned
    if not theme["title_font"]:
        theme["title_font"] = theme["font"]
    return theme


# --------------------------------------------------------------------------- #
# Rendering (python-pptx)
# --------------------------------------------------------------------------- #


class DeckBuilder:
    """Draws every slide on a blank layout so the look does not depend on the template."""

    def __init__(self, spec: dict[str, Any], *, template: Path | None, base_dir: Path):
        from pptx import Presentation
        from pptx.util import Inches

        self.spec = spec
        self.base_dir = base_dir
        self.theme = resolve_theme(spec)
        self.warnings: list[str] = []
        if template is not None:
            self.prs = Presentation(str(template))
            self._drop_existing_slides()
        else:
            self.prs = Presentation()
            self.prs.slide_width = Inches(13.333)
            self.prs.slide_height = Inches(7.5)
        self.W = self.prs.slide_width
        self.H = self.prs.slide_height
        self.margin = int(self.W * 0.045)
        self.content_w = self.W - 2 * self.margin
        self.body_top = int(self.H * 0.21)
        self.body_h = int(self.H * 0.68)
        self.footer_text = str(spec.get("footer") or "").strip()
        self.blank_layout = self._pick_blank_layout()
        self.slide_index = 0

    # -- helpers ---------------------------------------------------------- #

    def _drop_existing_slides(self) -> None:
        sld_id_lst = self.prs.slides._sldIdLst
        for sld_id in list(sld_id_lst):
            self.prs.part.drop_rel(sld_id.rId)
            sld_id_lst.remove(sld_id)

    def _pick_blank_layout(self):
        layouts = list(self.prs.slide_layouts)
        for layout in layouts:
            if str(layout.name or "").strip().lower() == "blank":
                return layout
        return min(layouts, key=lambda layout: len(layout.placeholders))

    def _rgb(self, key: str):
        from pptx.dml.color import RGBColor

        return RGBColor.from_string(self.theme[key])

    def _palette(self, index: int):
        from pptx.dml.color import RGBColor

        colors = [self.theme["primary"], self.theme["accent"]]
        colors += [c for c in SERIES_PALETTE if c not in colors]
        return RGBColor.from_string(colors[index % len(colors)])

    def _new_slide(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        self.slide_index += 1
        return slide

    def _rect(self, slide, left, top, width, height, color_key: str, *, rounded: bool = False):
        from pptx.enum.shapes import MSO_SHAPE

        shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
        shape = slide.shapes.add_shape(shape_type, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = self._rgb(color_key)
        shape.line.fill.background()
        shape.shadow.inherit = False
        if rounded:
            shape.adjustments[0] = 0.08
        return shape

    def _style_run(
        self,
        run,
        *,
        size: int,
        bold: bool = False,
        italic: bool = False,
        color_key: str = "text",
        title: bool = False,
    ) -> None:
        from pptx.oxml.ns import qn
        from pptx.util import Pt

        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.italic = italic
        run.font.color.rgb = self._rgb(color_key)
        run.font.name = self.theme["title_font"] if title else self.theme["font"]
        east_asian = self.theme.get("east_asian_font")
        if east_asian:
            rPr = run._r.get_or_add_rPr()
            for existing in rPr.findall(qn("a:ea")):
                rPr.remove(existing)
            ea = rPr.makeelement(qn("a:ea"), {"typeface": east_asian})
            rPr.insert_element_before(
                ea, "a:cs", "a:sym", "a:hlinkClick", "a:hlinkMouseOver", "a:rtl", "a:extLst"
            )

    def _textbox(self, slide, left, top, width, height, *, anchor: str = "top"):
        from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE
        from pptx.util import Inches

        box = slide.shapes.add_textbox(left, top, width, height)
        frame = box.text_frame
        frame.word_wrap = True
        frame.auto_size = MSO_AUTO_SIZE.NONE
        anchors = {"top": MSO_ANCHOR.TOP, "middle": MSO_ANCHOR.MIDDLE, "bottom": MSO_ANCHOR.BOTTOM}
        frame.vertical_anchor = anchors[anchor]
        frame.margin_left = frame.margin_right = Inches(0.08)
        frame.margin_top = frame.margin_bottom = Inches(0.04)
        return frame

    def _write(
        self,
        frame,
        text: str,
        *,
        size: int,
        bold: bool = False,
        italic: bool = False,
        color_key: str = "text",
        align: str = "left",
        title: bool = False,
        first: bool = True,
    ):
        from pptx.enum.text import PP_ALIGN

        paragraph = frame.paragraphs[0] if first else frame.add_paragraph()
        paragraph.alignment = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}[align]
        run = paragraph.add_run()
        run.text = text
        self._style_run(run, size=size, bold=bold, italic=italic, color_key=color_key, title=title)
        return paragraph

    def _bullet_paragraph(self, frame, text: str, level: int, *, size: int, first: bool):
        from pptx.oxml.ns import qn
        from pptx.util import Inches, Pt

        paragraph = frame.paragraphs[0] if first else frame.add_paragraph()
        paragraph.space_before = Pt(4 if level == 0 else 1)
        paragraph.space_after = Pt(2)
        run = paragraph.add_run()
        run.text = text
        self._style_run(run, size=max(size - 2 * level, 10), color_key="text")
        pPr = paragraph._p.get_or_add_pPr()
        pPr.set("marL", str(int(Inches(0.32 + 0.38 * level))))
        pPr.set("indent", str(int(-Inches(0.28))))
        bu_clr = pPr.makeelement(qn("a:buClr"), {})
        bu_clr.append(
            bu_clr.makeelement(qn("a:srgbClr"), {"val": self.theme["accent" if level == 0 else "muted"]})
        )
        pPr.insert_element_before(
            bu_clr,
            "a:buSzTx", "a:buSzPct", "a:buSzPts", "a:buFontTx", "a:buFont",
            "a:buNone", "a:buAutoNum", "a:buChar", "a:buBlip", "a:tabLst", "a:defRPr", "a:extLst",
        )
        bullet_char = "•" if level == 0 else ("–" if level == 1 else "·")
        bu_char = pPr.makeelement(qn("a:buChar"), {"char": bullet_char})
        pPr.insert_element_before(bu_char, "a:buBlip", "a:tabLst", "a:defRPr", "a:extLst")
        return paragraph

    def _bullets(self, frame, bullets: list[Any], *, base_size: int, first: bool = True) -> None:
        total_chars = sum(len(_bullet_text(item)) for item in bullets)
        size = base_size
        if len(bullets) > 6 or total_chars > 450:
            size = base_size - 2
        if len(bullets) > 8 or total_chars > 700:
            size = base_size - 4
        for index, item in enumerate(bullets):
            level = item.get("level", 0) if isinstance(item, dict) else 0
            self._bullet_paragraph(frame, _bullet_text(item), int(level), size=size, first=first and index == 0)

    def _title_bar(self, slide, title: str) -> None:
        from pptx.util import Inches

        frame = self._textbox(
            slide, self.margin, int(self.H * 0.06), self.content_w, int(self.H * 0.12), anchor="bottom"
        )
        self._write(frame, title, size=30 if len(title) <= 45 else 26, bold=True, color_key="primary", title=True)
        self._rect(slide, self.margin, int(self.H * 0.185), Inches(1.1), Inches(0.05), "accent")

    def _footer(self, slide) -> None:
        from pptx.util import Inches

        top = self.H - int(self.H * 0.075)
        if self.footer_text:
            frame = self._textbox(slide, self.margin, top, int(self.content_w * 0.7), Inches(0.35), anchor="middle")
            self._write(frame, self.footer_text, size=10, color_key="muted")
        frame = self._textbox(
            slide, self.W - self.margin - Inches(1.2), top, Inches(1.2), Inches(0.35), anchor="middle"
        )
        self._write(frame, str(self.slide_index), size=10, color_key="muted", align="right")

    def _notes(self, slide, notes: Any) -> None:
        if isinstance(notes, str) and notes.strip():
            slide.notes_slide.notes_text_frame.text = notes.strip()

    def _content_slide(self, spec_slide: dict[str, Any]):
        slide = self._new_slide()
        self._title_bar(slide, str(spec_slide["title"]))
        self._footer(slide)
        self._notes(slide, spec_slide.get("notes"))
        return slide

    # -- slide types ------------------------------------------------------ #

    def add_title(self, spec_slide: dict[str, Any], *, closing: bool = False) -> None:
        from pptx.util import Inches

        slide = self._new_slide()
        self._rect(slide, 0, 0, self.W, self.H, "primary")
        self._rect(slide, self.margin, int(self.H * 0.58), Inches(1.6), Inches(0.08), "accent")
        default_title = "Thank you" if closing else (self.spec.get("title") or "Untitled")
        title = str(spec_slide.get("title") or default_title)
        frame = self._textbox(
            slide, self.margin, int(self.H * 0.22), self.content_w, int(self.H * 0.34), anchor="bottom"
        )
        self._write(frame, title, size=44 if len(title) <= 40 else 36, bold=True, color_key="background", title=True)
        default_subtitle = "" if closing else (self.spec.get("subtitle") or "")
        subtitle = str(spec_slide.get("subtitle") or default_subtitle).strip()
        if subtitle:
            frame = self._textbox(slide, self.margin, int(self.H * 0.61), self.content_w, int(self.H * 0.16))
            self._write(frame, subtitle, size=20, color_key="light")
        meta_parts = [str(v).strip() for v in (self.spec.get("author"), self.spec.get("date")) if v and str(v).strip()]
        if meta_parts and not closing:
            frame = self._textbox(slide, self.margin, int(self.H * 0.84), self.content_w, Inches(0.5))
            self._write(frame, " · ".join(meta_parts), size=14, color_key="light")
        self._notes(slide, spec_slide.get("notes"))

    def add_section(self, spec_slide: dict[str, Any]) -> None:
        from pptx.util import Inches

        slide = self._new_slide()
        self._rect(slide, 0, 0, Inches(0.45), self.H, "accent")
        left = self.margin + Inches(0.3)
        width = self.content_w - Inches(0.3)
        frame = self._textbox(slide, left, int(self.H * 0.3), width, int(self.H * 0.25), anchor="bottom")
        self._write(frame, str(spec_slide["title"]), size=40, bold=True, color_key="primary", title=True)
        subtitle = str(spec_slide.get("subtitle") or "").strip()
        if subtitle:
            frame = self._textbox(slide, left, int(self.H * 0.56), width, int(self.H * 0.2))
            self._write(frame, subtitle, size=20, color_key="muted")
        self._footer(slide)
        self._notes(slide, spec_slide.get("notes"))

    def add_bullets(self, spec_slide: dict[str, Any]) -> None:
        slide = self._content_slide(spec_slide)
        frame = self._textbox(slide, self.margin, self.body_top, self.content_w, self.body_h)
        self._bullets(frame, list(spec_slide["bullets"]), base_size=22)

    def add_two_column(self, spec_slide: dict[str, Any]) -> None:
        from pptx.util import Inches

        slide = self._content_slide(spec_slide)
        gap = Inches(0.5)
        col_w = int((self.content_w - gap) / 2)
        for index, key in enumerate(("left", "right")):
            column = spec_slide[key]
            left = self.margin + index * (col_w + gap)
            top = self.body_top
            heading = str(column.get("heading") or "").strip()
            if heading:
                frame = self._textbox(slide, left, top, col_w, Inches(0.6))
                self._write(frame, heading, size=20, bold=True, color_key="primary")
                top += Inches(0.65)
            frame = self._textbox(slide, left, top, col_w, self.body_h - (top - self.body_top))
            text = str(column.get("text") or "").strip()
            bullets = column.get("bullets")
            if text:
                self._write(frame, text, size=18)
            if isinstance(bullets, list) and bullets:
                if text:
                    frame.add_paragraph()
                self._bullets(frame, bullets, base_size=20 if not text else 18, first=not text)

    def add_image(self, spec_slide: dict[str, Any]) -> None:
        from pptx.util import Inches

        slide = self._content_slide(spec_slide)
        path = _resolve_asset(str(spec_slide["image"]), self.base_dir)
        caption = str(spec_slide.get("caption") or "").strip()
        box_h = self.body_h - (Inches(0.5) if caption else 0)
        picture = slide.shapes.add_picture(str(path), self.margin, self.body_top)
        scale = min(self.content_w / picture.width, box_h / picture.height)
        picture.width = int(picture.width * scale)
        picture.height = int(picture.height * scale)
        picture.left = int(self.margin + (self.content_w - picture.width) / 2)
        picture.top = int(self.body_top + (box_h - picture.height) / 2)
        if caption:
            frame = self._textbox(
                slide, self.margin, self.body_top + box_h, self.content_w, Inches(0.5), anchor="middle"
            )
            self._write(frame, caption, size=12, italic=True, color_key="muted", align="center")

    def add_table(self, spec_slide: dict[str, Any]) -> None:
        from pptx.util import Pt

        slide = self._content_slide(spec_slide)
        headers = [str(h) for h in spec_slide["headers"]]
        rows = [
            [str(cell) for cell in row][: len(headers)] + [""] * max(0, len(headers) - len(row))
            for row in spec_slide["rows"]
        ]
        row_count = len(rows) + 1
        size = 14 if row_count <= 7 else (12 if row_count <= 11 else 10)
        row_h = Pt(size * 2.2)
        height = min(self.body_h, int(row_h * row_count))
        frame = slide.shapes.add_table(row_count, len(headers), self.margin, self.body_top, self.content_w, height)
        table = frame.table
        col_w = int(self.content_w / len(headers))
        for column in table.columns:
            column.width = col_w
        for col_index, header in enumerate(headers):
            self._table_cell(
                table.cell(0, col_index), header, size=size, bold=True, color_key="background", fill_key="primary"
            )
        for row_index, row in enumerate(rows, start=1):
            fill_key = "light" if row_index % 2 == 0 else "background"
            for col_index in range(len(headers)):
                self._table_cell(table.cell(row_index, col_index), row[col_index], size=size, fill_key=fill_key)

    def _table_cell(
        self,
        cell,
        text: str,
        *,
        size: int,
        bold: bool = False,
        color_key: str = "text",
        fill_key: str = "background",
    ) -> None:
        from pptx.enum.text import MSO_ANCHOR
        from pptx.util import Inches

        cell.fill.solid()
        cell.fill.fore_color.rgb = self._rgb(fill_key)
        cell.margin_left = cell.margin_right = Inches(0.08)
        cell.margin_top = cell.margin_bottom = Inches(0.04)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        frame = cell.text_frame
        frame.word_wrap = True
        paragraph = frame.paragraphs[0]
        run = paragraph.add_run()
        run.text = text
        self._style_run(run, size=size, bold=bold, color_key=color_key)

    def add_chart(self, spec_slide: dict[str, Any]) -> None:
        from pptx.chart.data import CategoryChartData
        from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION
        from pptx.util import Pt

        slide = self._content_slide(spec_slide)
        chart_spec = spec_slide["chart"]
        kind = str(chart_spec.get("kind", "column"))
        chart_type = {
            "bar": XL_CHART_TYPE.BAR_CLUSTERED,
            "column": XL_CHART_TYPE.COLUMN_CLUSTERED,
            "line": XL_CHART_TYPE.LINE_MARKERS,
            "pie": XL_CHART_TYPE.PIE,
            "doughnut": XL_CHART_TYPE.DOUGHNUT,
        }[kind]
        data = CategoryChartData()
        data.categories = [str(c) for c in chart_spec["categories"]]
        is_pie = kind in {"pie", "doughnut"}
        series_specs = chart_spec["series"][:1] if is_pie else chart_spec["series"]
        for index, item in enumerate(series_specs):
            data.add_series(str(item.get("name") or f"Series {index + 1}"), [float(v) for v in item["values"]])
        graphic_frame = slide.shapes.add_chart(
            chart_type, self.margin, self.body_top, self.content_w, self.body_h, data
        )
        chart = graphic_frame.chart
        chart.font.size = Pt(12)
        chart.font.name = self.theme["font"]
        chart.font.color.rgb = self._rgb("text")
        chart.has_legend = is_pie or len(series_specs) > 1
        if chart.has_legend:
            chart.legend.position = XL_LEGEND_POSITION.BOTTOM
            chart.legend.include_in_layout = False
        plot = chart.plots[0]
        if is_pie:
            plot.has_data_labels = True
            labels = plot.data_labels
            labels.show_percentage = True
            labels.show_value = False
            labels.number_format = "0%"
            labels.number_format_is_linked = False
            if kind == "pie":
                labels.position = XL_LABEL_POSITION.OUTSIDE_END
            for index, point in enumerate(plot.series[0].points):
                point.format.fill.solid()
                point.format.fill.fore_color.rgb = self._palette(index)
        else:
            plot.has_data_labels = bool(chart_spec.get("data_labels", False))
            for index, series in enumerate(plot.series):
                if kind == "line":
                    series.format.line.color.rgb = self._palette(index)
                    series.format.line.width = Pt(2.5)
                    series.smooth = False
                else:
                    series.format.fill.solid()
                    series.format.fill.fore_color.rgb = self._palette(index)
            if kind != "line":
                plot.gap_width = 80
        chart_title = str(chart_spec.get("title") or "").strip()
        chart.has_title = bool(chart_title)
        if chart_title:
            chart.chart_title.text_frame.text = chart_title
            for paragraph in chart.chart_title.text_frame.paragraphs:
                for run in paragraph.runs:
                    self._style_run(run, size=14, bold=True, color_key="primary")

    def add_kpi(self, spec_slide: dict[str, Any]) -> None:
        from pptx.util import Inches

        slide = self._content_slide(spec_slide)
        metrics = list(spec_slide["metrics"])
        per_row = 3 if len(metrics) > 4 else len(metrics)
        rows = [metrics[i:i + per_row] for i in range(0, len(metrics), per_row)]
        gap = Inches(0.4)
        row_h = int((self.body_h - gap * (len(rows) - 1)) / len(rows))
        value_size = 40 if len(rows) == 1 else 32
        for row_index, row in enumerate(rows):
            card_w = int((self.content_w - gap * (len(row) - 1)) / len(row))
            top = self.body_top + row_index * (row_h + gap)
            for col_index, metric in enumerate(row):
                left = self.margin + col_index * (card_w + gap)
                self._rect(slide, left, top, card_w, row_h, "light", rounded=True)
                value_frame = self._textbox(
                    slide, left, top + int(row_h * 0.12), card_w, int(row_h * 0.45), anchor="middle"
                )
                self._write(
                    value_frame, str(metric["value"]), size=value_size, bold=True,
                    color_key="primary", align="center", title=True,
                )
                label_frame = self._textbox(
                    slide, left + Inches(0.2), top + int(row_h * 0.58), card_w - Inches(0.4), int(row_h * 0.38)
                )
                self._write(label_frame, str(metric["label"]), size=16, color_key="text", align="center")
                description = str(metric.get("description") or "").strip()
                if description:
                    self._write(label_frame, description, size=12, color_key="muted", align="center", first=False)

    def add_quote(self, spec_slide: dict[str, Any]) -> None:
        from pptx.util import Inches

        slide = self._new_slide()
        self._rect(slide, self.margin, int(self.H * 0.25), Inches(0.12), int(self.H * 0.42), "accent")
        left = self.margin + Inches(0.5)
        width = self.content_w - Inches(0.5)
        frame = self._textbox(slide, left, int(self.H * 0.22), width, int(self.H * 0.48), anchor="middle")
        quote = str(spec_slide["quote"]).strip()
        self._write(
            frame, f"“{quote}”", size=30 if len(quote) <= 140 else 24,
            italic=True, color_key="primary", title=True,
        )
        attribution = str(spec_slide.get("attribution") or "").strip()
        if attribution:
            frame = self._textbox(slide, left, int(self.H * 0.72), width, Inches(0.6))
            self._write(frame, f"— {attribution}", size=16, color_key="muted")
        self._footer(slide)
        self._notes(slide, spec_slide.get("notes"))

    # -- driver ------------------------------------------------------------ #

    def build(self) -> None:
        handlers = {
            "title": self.add_title,
            "section": self.add_section,
            "bullets": self.add_bullets,
            "two_column": self.add_two_column,
            "image": self.add_image,
            "table": self.add_table,
            "chart": self.add_chart,
            "kpi": self.add_kpi,
            "quote": self.add_quote,
            "closing": lambda spec_slide: self.add_title(spec_slide, closing=True),
        }
        slides = list(self.spec["slides"])
        if slides[0].get("type") != "title":
            self.add_title({"title": self.spec.get("title"), "subtitle": self.spec.get("subtitle")})
        for spec_slide in slides:
            handlers[str(spec_slide["type"])](spec_slide)
        core = self.prs.core_properties
        core.title = str(self.spec.get("title") or "")
        if self.spec.get("author"):
            core.author = str(self.spec["author"])

    def save(self, output: Path) -> None:
        output.parent.mkdir(parents=True, exist_ok=True)
        self.prs.save(str(output))


def build_deck(
    spec: dict[str, Any],
    output: Path,
    *,
    template: Path | None = None,
    base_dir: Path | None = None,
) -> dict[str, Any]:
    """Validate, render and save a deck. Returns the JSON-able summary."""

    base_dir = base_dir or Path.cwd()
    errors, warnings = validate_spec(spec, base_dir)
    if errors:
        return {"ok": False, "errors": errors, "warnings": warnings}
    builder = DeckBuilder(spec, template=template, base_dir=base_dir)
    builder.build()
    builder.save(output)
    from pptx import Presentation

    verified = len(Presentation(str(output)).slides)
    return {
        "ok": True,
        "output": str(output),
        "slides": verified,
        "bytes": output.stat().st_size,
        "warnings": warnings + builder.warnings,
    }


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def example_spec() -> dict[str, Any]:
    example_path = Path(__file__).resolve().parent.parent / "references" / "spec-example.json"
    if example_path.is_file():
        return json.loads(example_path.read_text(encoding="utf-8"))
    return {
        "title": "Example deck",
        "subtitle": "Generated with build_deck.py",
        "author": "EFP",
        "date": date.today().isoformat(),
        "slides": [
            {"type": "bullets", "title": "Agenda", "bullets": ["Context", "Findings", "Next steps"]},
            {"type": "closing", "title": "Thank you"},
        ],
    }


def _emit(payload: dict[str, Any], *, quiet: bool) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=None if quiet else 2))


def _utf8_stdout() -> None:
    """Deck text is often non-ASCII; do not let a legacy console encoding crash the summary."""
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):
            pass


def main(argv: list[str] | None = None) -> int:
    _utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("spec", nargs="?", help="Path to the JSON deck spec")
    parser.add_argument("--output", help="Where to write the .pptx (default: spec.output or output/<title>.pptx)")
    parser.add_argument(
        "--template", help="Existing .pptx/.potx whose theme and slide size to reuse; its own slides are removed"
    )
    parser.add_argument("--validate-only", action="store_true", help="Check the spec and exit without building")
    parser.add_argument("--print-example", action="store_true", help="Print the example spec and exit")
    parser.add_argument("--quiet", action="store_true", help="Single-line JSON output")
    args = parser.parse_args(argv)

    if args.print_example:
        print(json.dumps(example_spec(), ensure_ascii=False, indent=2))
        return 0
    if not args.spec:
        parser.error("spec path is required unless --print-example is given")

    spec_path = Path(args.spec).expanduser()
    if not spec_path.is_file():
        _emit({"ok": False, "errors": [f"spec not found: {spec_path}"]}, quiet=args.quiet)
        return 2
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        _emit({"ok": False, "errors": [f"spec is not valid JSON: {exc}"]}, quiet=args.quiet)
        return 2

    base_dir = spec_path.resolve().parent
    errors, warnings = validate_spec(spec, base_dir)
    if errors:
        _emit({"ok": False, "errors": errors, "warnings": warnings}, quiet=args.quiet)
        return 2
    if args.validate_only:
        _emit(
            {"ok": True, "validated": True, "slides": len(spec["slides"]), "warnings": warnings},
            quiet=args.quiet,
        )
        return 0

    try:
        import pptx  # noqa: F401
    except ImportError:
        _emit(
            {
                "ok": False,
                "errors": [
                    "python-pptx is not installed in this runtime. Try `python -m pip install --user python-pptx`; "
                    "if that fails the runtime image needs python-pptx added to requirements.txt."
                ],
            },
            quiet=args.quiet,
        )
        return 3

    template = None
    if args.template:
        template = Path(args.template).expanduser()
        if not template.is_file():
            _emit({"ok": False, "errors": [f"template not found: {template}"]}, quiet=args.quiet)
            return 4

    output = resolve_output_path(spec, args.output)
    try:
        summary = build_deck(spec, output, template=template, base_dir=base_dir)
    except Exception as exc:  # surface the failure as JSON so the agent can act on it
        _emit({"ok": False, "errors": [f"{exc.__class__.__name__}: {exc}"]}, quiet=args.quiet)
        return 1
    _emit(summary, quiet=args.quiet)
    return 0 if summary.get("ok") else 2


if __name__ == "__main__":
    sys.exit(main())
