# Agent Trust Policy Candidates v0

`policy-candidates-v0.json` defines the next layer above the current method
cards: named checks that a future audit policy can express. It is deliberately
**design-only** and not executable by the v0.1.0 CLI.

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

Implementation should begin only after one real adapter can provide all inputs
for at least two checks.

Public case pattern for `negative_result_gate`:
[`../docs/cases/negative-result-gate.md`](cases/negative-result-gate.md).
