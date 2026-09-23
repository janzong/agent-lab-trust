# Agent Lab Trust

Part of the **agent trust series**: [SERIES.md](SERIES.md) — write it down → test it → govern it.

[![reproduce](https://github.com/janzong/agent-lab-trust/actions/workflows/reproduce.yml/badge.svg)](https://github.com/janzong/agent-lab-trust/actions/workflows/reproduce.yml)

Local-first, read-only agent run validator.

It does three things:

- `validate <root>` — discover runs, enforce strict validity (a non-empty
  `output/structured.json` or `results/structured.json`), and report per-run
  failure codes and cost per call;
- `report <root>` — aggregate runs into a canonical `report_hash`;
- `deletion-proof` — run a synthetic-only deletion drill and emit an `audit_hash`.

No network calls at test time. No private runs, bundles, credentials, prompts,
or model responses.

## Reproduce in one command

```bash
bash scripts/reproduce.sh
```

It prints one JSON block with the repo commit, both timezone test results,
`report_hash`, and deletion `audit_hash`. To report a reproduction, use the
“Reproduction report” issue template (fields only; no logs or credentials).

## Reproduce with Docker

```bash
docker run --rm ghcr.io/janzong/agent-lab-trust@sha256:9f9428557933004514ec6b54988fc3668071e1b73f87e0c3ac2e04ba4536f3a0
```

No Python setup required; the image runs the same one-command reproduction. The
`rc2` tag points to the same image, but the digest above is pinned so a local
registry cache cannot serve an older build.

## Run

```bash
python3 -m venv .venv
.venv/bin/pip install -i https://pypi.tuna.tsinghua.edu.cn/simple \
  'pydantic>=2.7,<3' 'pytest>=8,<9'

TZ=UTC .venv/bin/python -m pytest -q
.venv/bin/python -m agent_lab_trust.cli validate tests/fixtures/gen-mentor
.venv/bin/python -m agent_lab_trust.cli report tests/fixtures/gen-mentor
.venv/bin/python -m agent_lab_trust.cli deletion-proof
```

Expected:

| Check | Expected |
|---|---|
| tests | 13 passed under both `TZ=UTC` and `TZ=Asia/Shanghai` |
| `validate` | `replay-sample` success true, `failure_code` `"ok"` |
| `report` | runs 1, success 1, failure 0, `report_hash` `a841b192981fd7e7` |
| `deletion-proof` | `clean: true`, `audit_hash` `4f0193abbd49a0f9` |

## Governance audit

```bash
agent-lab-trust audit tests/fixtures/gen-mentor --policy policy.example.json
```

The audit checks each run against a JSON policy: per-run cost and call caps,
artifact contracts (`required_artifacts` with `required_artifacts_mode: all|any`),
and forbidden markers. It prints a canonical `audit_hash`. `deletion-proof
--output <path>` writes the deletion proof used in the same policy flow.

## Seeking 3 independent reproductions

This is `v0.1.0-rc2`. I am looking for **3 independent reproductions by
non-authors**. Run the commands above and report only: machine/Python, test
count, `report_hash`, `audit_hash`, and whether the artifact SHA matched. See
the issue tracker for the current request.

## Limits

- author-side verification only so far;
- no real learner data;
- this validates run artifacts and deletion proof, not agent quality.
