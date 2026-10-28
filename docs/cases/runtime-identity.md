# Case Pattern: Runtime Identity

## Problem

A health endpoint can report an expected version while the process, code,
artifact, data, or served model differs from the intended deployment.

## Mechanism

```text
target commit
actual commit
process start time
health version
frontend artifact hash
table counts or checksums
rollback position
requested model
served model
provider
```

Deployment verification reads these facts back rather than inferring identity
from health alone.

## Production case

The production verification checked target and actual deployment identity,
process start time, health version, frontend artifact identity, table counts and
checksums, rollback position, and model attribution. A successful health check
was treated as one signal, not as proof that the expected code or model was
actually serving.

## Policy mapping

```json
{
  "id": "runtime_identity_required",
  "policy_type": "required",
  "fail_closed": true,
  "expected_inputs": [
    "target_commit",
    "actual_commit",
    "process_start_time",
    "health_version",
    "artifact_hash",
    "table_counts",
    "rollback_path",
    "requested_model",
    "served_model",
    "provider"
  ]
}
```

## Evidence worth retaining

```text
deployment timestamp
target and actual commit
process start time
frontend artifact hash
per-table counts or checksums
rollback path
requested model
served model and provider
verification result
```

## Boundary

This case does not prove that:

- the output is semantically correct;
- the source evidence is valid;
- the model response has user value;
- the deployment has no undiscovered operational risk.

Runtime identity establishes provenance. It does not establish quality.

## Related artifacts

- [Runtime identity method card](../method-cards-20261026.md#8-runtime-identity)
- [Policy candidates](../policy-candidates-v0.json)
- [Governed production essay](https://dev.to/janzong/from-capability-to-governed-production-5g7k)
