#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

IGNORE_DIRS = {".git", ".github", "scripts", "__pycache__"}
REQUIRED_KEYS = {"name", "description", "version", "owner"}


def parse_frontmatter(content: str) -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    if not content.startswith("---\n") and content != "---":
        return {}, ["frontmatter must start with ---"]

    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, ["frontmatter opening delimiter not found"]

    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return {}, ["frontmatter closing delimiter not found"]

    fm_lines = lines[1:end_idx]
    data: dict[str, object] = {}
    i = 0
    while i < len(fm_lines):
        line = fm_lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue

        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*)$", line)
        if not m:
            i += 1
            continue

        key = m.group(1)
        value = m.group(2).strip()
        if value:
            data[key] = value.strip('"\'')
            i += 1
            continue

        items: list[str] = []
        i += 1
        while i < len(fm_lines):
            item_line = fm_lines[i]
            sm = re.match(r"^\s*-\s*(.+?)\s*$", item_line)
            if sm:
                items.append(sm.group(1).strip().strip('"\''))
                i += 1
                continue
            break
        data[key] = items

    return data, errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors: list[str] = []
    skill_dirs = []
    names: dict[str, Path] = {}

    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        if child.name in IGNORE_DIRS or child.name.startswith('.'):
            continue

        skill_md = child / "skill.md"
        skill_py = child / "skill.py"
        if not (skill_md.exists() or skill_py.exists()):
            continue

        skill_dirs.append(child)
        if not skill_md.exists():
            errors.append(f"{child.name}: missing skill.md")
            continue

        content = skill_md.read_text(encoding="utf-8")
        data, fm_errors = parse_frontmatter(content)
        for msg in fm_errors:
            errors.append(f"{child.name}/skill.md: {msg}")
        if fm_errors:
            continue

        for key in REQUIRED_KEYS:
            if not str(data.get(key, "")).strip():
                errors.append(f"{child.name}/skill.md: missing or empty '{key}'")

        trigger_val = data.get("triggers", data.get("trigger"))
        if isinstance(trigger_val, list):
            if not [x for x in trigger_val if str(x).strip()]:
                errors.append(f"{child.name}/skill.md: triggers/trigger must not be empty")
        elif not str(trigger_val or "").strip():
            errors.append(f"{child.name}/skill.md: missing or empty 'triggers'/'trigger'")

        name = str(data.get("name", "")).strip()
        if name:
            if name in names:
                errors.append(f"duplicate skill name '{name}' in {names[name].name} and {child.name}")
            else:
                names[name] = child

        refs = data.get("references")
        if isinstance(refs, list):
            for ref in refs:
                ref_path = child / str(ref)
                if not ref_path.exists():
                    errors.append(f"{child.name}/skill.md: reference not found: {ref}")

    total_skill_md = sum(1 for d in skill_dirs if (d / "skill.md").exists())
    total_python_backed = sum(1 for d in skill_dirs if (d / "skill.py").exists())

    print(f"total skill directories: {len(skill_dirs)}")
    print(f"total skill.md discovered: {total_skill_md}")
    print(f"python-backed skills count: {total_python_backed}")

    if errors:
        print("\nValidation errors:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("\nValidation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
