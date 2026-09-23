# Agent Lab Trust

Part of the **agent trust series**: [SERIES.md](SERIES.md) — write it down → test it → govern it. Write-ups: [negative result](https://dev.to/janzong/we-ran-2-vs-4-agents-six-times-four-agents-cost-21x-and-did-not-improve-success-k98) · [governance audit](https://dev.to/janzong/your-agent-run-passed-can-you-prove-it-was-allowed-3d5i).

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
docker run --rm ghcr.io/janzong/agent-lab-trust@sha256:0c65075920b991b6f5fc822b8e3b7ab2ca5c69850c2b3ef16f2cc78a0241ddb6
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
| tests | 22 passed under both `TZ=UTC` and `TZ=Asia/Shanghai` |
| `validate` | `replay-sample` success true, `failure_code` `"ok"` |
| `report` | runs 1, success 1, failure 0, `report_hash` `a841b192981fd7e7` |
| `deletion-proof` | `clean: true`, `audit_hash` `4f0193abbd49a0f9` |
| `audit` | `passed: true`, `audit_hash` `b304f294834a5901101d45fb98547c233d90e16c2f7cb5b965ce16641b1acbd3` |

## Governance audit

```bash
agent-lab-trust audit tests/fixtures/gen-mentor --policy policy.example.json
```

The audit checks each run against a JSON policy: per-run cost and call caps,
artifact contracts (`required_artifacts` with `required_artifacts_mode: all|any`),
and forbidden markers. It prints a canonical `audit_hash`. `deletion-proof
--output <path>` writes the deletion proof used in the same policy flow.

## Seeking 3 independent reproductions

This is the current main (policy pinning included). For the pre-audit `v0.1.0-rc2` snapshot, use the release tag; the issue pins both targets. I am looking for **3 independent reproductions by non-authors**. Run the commands above and report only: machine/Python, test
count, `report_hash`, `audit_hash`, and whether the artifact SHA matched. See
the issue tracker for the current request.

## Limits

- author-side verification only so far;
- no real learner data;
- this validates run artifacts and deletion proof, not agent quality.
