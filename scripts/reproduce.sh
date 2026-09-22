#!/usr/bin/env bash
# One-command reproduction for agent-lab-trust.
set -euo pipefail
cd "$(dirname "$0")/.."

PY="${PYTHON:-python3}"
if [ ! -d .venv ]; then
  "$PY" -m venv .venv
fi
.venv/bin/pip install -q -i https://pypi.tuna.tsinghua.edu.cn/simple \
  'pydantic>=2.7,<3' 'pytest>=8,<9'

utc="$(TZ=UTC .venv/bin/python -m pytest -q 2>&1 | tail -1)"
shanghai="$(TZ=Asia/Shanghai .venv/bin/python -m pytest -q 2>&1 | tail -1)"
validate="$(.venv/bin/python -m agent_lab_trust.cli validate tests/fixtures/gen-mentor)"
report="$(.venv/bin/python -m agent_lab_trust.cli report tests/fixtures/gen-mentor)"
deletion="$(.venv/bin/python -m agent_lab_trust.cli deletion-proof)"
commit="$(git rev-parse HEAD 2>/dev/null || echo unknown)"

COMMIT="$commit" UTC="$utc" SHANGHAI="$shanghai" VALIDATE="$validate" REPORT="$report" DELETION="$deletion" \
python3 - <<'PY'
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
