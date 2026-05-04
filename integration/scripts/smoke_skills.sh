#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${REPO_ROOT}"

python scripts/validate_skills.py --root "${REPO_ROOT}"
python scripts/validate_skills.py --root "${REPO_ROOT}" --opencode-compatible
python -m pytest -q tests/test_validate_skills.py
