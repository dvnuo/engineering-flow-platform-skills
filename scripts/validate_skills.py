#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

IGNORE_DIRS = {".git", ".github", "scripts", "__pycache__"}
REQUIRED_KEYS = {"name", "description", "version", "owner"}


def normalize_opencode_name(raw_name: str, fallback_seed: str) -> str:
    normalized = (raw_name or "").strip().lower()
    normalized = normalized.replace("_", "-").replace(" ", "-")
    normalized = re.sub(r"[^a-z0-9-]", "-", normalized)
    normalized = re.sub(r"-+", "-", normalized)
    normalized = normalized.strip("-")
    if normalized:
        return normalized

    digest = hashlib.sha256(fallback_seed.encode("utf-8")).hexdigest()[:12]
    return f"skill-{digest}"


def parse_frontmatter(content: str) -> tuple[dict[str, object], list[str]]:
    if not content.startswith("---"):
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

    frontmatter_text = "\n".join(lines[1:end_idx])

    if yaml is not None:
        try:
            loaded = yaml.safe_load(frontmatter_text)
        except yaml.YAMLError as exc:
            return {}, [f"invalid frontmatter yaml: {exc}"]
        if loaded is None:
            return {}, []
        if not isinstance(loaded, dict):
            return {}, ["frontmatter must parse to a mapping/object"]
        return loaded, []

    return parse_frontmatter_fallback(lines[1:end_idx])


def parse_frontmatter_fallback(fm_lines: list[str]) -> tuple[dict[str, object], list[str]]:
    data: dict[str, object] = {}
    i = 0
    while i < len(fm_lines):
        raw = fm_lines[i]
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*)$", raw)
        if not m:
            i += 1
            continue

        key = m.group(1)
        value = m.group(2)

        if value.strip() == "[]":
            data[key] = []
            i += 1
            continue

        if value.strip():
            cleaned = value.strip()
            if (
                (cleaned.startswith('"') and cleaned.endswith('"'))
                or (cleaned.startswith("'") and cleaned.endswith("'"))
            ) and len(cleaned) >= 2:
                cleaned = cleaned[1:-1]
            data[key] = cleaned
            i += 1
            continue

        i += 1
        list_items: list[str] = []
        while i < len(fm_lines):
            item_line = fm_lines[i]
            if not item_line.strip():
                i += 1
                continue
            sm = re.match(r"^\s*-\s*(.*?)\s*$", item_line)
            if not sm:
                break
            item = sm.group(1).strip()
            if (
                (item.startswith('"') and item.endswith('"'))
                or (item.startswith("'") and item.endswith("'"))
            ) and len(item) >= 2:
                item = item[1:-1]
            list_items.append(item)
            i += 1

        data[key] = list_items if list_items else ""

    return data, []


def discover_skill_files(root: Path, errors: list[str]) -> tuple[list[Path], list[Path]]:
    skill_dirs: list[Path] = []
    skill_files: list[Path] = []

    for child in sorted(root.iterdir()):
        if child.is_dir():
            if child.name in IGNORE_DIRS or child.name.startswith("."):
                continue
            skill_md = child / "skill.md"
            skill_py = child / "skill.py"
            if not (skill_md.exists() or skill_py.exists()):
                continue

            skill_dirs.append(child)
            if not skill_md.exists():
                errors.append(f"{child.name}: missing skill.md")
                continue
            skill_files.append(skill_md)
            continue

        if child.is_file() and child.suffix == ".md":
            content = child.read_text(encoding="utf-8")
            if content.startswith("---"):
                skill_files.append(child)

    return skill_dirs, skill_files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--opencode-compatible", action="store_true")
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parents[1]
    errors: list[str] = []

    nested_skills_dir = root / "skills"
    if nested_skills_dir.exists():
        errors.append(
            "nested skills/ directory is not allowed; repository root must be the skills root"
        )

    skill_dirs, skill_files = discover_skill_files(root, errors)
    names: dict[str, Path] = {}
    normalized_names: dict[str, Path] = {}

    for skill_md in skill_files:
        rel = skill_md.relative_to(root)
        content = skill_md.read_text(encoding="utf-8")
        data, fm_errors = parse_frontmatter(content)
        for msg in fm_errors:
            errors.append(f"{rel}: {msg}")
        if fm_errors:
            continue

        for key in REQUIRED_KEYS:
            if not str(data.get(key, "")).strip():
                errors.append(f"{rel}: missing or empty '{key}'")

        trigger_val = data.get("triggers", data.get("trigger"))
        if isinstance(trigger_val, list):
            if not [x for x in trigger_val if str(x).strip()]:
                errors.append(f"{rel}: triggers/trigger must not be empty")
        elif not str(trigger_val or "").strip():
            errors.append(f"{rel}: missing or empty 'triggers'/'trigger'")

        name = str(data.get("name", "")).strip()
        if name:
            if name in names:
                errors.append(
                    f"duplicate skill name '{name}' in {names[name].relative_to(root)} and {rel}"
                )
            else:
                names[name] = skill_md

        refs = data.get("references")
        if isinstance(refs, list):
            ref_base = skill_md.parent
            for ref in refs:
                ref_path = ref_base / str(ref)
                if not ref_path.exists():
                    errors.append(f"{rel}: reference not found: {ref}")

        if args.opencode_compatible:
            if not str(data.get("description", "")).strip():
                errors.append(f"{rel}: missing or empty 'description'")

            fallback_name = skill_md.parent.name if skill_md.name == "skill.md" else skill_md.stem
            raw_name = str(data.get("name", "")).strip() or fallback_name
            normalized = normalize_opencode_name(raw_name, str(rel))
            if not normalized:
                errors.append(f"{rel}: OpenCode normalized name is empty")
            elif normalized in normalized_names:
                errors.append(
                    "duplicate OpenCode normalized skill name "
                    f"'{normalized}' from {normalized_names[normalized].relative_to(root)} and {rel}"
                )
            else:
                normalized_names[normalized] = skill_md

            for field in ["tools", "task_tools"]:
                val = data.get(field)
                if val is None:
                    continue
                if val == "" or not isinstance(val, list):
                    errors.append(f"{rel}: '{field}' must be a list or omitted")
                    continue
                for item in val:
                    if not str(item).strip():
                        errors.append(f"{rel}: '{field}' contains empty item")

    total_skill_md = sum(1 for d in skill_dirs if (d / "skill.md").exists())
    total_python_backed = sum(1 for d in skill_dirs if (d / "skill.py").exists())

    print(f"total skill directories: {len(skill_dirs)}")
    print(f"total skill.md discovered: {total_skill_md}")
    print(f"python-backed skills count: {total_python_backed}")
    print(
        "opencode-compatible checks: "
        + ("enabled" if args.opencode_compatible else "disabled")
    )
    if args.opencode_compatible:
        print(f"opencode normalized skill names: {len(normalized_names)}")

    if errors:
        print("\nValidation errors:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("\nValidation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
