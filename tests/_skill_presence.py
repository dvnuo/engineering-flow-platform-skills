"""Locate a skill, or skip when this branch does not carry it.

Skills are distributed on per-role branches: an assistant type points at one
branch, and that branch holds only the skills that role needs. Contract tests
name their subject directly, so on a branch without that skill they would fail
for the wrong reason -- reporting a broken contract when the skill is simply not
part of this role.

Skipping keeps every branch's CI meaningful: each one verifies the contracts of
the skills it actually ships, and the full set is still covered wherever all the
skills are present.
"""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def skill_dir(name: str) -> Path:
    return REPO_ROOT / name


def has_skill(name: str) -> bool:
    return (skill_dir(name) / "skill.md").is_file()


def require_skill(name: str) -> Path:
    """Return the skill's skill.md, skipping if this branch omits the skill."""

    path = skill_dir(name) / "skill.md"
    if not path.is_file():
        pytest.skip(f"{name} is not on this branch")
    return path


def require_skills(names: list[str]) -> list[str]:
    """Return the subset present here, skipping only if none are."""

    present = [name for name in names if has_skill(name)]
    if not present:
        pytest.skip(f"none of {', '.join(names)} are on this branch")
    return present
