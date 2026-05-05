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
OPENCODE_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
OPENCODE_PERMISSION_DEFAULTS = {"allow", "ask", "deny"}
OPENCODE_EXECUTION_KINDS = {"prompt_only", "programmatic", "hybrid"}
OPENCODE_COMPATIBILITY_LEVELS = {"full", "degraded", "unsupported"}
OPENCODE_TOOL_NAME_RE = re.compile(r"^efp_[a-z0-9_]+$")


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
    def parse_scalar(raw: str) -> object:
        cleaned = raw.strip()
        if (
            (cleaned.startswith('"') and cleaned.endswith('"'))
            or (cleaned.startswith("'") and cleaned.endswith("'"))
        ) and len(cleaned) >= 2:
            return cleaned[1:-1]
        low = cleaned.lower()
        if low == "true":
            return True
        if low == "false":
            return False
        if re.fullmatch(r"-?\d+", cleaned):
            try:
                return int(cleaned)
            except ValueError:
                return cleaned
        return cleaned

    def clean_scalar(raw: str) -> str:
        parsed = parse_scalar(raw)
        return parsed if isinstance(parsed, str) else str(parsed)

    def parse_mapping(start: int, base_indent: int) -> tuple[dict[str, object], int]:
        data: dict[str, object] = {}
        i = start
        while i < len(fm_lines):
            raw = fm_lines[i]
            if not raw.strip() or raw.strip().startswith("#"):
                i += 1
                continue
            indent = len(raw) - len(raw.lstrip(" "))
            if indent < base_indent:
                break
            if indent > base_indent:
                i += 1
                continue
            m = re.match(r"^\s*([^:#][^:]*)\s*:\s*(.*)$", raw)
            if not m:
                i += 1
                continue
            key = parse_scalar(m.group(1))
            value = m.group(2)
            if value.strip() == "[]":
                data[key] = []
                i += 1
                continue
            if value.strip():
                data[key] = parse_scalar(value)
                i += 1
                continue
            i += 1
            list_items: list[str] = []
            j = i
            while j < len(fm_lines):
                line = fm_lines[j]
                if not line.strip():
                    j += 1
                    continue
                item_indent = len(line) - len(line.lstrip(" "))
                if item_indent <= base_indent:
                    break
                sm = re.match(r"^\s*-\s*(.*?)\s*$", line)
                if sm:
                    list_items.append(parse_scalar(sm.group(1)))
                    j += 1
                    continue
                break
            if list_items:
                data[key] = list_items
                i = j
                continue
            nested, next_i = parse_mapping(i, base_indent + 2)
            data[key] = nested if nested else ""
            i = next_i
        return data, i

    parsed, _ = parse_mapping(0, 0)
    return parsed, []


def _is_non_empty_string_list(value: object) -> bool:
    if not isinstance(value, list):
        return False
    return bool(value) and all(isinstance(item, str) and item.strip() for item in value)




def _collect_legacy_tool_names(data: dict[str, object], errors: list[str], rel: Path) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for field in ["tools", "task_tools"]:
        val = data.get(field)
        if val is None:
            continue
        if val == "" or not isinstance(val, list):
            errors.append(f"{rel}: '{field}' must be a list or omitted")
            continue
        for item in val:
            if not isinstance(item, str):
                errors.append(f"{rel}: '{field}' items must be non-empty strings")
                continue
            tool_name = item.strip()
            if not tool_name:
                errors.append(f"{rel}: '{field}' contains empty item")
                continue
            if tool_name not in seen:
                seen.add(tool_name)
                result.append(tool_name)
    return result


def validate_opencode_tool_mappings(
    *,
    rel: Path,
    opencode: dict[str, object],
    legacy_tool_names: list[str],
    errors: list[str],
) -> int:
    if not legacy_tool_names:
        mappings = opencode.get("tool_mappings")
        if mappings is None or mappings == {}:
            return 0
        if not isinstance(mappings, dict):
            errors.append(f"{rel}: opencode.tool_mappings must be a mapping/object when present")
            return 0
        if mappings:
            errors.append(
                f"{rel}: opencode.tool_mappings must be omitted or empty when tools/task_tools are empty"
            )
        return 0

    mappings = opencode.get("tool_mappings")
    if not isinstance(mappings, dict):
        errors.append(
            f"{rel}: opencode.tool_mappings must map every tools/task_tools item to its OpenCode wrapper name"
        )
        return 0

    cleaned_mappings: dict[str, object] = {}
    for raw_key, raw_value in mappings.items():
        if not isinstance(raw_key, str):
            errors.append(f"{rel}: opencode.tool_mappings keys must be non-empty strings")
            continue
        key = raw_key.strip()
        if not key:
            errors.append(f"{rel}: opencode.tool_mappings contains empty key")
            continue
        if key != raw_key:
            errors.append(
                f"{rel}: opencode.tool_mappings key '{raw_key}' must not include leading or trailing whitespace"
            )
            continue
        if key in cleaned_mappings:
            errors.append(
                f"{rel}: opencode.tool_mappings contains duplicate mapping for tool '{key}'"
            )
            continue
        cleaned_mappings[key] = raw_value

    expected_keys = set(legacy_tool_names)
    actual_keys = set(cleaned_mappings.keys())

    missing = sorted(expected_keys - actual_keys)
    extra = sorted(actual_keys - expected_keys)

    for key in missing:
        errors.append(f"{rel}: opencode.tool_mappings missing mapping for tool '{key}'")
    for key in extra:
        errors.append(f"{rel}: opencode.tool_mappings contains extra mapping for unknown tool '{key}'")

    accepted = 0
    for native_name in legacy_tool_names:
        raw_value = cleaned_mappings.get(native_name)
        if raw_value is None:
            continue
        if not isinstance(raw_value, str) or not raw_value.strip():
            errors.append(f"{rel}: opencode.tool_mappings.{native_name} must be a non-empty string")
            continue

        opencode_name = raw_value.strip()
        if not OPENCODE_TOOL_NAME_RE.fullmatch(opencode_name):
            errors.append(
                f"{rel}: opencode.tool_mappings.{native_name}='{opencode_name}' must match ^efp_[a-z0-9_]+$"
            )
            continue

        expected_value = f"efp_{native_name}"
        if opencode_name != expected_value:
            errors.append(f"{rel}: opencode.tool_mappings.{native_name} must be '{expected_value}'")
            continue

        accepted += 1

    return accepted

def validate_opencode_metadata(
    *,
    rel: Path,
    data: dict[str, object],
    has_skill_py: bool,
    legacy_tool_names: list[str],
    errors: list[str],
) -> dict[str, object]:
    result: dict[str, object] = {}
    opencode = data.get("opencode")
    if not isinstance(opencode, dict):
        errors.append(f"{rel}: missing or invalid 'opencode' mapping for OpenCode compatibility")
        return result

    tool_mapping_count = validate_opencode_tool_mappings(
        rel=rel,
        opencode=opencode,
        legacy_tool_names=legacy_tool_names,
        errors=errors,
    )
    result["tool_mapping_count"] = tool_mapping_count

    execution_kind = opencode.get("execution_kind")
    if not isinstance(execution_kind, str) or execution_kind not in OPENCODE_EXECUTION_KINDS:
        errors.append(
            f"{rel}: opencode.execution_kind must be one of: hybrid, programmatic, prompt_only"
        )
    else:
        result["execution_kind"] = execution_kind

    compatibility = opencode.get("compatibility")
    if not isinstance(compatibility, str) or compatibility not in OPENCODE_COMPATIBILITY_LEVELS:
        errors.append(
            f"{rel}: opencode.compatibility must be one of: degraded, full, unsupported"
        )
    else:
        result["compatibility"] = compatibility

    permission_default = ""
    permission = opencode.get("permission")
    if isinstance(permission, dict):
        permission_default = permission.get("default", "")
    if (
        not isinstance(permission, dict)
        or not isinstance(permission_default, str)
        or permission_default not in OPENCODE_PERMISSION_DEFAULTS
    ):
        errors.append(f"{rel}: opencode.permission.default must be one of: allow, ask, deny")
    else:
        result["permission_default"] = permission_default

    capability_tags = opencode.get("capability_tags")
    if not _is_non_empty_string_list(capability_tags):
        errors.append(f"{rel}: opencode.capability_tags must be a non-empty list of strings")

    if has_skill_py and execution_kind == "prompt_only":
        errors.append(f"{rel}: Python-backed skill cannot use opencode.execution_kind=prompt_only")
    if has_skill_py and compatibility == "full":
        errors.append(
            f"{rel}: Python-backed skill cannot claim opencode.compatibility=full until OpenCode has a Python execution adapter"
        )
    if compatibility == "unsupported" and permission_default != "deny":
        errors.append(f"{rel}: unsupported OpenCode skill must use opencode.permission.default=deny")

    return result


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


def validate_root(root: Path, opencode_compatible: bool = False) -> tuple[int, list[str], dict[str, int]]:
    errors: list[str] = []

    nested_skills_dir = root / "skills"
    if nested_skills_dir.exists():
        errors.append(
            "nested skills/ directory is not allowed; repository root must be the skills root"
        )

    if (root / ".opencode").exists():
        errors.append(
            "generated OpenCode artifacts are not allowed in skills repo; "
            "remove .opencode/ and let opencode-runtime generate them at container startup"
        )

    if (root / "skills-index.json").exists():
        errors.append(
            "generated skills-index.json is not allowed in skills repo; "
            "it is runtime adapter state and must be generated by opencode-runtime"
        )

    skill_dirs, skill_files = discover_skill_files(root, errors)
    names: dict[str, Path] = {}
    normalized_names: dict[str, Path] = {}
    opencode_metadata_count = 0
    opencode_permission_counts = {"allow": 0, "ask": 0, "deny": 0}
    opencode_execution_kind_counts = {"prompt_only": 0, "programmatic": 0, "hybrid": 0}
    opencode_compatibility_counts = {"full": 0, "degraded": 0, "unsupported": 0}
    opencode_tool_required_skill_count = 0
    opencode_tool_mapped_skill_count = 0
    opencode_tool_mapping_count = 0

    for skill_md in skill_files:
        rel = skill_md.relative_to(root)
        content = skill_md.read_text(encoding="utf-8")
        data, fm_errors = parse_frontmatter(content)
        has_skill_py = (skill_md.parent / "skill.py").exists()
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

        if opencode_compatible:
            if not str(data.get("description", "")).strip():
                errors.append(f"{rel}: missing or empty 'description'")

            fallback_name = skill_md.parent.name if skill_md.name == "skill.md" else skill_md.stem
            raw_name = str(data.get("name", "")).strip() or fallback_name
            normalized = normalize_opencode_name(raw_name, str(rel))

            if not normalized:
                errors.append(f"{rel}: OpenCode normalized name is empty")
            elif not OPENCODE_NAME_RE.fullmatch(normalized):
                errors.append(
                    f"{rel}: OpenCode normalized name '{normalized}' must match "
                    "^[a-z0-9]+(?:-[a-z0-9]+)*$"
                )
            elif normalized in normalized_names:
                errors.append(
                    "duplicate OpenCode normalized skill name "
                    f"'{normalized}' from {normalized_names[normalized].relative_to(root)} and {rel}"
                )
            else:
                normalized_names[normalized] = skill_md

            legacy_tool_names = _collect_legacy_tool_names(data, errors, rel)
            if legacy_tool_names:
                opencode_tool_required_skill_count += 1

            opencode_meta = validate_opencode_metadata(
                rel=rel,
                data=data,
                has_skill_py=has_skill_py,
                legacy_tool_names=legacy_tool_names,
                errors=errors,
            )
            if opencode_meta:
                opencode_metadata_count += 1
                permission_default = opencode_meta.get("permission_default")
                execution_kind = opencode_meta.get("execution_kind")
                compatibility = opencode_meta.get("compatibility")
                if permission_default in opencode_permission_counts:
                    opencode_permission_counts[permission_default] += 1
                if execution_kind in opencode_execution_kind_counts:
                    opencode_execution_kind_counts[execution_kind] += 1
                if compatibility in opencode_compatibility_counts:
                    opencode_compatibility_counts[compatibility] += 1
                mapping_count = int(opencode_meta.get("tool_mapping_count", 0))
                opencode_tool_mapping_count += mapping_count
                if legacy_tool_names and mapping_count == len(legacy_tool_names):
                    opencode_tool_mapped_skill_count += 1

    stats = {
        "total_skill_directories": len(skill_dirs),
        "total_skill_md_discovered": len(skill_files),
        "python_backed_skills_count": sum(1 for d in skill_dirs if (d / "skill.py").exists()),
        "opencode_compatible_enabled": int(opencode_compatible),
        "opencode_normalized_skill_names": len(normalized_names),
        "opencode_metadata_count": opencode_metadata_count,
        "opencode_permission_default_allow_count": opencode_permission_counts["allow"],
        "opencode_permission_default_ask_count": opencode_permission_counts["ask"],
        "opencode_permission_default_deny_count": opencode_permission_counts["deny"],
        "opencode_execution_kind_prompt_only_count": opencode_execution_kind_counts["prompt_only"],
        "opencode_execution_kind_programmatic_count": opencode_execution_kind_counts["programmatic"],
        "opencode_execution_kind_hybrid_count": opencode_execution_kind_counts["hybrid"],
        "opencode_compatibility_full_count": opencode_compatibility_counts["full"],
        "opencode_compatibility_degraded_count": opencode_compatibility_counts["degraded"],
        "opencode_compatibility_unsupported_count": opencode_compatibility_counts["unsupported"],
        "opencode_tool_required_skill_count": opencode_tool_required_skill_count,
        "opencode_tool_mapped_skill_count": opencode_tool_mapped_skill_count,
        "opencode_tool_mapping_count": opencode_tool_mapping_count,
    }

    exit_code = 1 if errors else 0
    return exit_code, errors, stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="skills repository root; defaults to this script's parent repository",
    )
    parser.add_argument("--opencode-compatible", action="store_true")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    if not root.exists() or not root.is_dir():
        print(f"skills root not found or not a directory: {root}")
        return 2

    exit_code, errors, stats = validate_root(root, opencode_compatible=args.opencode_compatible)

    print(f"total skill directories: {stats['total_skill_directories']}")
    print(f"total skill.md discovered: {stats['total_skill_md_discovered']}")
    print(f"python-backed skills count: {stats['python_backed_skills_count']}")
    print(
        "opencode-compatible checks: "
        + ("enabled" if args.opencode_compatible else "disabled")
    )
    if args.opencode_compatible:
        print(f"opencode normalized skill names: {stats['opencode_normalized_skill_names']}")
        print(f"opencode metadata count: {stats['opencode_metadata_count']}")
        print(
            "opencode permission defaults: "
            f"allow={stats['opencode_permission_default_allow_count']} "
            f"ask={stats['opencode_permission_default_ask_count']} "
            f"deny={stats['opencode_permission_default_deny_count']}"
        )
        print(
            "opencode execution kinds: "
            f"prompt_only={stats['opencode_execution_kind_prompt_only_count']} "
            f"programmatic={stats['opencode_execution_kind_programmatic_count']} "
            f"hybrid={stats['opencode_execution_kind_hybrid_count']}"
        )
        print(
            "opencode compatibility levels: "
            f"full={stats['opencode_compatibility_full_count']} "
            f"degraded={stats['opencode_compatibility_degraded_count']} "
            f"unsupported={stats['opencode_compatibility_unsupported_count']}"
        )
        print(f"opencode tool-required skills: {stats['opencode_tool_required_skill_count']}")
        print(f"opencode tool-mapped skills: {stats['opencode_tool_mapped_skill_count']}")
        print(f"opencode tool mappings: {stats['opencode_tool_mapping_count']}")

    if errors:
        print("\nValidation errors:")
        for err in errors:
            print(f"- {err}")
        return exit_code

    print("\nValidation passed.")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
