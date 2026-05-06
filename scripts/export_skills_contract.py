#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.validate_skills import (  # noqa: E402
    discover_skill_files,
    normalize_opencode_name,
    parse_frontmatter,
    validate_root,
)


SCHEMA_VERSION = "efp.skills.contract.v1"
VALID_SCOPES = {"production", "integration-fixtures"}


class ContractValidationError(ValueError):
    def __init__(self, errors: list[str], stats: dict[str, int] | None = None) -> None:
        super().__init__("\n".join(errors))
        self.errors = errors
        self.stats = stats or {}


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _skill_record(root: Path, skill_md: Path) -> dict[str, object]:
    rel = skill_md.relative_to(root)
    data, _ = parse_frontmatter(skill_md.read_text(encoding="utf-8"))

    fallback_name = skill_md.parent.name if skill_md.name == "skill.md" else skill_md.stem
    raw_name = str(data.get("name", "")).strip() or fallback_name
    normalized_name = normalize_opencode_name(raw_name, str(rel))

    trigger_values = _string_list(data.get("triggers"))
    if not trigger_values:
        trigger_scalar = data.get("trigger")
        if trigger_scalar is not None and str(trigger_scalar).strip():
            trigger_values = [str(trigger_scalar)]

    opencode = data.get("opencode") if isinstance(data.get("opencode"), dict) else {}
    permission = opencode.get("permission") if isinstance(opencode.get("permission"), dict) else {}
    tool_mappings = opencode.get("tool_mappings") if isinstance(opencode.get("tool_mappings"), dict) else {}

    directory = skill_md.parent.name if skill_md.name == "skill.md" else skill_md.stem

    return {
        "path": rel.as_posix(),
        "directory": directory,
        "name": str(data.get("name", "")),
        "normalized_opencode_name": normalized_name,
        "description": str(data.get("description", "")),
        "version": str(data.get("version", "")),
        "owner": str(data.get("owner", "")),
        "triggers": trigger_values,
        "tools": _string_list(data.get("tools")),
        "task_tools": _string_list(data.get("task_tools")),
        "references": _string_list(data.get("references")),
        "python_backed": (skill_md.parent / "skill.py").exists(),
        "opencode": {
            "execution_kind": str(opencode.get("execution_kind", "")),
            "compatibility": str(opencode.get("compatibility", "")),
            "permission_default": str(permission.get("default", "")),
            "capability_tags": _string_list(opencode.get("capability_tags")),
            "tool_mappings": {str(k): str(v) for k, v in tool_mappings.items()},
        },
    }


def _validate_root_for_contract(root: Path) -> dict[str, int]:
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"skills root not found or not a directory: {root}")

    exit_code, errors, stats = validate_root(root, opencode_compatible=True)
    if exit_code != 0:
        raise ContractValidationError(errors, stats)

    return stats


def build_contract(root: Path, scope: str) -> dict[str, object]:
    if scope not in VALID_SCOPES:
        raise ValueError(
            f"invalid scope {scope!r}; expected one of: integration-fixtures, production"
        )

    root = root.resolve()
    stats = _validate_root_for_contract(root)

    errors: list[str] = []
    _, skill_files = discover_skill_files(root, errors)
    if errors:
        raise ContractValidationError(errors, stats)

    records = [_skill_record(root, skill_md) for skill_md in skill_files]
    records.sort(key=lambda item: (str(item["normalized_opencode_name"]), str(item["path"])))
    return {
        "schema_version": SCHEMA_VERSION,
        "scope": scope,
        "stats": stats,
        "skills": records,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export machine-readable skills metadata contract JSON")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="skills repository root; defaults to this script's parent repository",
    )
    parser.add_argument(
        "--scope",
        choices=["production", "integration-fixtures"],
        default="production",
    )
    parser.add_argument("--output", type=Path, help="output JSON file path; defaults to stdout")
    parser.add_argument("--pretty", action="store_true", help="pretty-print JSON with 2-space indentation")
    args = parser.parse_args(argv)

    try:
        contract = build_contract(args.root, scope=args.scope)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except ContractValidationError as exc:
        for err in exc.errors:
            print(f"- {err}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    dump_kwargs: dict[str, object] = {"ensure_ascii": False, "sort_keys": True}
    if args.pretty:
        dump_kwargs["indent"] = 2

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as fh:
            json.dump(contract, fh, **dump_kwargs)
            fh.write("\n")
    else:
        json.dump(contract, sys.stdout, **dump_kwargs)
        sys.stdout.write("\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
