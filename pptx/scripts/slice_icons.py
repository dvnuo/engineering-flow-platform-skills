#!/usr/bin/env python3
"""Cut an icon sheet (many icons in one PNG) into single PNG files.

Usage:
    python slice_icons.py SHEET.png --out DIR [--grid ROWSxCOLS] [--names a,b,c | --names-file FILE]
                          [--size 256] [--pad 0.12] [--min-gap 4] [--quiet]

Without ``--grid`` the cells are found from the empty gutters between icons,
which works for the usual evenly spaced sheets. Each icon is written as
``DIR/<name>.png`` (square, transparent, ``size`` px), plus ``DIR/icons.json``
(index, row, col, name, file, bbox on the sheet) and ``DIR/contact-sheet.png``,
a numbered overview a person or the agent uses to name the icons.

Exit codes: 0 ok, 2 bad input, 3 Pillow missing.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ALPHA_THRESHOLD = 16
COLOR_THRESHOLD = 40
MIN_BAND_PX = 3


def ink_mask(image):
    """1-bit mask of the icon pixels: alpha where the sheet has transparency, colour distance otherwise."""
    from PIL import Image, ImageChops

    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    if alpha.getextrema()[0] < 255:
        return alpha.point(lambda a: 255 if a > ALPHA_THRESHOLD else 0).convert("1")
    rgb = rgba.convert("RGB")
    width, height = rgb.size
    corners = [rgb.getpixel((0, 0)), rgb.getpixel((width - 1, 0)), rgb.getpixel((0, height - 1)), rgb.getpixel((width - 1, height - 1))]
    background = max(set(corners), key=corners.count)
    diff = ImageChops.difference(rgb, Image.new("RGB", rgb.size, background)).convert("L")
    return diff.point(lambda v: 255 if v > COLOR_THRESHOLD else 0).convert("1")


def _profile(mask, axis: str) -> list[bool]:
    width, height = mask.size
    if axis == "rows":
        return [mask.crop((0, y, width, y + 1)).getbbox() is not None for y in range(height)]
    return [mask.crop((x, 0, x + 1, height)).getbbox() is not None for x in range(width)]


def bands(profile: list[bool], *, min_gap: int) -> list[tuple[int, int]]:
    """Runs of ink (start, end) in a profile, merging runs split by gaps shorter than min_gap."""
    runs: list[tuple[int, int]] = []
    start = None
    for index, ink in enumerate(profile + [False]):
        if ink and start is None:
            start = index
        elif not ink and start is not None:
            runs.append((start, index))
            start = None
    merged: list[tuple[int, int]] = []
    for run in runs:
        if merged and run[0] - merged[-1][1] < min_gap:
            merged[-1] = (merged[-1][0], run[1])
        else:
            merged.append(run)
    return [run for run in merged if run[1] - run[0] >= MIN_BAND_PX]


def detect_cells(mask, *, min_gap: int) -> tuple[list[tuple[int, int, int, int]], int, int]:
    """Cells (left, top, right, bottom) at every row band × column band that holds ink."""
    row_bands = bands(_profile(mask, "rows"), min_gap=min_gap)
    col_bands = bands(_profile(mask, "cols"), min_gap=min_gap)
    cells = []
    for top, bottom in row_bands:
        for left, right in col_bands:
            if mask.crop((left, top, right, bottom)).getbbox() is not None:
                cells.append((left, top, right, bottom))
    return cells, len(row_bands), len(col_bands)


def grid_cells(size: tuple[int, int], rows: int, cols: int) -> list[tuple[int, int, int, int]]:
    width, height = size
    cells = []
    for row in range(rows):
        for col in range(cols):
            cells.append((col * width // cols, row * height // rows, (col + 1) * width // cols, (row + 1) * height // rows))
    return cells


def parse_grid(value: str | None) -> tuple[int, int] | None:
    if not value:
        return None
    match = re.fullmatch(r"\s*(\d+)\s*[xX×]\s*(\d+)\s*", value)
    if not match or int(match.group(1)) < 1 or int(match.group(2)) < 1:
        raise ValueError("--grid must look like ROWSxCOLS, e.g. 4x6")
    return int(match.group(1)), int(match.group(2))


def slugify(name: str, fallback: str) -> str:
    text = re.sub(r"[^\w\-]+", "-", str(name or "").strip(), flags=re.UNICODE).strip("-_").lower()
    return text or fallback


def render_icon(sheet, mask, cell: tuple[int, int, int, int], *, size: int, pad: float):
    """Crop the ink inside a cell and centre it on a transparent square canvas."""
    from PIL import Image

    left, top, right, bottom = cell
    bbox = mask.crop(cell).getbbox()
    if bbox is None:
        return None, None
    region = (left + bbox[0], top + bbox[1], left + bbox[2], top + bbox[3])
    icon = sheet.convert("RGBA").crop(region)
    inner = max(1, int(size * (1 - 2 * pad)))
    scale = min(inner / icon.width, inner / icon.height)
    resized = icon.resize((max(1, int(icon.width * scale)), max(1, int(icon.height * scale))), Image.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.paste(resized, ((size - resized.width) // 2, (size - resized.height) // 2), resized)
    return canvas, region


def contact_sheet(entries: list[dict[str, Any]], out_dir: Path, *, thumb: int = 96, per_row: int = 6) -> Path:
    from PIL import Image, ImageDraw, ImageFont

    try:
        font = ImageFont.load_default(size=13)
    except TypeError:  # Pillow < 10.1
        font = ImageFont.load_default()
    rows = max(1, (len(entries) + per_row - 1) // per_row)
    cell_w, cell_h = thumb + 24, thumb + 40
    sheet = Image.new("RGBA", (per_row * cell_w + 12, rows * cell_h + 12), (255, 255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    for position, entry in enumerate(entries):
        x = 12 + (position % per_row) * cell_w
        y = 12 + (position // per_row) * cell_h
        icon = Image.open(out_dir / entry["file"]).convert("RGBA").resize((thumb, thumb), Image.LANCZOS)
        draw.rectangle((x - 2, y - 2, x + thumb + 2, y + thumb + 2), outline=(200, 200, 200, 255))
        sheet.paste(icon, (x, y), icon)
        draw.text((x, y + thumb + 6), f"{entry['index']} {entry['name']}"[:22], fill=(30, 30, 30, 255), font=font)
    path = out_dir / "contact-sheet.png"
    sheet.save(path, optimize=True)
    return path


def slice_sheet(
    sheet_path: Path,
    out_dir: Path,
    *,
    grid: tuple[int, int] | None = None,
    names: list[str] | None = None,
    size: int = 256,
    pad: float = 0.12,
    min_gap: int = 4,
) -> dict[str, Any]:
    from PIL import Image

    sheet = Image.open(sheet_path)
    mask = ink_mask(sheet)
    if grid:
        cells, rows, cols = grid_cells(sheet.size, *grid), grid[0], grid[1]
    else:
        cells, rows, cols = detect_cells(mask, min_gap=min_gap)
    if not cells:
        return {"ok": False, "errors": ["no icons found; is the sheet transparent or on a plain background?"]}
    out_dir.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, Any]] = []
    used: set[str] = set()
    for position, cell in enumerate(cells):
        icon, region = render_icon(sheet, mask, cell, size=size, pad=pad)
        if icon is None:
            continue
        index = len(entries) + 1
        requested = names[index - 1] if names and index - 1 < len(names) else ""
        name = slugify(requested, f"icon-{index:02d}")
        base = name
        suffix = 2
        while name in used:
            name = f"{base}-{suffix}"
            suffix += 1
        used.add(name)
        file_name = f"{name}.png"
        icon.save(out_dir / file_name, optimize=True)
        row = position // cols if grid else next(i for i, band in enumerate(bands(_profile(mask, "rows"), min_gap=min_gap)) if band[0] == cell[1])
        col = position % cols if grid else next(i for i, band in enumerate(bands(_profile(mask, "cols"), min_gap=min_gap)) if band[0] == cell[0])
        entries.append({"index": index, "row": row + 1, "col": col + 1, "name": name, "file": file_name, "bbox": list(region)})
    manifest = out_dir / "icons.json"
    manifest.write_text(json.dumps({"sheet": str(sheet_path), "size": size, "icons": entries}, ensure_ascii=False, indent=2), encoding="utf-8")
    contact = contact_sheet(entries, out_dir)
    return {
        "ok": True,
        "icons": len(entries),
        "rows": rows,
        "cols": cols,
        "out": str(out_dir),
        "manifest": str(manifest),
        "contact_sheet": str(contact),
        "names": [entry["name"] for entry in entries],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("sheet", help="PNG/JPEG with several icons")
    parser.add_argument("--out", required=True, help="Directory for the single icons")
    parser.add_argument("--grid", help="ROWSxCOLS when the icons sit on a regular grid, e.g. 4x6")
    parser.add_argument("--names", help="Comma-separated names in reading order (left to right, top to bottom)")
    parser.add_argument("--names-file", help="File with one name per line, same order as --names")
    parser.add_argument("--size", type=int, default=256, help="Output icon size in pixels (square)")
    parser.add_argument("--pad", type=float, default=0.12, help="Transparent padding as a fraction of the size")
    parser.add_argument("--min-gap", type=int, default=4, help="Gutter width in pixels that separates two icons")
    parser.add_argument("--quiet", action="store_true", help="Single-line JSON output")
    args = parser.parse_args(argv)

    sheet_path = Path(args.sheet).expanduser()
    if not sheet_path.is_file():
        print(json.dumps({"ok": False, "errors": [f"sheet not found: {sheet_path}"]}))
        return 2
    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        print(json.dumps({"ok": False, "errors": ["Pillow is not installed; run `python -m pip install --user Pillow`"]}))
        return 3
    try:
        grid = parse_grid(args.grid)
    except ValueError as exc:
        print(json.dumps({"ok": False, "errors": [str(exc)]}))
        return 2
    names: list[str] | None = None
    if args.names_file:
        names = [line.strip() for line in Path(args.names_file).read_text(encoding="utf-8").splitlines() if line.strip()]
    elif args.names:
        names = [part.strip() for part in args.names.split(",")]
    if args.size < 16 or not 0 <= args.pad < 0.5:
        print(json.dumps({"ok": False, "errors": ["--size must be at least 16 and --pad between 0 and 0.5"]}))
        return 2
    try:
        summary = slice_sheet(sheet_path, Path(args.out).expanduser(), grid=grid, names=names, size=args.size, pad=args.pad, min_gap=max(1, args.min_gap))
    except Exception as exc:
        print(json.dumps({"ok": False, "errors": [f"{exc.__class__.__name__}: {exc}"]}, ensure_ascii=False))
        return 2
    print(json.dumps(summary, ensure_ascii=False, indent=None if args.quiet else 2))
    return 0 if summary.get("ok") else 2


if __name__ == "__main__":
    sys.exit(main())
