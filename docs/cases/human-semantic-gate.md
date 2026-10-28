# Case Pattern: Human Semantic Gate

## Problem

Mechanical validation can establish that a record is well formed while missing
what the record means. A concept-like string may actually be an institution, an
event, a policy, or a sentence fragment. A relation can have valid identifiers
while pointing in the wrong semantic direction.

## Mechanism

```text
machine pre-label
→ stratified human sample
→ measured agreement or precision
→ preregistered threshold
→ apply, reject, or enlarge sample
→ manifest
```

The gate does not ask a human to inspect every row. It asks whether the
production write has enough sampled evidence to support admission.

## Production case

During semantic cleanup of a knowledge base, machine pre-labeling was used to
reduce the candidate pool. Human review then qualified the remaining semantic
labels:

```text
method labels after semantic relabel: 281 → 106
citable objects after semantic relabel: 6,006 → 3,940
independent method-label agreement: 87.5%
independent citable-label agreement: 88%
```

The reductions were not treated as losses by default. They were the result of
separating mechanical validity from semantic acceptance.

## Evidence worth retaining

```text
model and prompt/rule version
label distribution
sample size
sampling strata
human agreement or precision
threshold
apply/reject decision
review manifest
```

Reviewer identity is not required in the public case pattern.

## Policy mapping

```json
{
  "id": "human_precision_threshold",
  "policy_type": "threshold",
  "fail_closed": true,
  "threshold": {
    "metric": "human_precision",
    "minimum": 0.8,
    "minimum_sample": 25
  },
  "on_failure": "block",
  "blocked_operation": "semantic_production_write"
}
```

## Boundary

This case does not prove that:

- the human sample certifies every unsampled record;
- agreement with reviewers proves semantic truth;
- the same threshold applies to every domain;
- low agreement means the model is useless;
- high agreement proves user value.

Sampling estimates quality. It does not exhaustively verify a population.

## Why the gate matters

The gate makes three facts visible:

1. machines can reduce inspection scale without owning semantic authority;
2. human review can be measured rather than described;
3. a semantic production write can be blocked before it becomes shared state.

## Related artifacts

- [Human-sample semantic gate method card](../method-cards-20261026.md#4-human-sample-semantic-gate)
- [Policy candidates](../policy-candidates-v0.json)
- [Governed production essay](https://dev.to/janzong/from-capability-to-governed-production-5g7k)
