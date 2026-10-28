# Case Pattern: Bounded Expansion

## Problem

A teaching or research agent often needs to move beyond supplied course or task
context. Unbounded synthesis can turn inference into apparent authority.

## Mechanism

```text
course or task seed
→ canonical reference or theory whitelist
→ evidence-backed external expansion
→ question-only fallback
```

The seed is a provenance anchor, not a wall. The system may connect outward, but
the evidence tier must remain visible.

## Production case

The teaching-companion review separated course fidelity, whitelisted theory
connections, evidence-backed beyond material, and question-only fallback. A
claim outside the available evidence was not accepted as a conclusion merely
because it was pedagogically useful.

## Policy mapping

```json
{
  "id": "bounded_expansion_tiering_required",
  "policy_type": "required",
  "fail_closed": true,
  "expected_inputs": [
    "seed_context_id",
    "canonical_reference_ids",
    "external_evidence_ids",
    "unsupported_statements",
    "question_only_fallbacks"
  ]
}
```

## Evidence worth retaining

```text
course/task seed identifier
canonical or whitelisted references
external evidence identifiers
unsupported statements
question-only fallbacks
review decision
```

## Boundary

This case does not prove that:

- the expanded material improves learning outcomes;
- the user finds the expansion relevant;
- a whitelist is complete or authoritative;
- the fallback is pedagogically ideal.

Evidence tiering improves provenance and reviewability, not classroom effect.

## Related artifacts

- [Bounded expansion method card](../method-cards-20261026.md#9-bounded-expansion-tiering)
- [Policy candidates](../policy-candidates-v0.json)
- [Governed production essay](https://dev.to/janzong/from-capability-to-governed-production-5g7k)
