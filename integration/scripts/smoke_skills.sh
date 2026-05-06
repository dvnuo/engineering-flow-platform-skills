#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${REPO_ROOT}"

python scripts/validate_skills.py --root "${REPO_ROOT}"
python scripts/validate_skills.py --root "${REPO_ROOT}" --opencode-compatible
python scripts/validate_skills.py --root "${REPO_ROOT}/integration/fixtures" --opencode-compatible

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

python scripts/export_skills_contract.py \
  --root "${REPO_ROOT}" \
  --scope production \
  --output "${TMP_DIR}/skills-contract.json" \
  --pretty
python -m json.tool "${TMP_DIR}/skills-contract.json" >/dev/null

python scripts/export_skills_contract.py \
  --root "${REPO_ROOT}/integration/fixtures" \
  --scope integration-fixtures \
  --output "${TMP_DIR}/skills-fixtures-contract.json" \
  --pretty
python -m json.tool "${TMP_DIR}/skills-fixtures-contract.json" >/dev/null

python -m pytest -q
