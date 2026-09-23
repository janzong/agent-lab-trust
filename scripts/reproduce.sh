#!/usr/bin/env bash
# One-command reproduction for agent-lab-trust.
set -euo pipefail
cd "$(dirname "$0")/.."

if python3 -c 'import pydantic, pytest' >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  if [ ! -d .venv ]; then
    python3 -m venv .venv
  fi
  .venv/bin/pip install -q -i https://pypi.tuna.tsinghua.edu.cn/simple \
    'pydantic>=2.7,<3' 'pytest>=8,<9'
  PYTHON_BIN="$PWD/.venv/bin/python"
fi

utc="$(TZ=UTC "$PYTHON_BIN" -m pytest -q 2>&1 | tail -1)"
shanghai="$(TZ=Asia/Shanghai "$PYTHON_BIN" -m pytest -q 2>&1 | tail -1)"
validate="$("$PYTHON_BIN" -m agent_lab_trust.cli validate tests/fixtures/gen-mentor)"
report="$("$PYTHON_BIN" -m agent_lab_trust.cli report tests/fixtures/gen-mentor)"
deletion="$("$PYTHON_BIN" -m agent_lab_trust.cli deletion-proof)"
commit="$(git rev-parse HEAD 2>/dev/null || echo "${AGENT_LAB_COMMIT:-unknown}")"

COMMIT="$commit" UTC="$utc" SHANGHAI="$shanghai" VALIDATE="$validate" REPORT="$report" DELETION="$deletion" \
"$PYTHON_BIN" - <<'PY'
import json, os
print(json.dumps({
    "repo_commit": os.environ["COMMIT"],
    "tests_utc": os.environ["UTC"],
    "tests_asia_shanghai": os.environ["SHANGHAI"],
    "validate": json.loads(os.environ["VALIDATE"]),
    "report": json.loads(os.environ["REPORT"]),
    "deletion_proof": json.loads(os.environ["DELETION"]),
}, ensure_ascii=False, sort_keys=True))
PY
