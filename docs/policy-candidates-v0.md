# Agent Trust Policy Candidates v0

`policy-candidates-v0.json` defines the next layer above the current method
cards: named checks that an audit policy can express. Three inputs-first checks
are executable in v0; the remaining checks stay design-only.

## Candidate checks

| Check | Failure mode |
|---|---|
| `exact_evidence_required` | fail closed if exact source/chunk evidence is absent |
| `dry_run_required` | fail closed if a production mutation has no dry-run plan |
| `negative_result_gate` | block production writes when human precision misses 0.80 |
| `human_precision_threshold` | block semantic writes below 0.80 precision |
| `source_purity_required` | fail closed when a requested source view is contaminated |
| `host_parity_required` | fail closed when host counts/checksums differ |
| `rollback_manifest_required` | fail closed when rollback/manifest artifacts are absent |
| `natural_reuse_requires_uncontrolled_selection` | fail closed when controlled adoption is presented as natural reuse |
| `runtime_identity_required` | fail closed when code, process, artifact, data, or model identity is absent |
| `bounded_expansion_tiering_required` | fail closed when expansion beyond a seed lacks explicit evidence tiers |

## Boundary

This schema does not replace the existing run policy. It records the contract
needed before implementation:

```text
method card
→ named check
→ required inputs
→ threshold / artifact requirement
→ fail-closed behavior
```

The shipped example can be evaluated without touching any external system:

```bash
agent-lab-trust policy-check examples/policy-evidence/evidence.json \
  --policy policy-candidates-v0.json \
  --root examples/policy-evidence
```

Missing evidence for any implemented check is fail-closed. The output includes
per-check results, missing inputs, unimplemented checks, `policy_sha256`, and
`evaluation_sha256`.

Public case pattern for `negative_result_gate`:
[`../docs/cases/negative-result-gate.md`](cases/negative-result-gate.md).
