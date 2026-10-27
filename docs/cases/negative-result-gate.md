# Case Pattern: Negative-Result Gate

## Problem

An agent can generate a large set of plausible structured relationships. The
structure looks useful, the coverage looks impressive, and each candidate has an
identifier. The hard question is whether the relationships are reliable enough
to enter a production graph.

In a production knowledge-governance trial, an extraction pipeline generated:

```text
candidate relations: 308
human sample: 50
correct: 10
precision: 20%
preregistered threshold: 80%
production writes: 0
```

The system retained the candidates and review table, but wrote zero typed
relations to production.

## Mechanism

```text
declare method and threshold
→ generate candidates
→ draw a human sample
→ compute precision
→ compare against the threshold
→ retain artifacts
→ block production write if the gate fails
```

The gate is useful only when all parts are present:

- the threshold existed before evaluation;
- the candidate artifact is retained;
- the human sample is retained;
- precision is computable;
- the production write count is checkable;
- the failed method is marked deferred, not impossible.

## Policy mapping

```json
{
  "id": "negative_result_gate",
  "policy_type": "threshold",
  "fail_closed": true,
  "threshold": {
    "metric": "human_precision",
    "minimum": 0.8
  },
  "on_failure": "block",
  "blocked_operation": "production_write",
  "expected_inputs": [
    "candidate_count",
    "human_sample_count",
    "correct_count",
    "production_write_count"
  ]
}
```

## Evidence worth retaining

```text
method version
prompt or rule version, if public and safe
candidate artifact path or hash
human-review table path or hash
threshold declaration
computed precision
production write count
decision timestamp
reviewer role
```

For public case patterns, reviewer identity is not required.

## Boundary

This case does **not** prove that:

- typed relation extraction is permanently impossible;
- every LLM-generated relation is wrong;
- the sample represents every unseen candidate exactly;
- blocking the write improved downstream business productivity;
- the same threshold applies to every domain.

It proves that this method, data representation, evidence binding, and threshold
combination was unsafe for production at the time of the trial.

## Why the negative result is capital

The failed trial:

1. prevented a low-precision graph from entering production;
2. made a quality boundary explicit;
3. preserved evidence for future method comparison;
4. avoided a later cleanup operation;
5. made the system’s refusal observable rather than rhetorical.

## Related artifacts

- [Negative-result gate method card](../method-cards-20261026.md#3-negative-result-gate)
- [Policy candidates](../policy-candidates-v0.json)
- [Governed production essay](https://dev.to/janzong/from-capability-to-governed-production-5g7k)
