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
docker run --rm ghcr.io/janzong/agent-lab-trust@sha256:a5a170b2b2801bd61ff9c189c8f391323cfd8e8ca4e236f049abeaf85e97a28f
```

No Python setup required; the image runs the same one-command reproduction. The digest above is
pinned so a local registry cache cannot serve a different build. The `rc2` **tag** is *not* the
same build: it still resolves to the pre-audit snapshot (13 tests, no governance audit) — use the
pinned digest above for the current build.

## Run

```bash
python3 -m venv .venv
.venv/bin/pip install 'pydantic>=2.7,<3' 'pytest>=8,<9'
# Optional: if PyPI is slow on your network, add a mirror, e.g.
# .venv/bin/pip install -i https://pypi.tuna.tsinghua.edu.cn/simple 'pydantic>=2.7,<3' 'pytest>=8,<9'

TZ=UTC .venv/bin/python -m pytest -q
.venv/bin/python -m agent_lab_trust.cli validate tests/fixtures/gen-mentor
.venv/bin/python -m agent_lab_trust.cli report tests/fixtures/gen-mentor
.venv/bin/python -m agent_lab_trust.cli deletion-proof
```

Expected:

| Check | Expected |
|---|---|
| tests | 29 passed under both `TZ=UTC` and `TZ=Asia/Shanghai` |
| `validate` | `replay-sample` success true, `failure_code` `"ok"` |
| `report` | runs 1, success 1, failure 0, `report_hash` `a841b192981fd7e7` |
| `deletion-proof` | `clean: true`, `audit_hash` `4f0193abbd49a0f9` |
| `audit` | `passed: true`, `audit_hash` `b304f294834a5901101d45fb98547c233d90e16c2f7cb5b965ce16641b1acbd3` |

## Governance audit

### Batch contract

The optional `batch_contract` section lets you audit per-run quality metrics
against declared thresholds. Metrics are read from a JSON file inside each run
directory; fields are addressed by dotted path.

```json
"batch_contract": {
  "metrics_file": "output/structured.json",
  "metrics": {
    "metrics.citation_reconciliation": {"min": 0.5},
    "metrics.dirty_entries": {"max": 4}
  }
}
```

**Contract evolution**: when you add a new metric field, give it a default
value in your producer so old runs still parse. A missing or non-numeric field
emits `batch_metric_unknown` (fail-closed), not zero — per the
[validity-states rule](docs/validity-states.md#the-absent-zero-rule). If a
metric only exists for new runs, split it into a separate metrics file or
version the file name rather than breaking the contract for old runs.

`policy.example.json` intentionally stays minimal so the bundled fixture
passes; add the `batch_contract` section only after your producer emits the
metrics it names.

```bash
agent-lab-trust audit tests/fixtures/gen-mentor --policy policy.example.json
```

The audit checks each run against a JSON policy: per-run cost and call caps,
artifact contracts (`required_artifacts` with `required_artifacts_mode: all|any`),
and forbidden markers. It prints a canonical `audit_hash`. `deletion-proof
--output <path>` writes the deletion proof used in the same policy flow.

## Method cards

[`docs/method-cards-20261026.md`](docs/method-cards-20261026.md) generalizes
production governance patterns into reusable audit ideas: exact evidence chains,
dry-run-first writes, negative-result gates, human-sample semantic gates, source
purity views, dual-host parity, natural-reuse observation, runtime identity, and
bounded expansion tiering.

## Policy candidates

[`policy-candidates-v0.json`](policy-candidates-v0.json) defines the design-only
successor to those cards: named checks, required inputs, thresholds, and
fail-closed behavior. See
[`docs/policy-candidates-v0.md`](docs/policy-candidates-v0.md). No candidate is
executable by the v0.1.0 CLI yet.

## Public case patterns

[`docs/cases/negative-result-gate.md`](docs/cases/negative-result-gate.md)
generalizes the 308-candidate / 20%-precision / zero-production-write trial into
a reusable governance pattern.

## Theory essay

[`From Capability to Governed Production`](https://dev.to/janzong/from-capability-to-governed-production-5g7k)
proposes a minimal theory of governed agent production. The repository edition is
[`docs/essays/from-capability-to-governed-production-public-v1.md`](docs/essays/from-capability-to-governed-production-public-v1.md).

## Reproduction status

Three independent non-author reproductions are complete, and the reproduction
issue is closed as completed:
<https://github.com/janzong/agent-lab-trust/issues/1>.

v0.1.0 is published:
<https://github.com/janzong/agent-lab-trust/releases/tag/v0.1.0>.

Current main requires Python 3.11 or newer. The pre-audit `v0.1.0-rc2`
snapshot remains available from the release tag; use the pinned Docker digest
above for the current policy-audit build.

## Limits

- author-side verification only so far;
- no real learner data;
- this validates run artifacts and deletion proof, not agent quality.
