# Case Pattern: Exact Evidence Chain

## Problem

An agent can cite a real document title while using content that the document
does not support. A title match, semantic similarity, or model confidence score
is not sufficient evidence for a citable object.

## Mechanism

```text
citable object
⇒ authorized source
⇒ verified evidence span
⇒ quote reproduced at a recorded offset
⇒ current chunk covers the interval
⇒ source is published
```

## Production case

The production knowledge base used one exact-evidence invariant for the final
citable layer:

```text
citable objects: 3,940
citable objects with verified exact evidence: 3,940 / 3,940
bad quote/offset failures: 0
current-chunk coverage failures: 0
archived/orphan/non-published citable: 0
recent report discovery links present: 687 / 687
```

The evidence chain changed the question from:

```text
Did the model cite a real document?
```

to:

```text
Can an independent reviewer replay the exact quote through a current source?
```

## Policy mapping

```json
{
  "id": "exact_evidence_required",
  "policy_type": "required",
  "fail_closed": true,
  "expected_inputs": [
    "asset_id",
    "quote",
    "source_sha",
    "chunk_id",
    "source_status"
  ]
}
```

## Evidence worth retaining

```text
citable object count
verified evidence count
quote/offset mismatch count
current chunk coverage failures
archived/orphan/non-published count
source document status
report-level citation resolution count
```

## Boundary

This case does not prove that:

- an exact quote supports the surrounding generated claim semantically;
- the source is authoritative for every domain use;
- a citation is relevant to the user;
- source existence implies correct reasoning.

Exact evidence proves reproducibility. Human semantic judgment remains separate.

## Related artifacts

- [Exact evidence method card](../method-cards-20261026.md#1-exact-evidence-chain)
- [Policy candidates](../policy-candidates-v0.json)
- [Governed production essay](https://dev.to/janzong/from-capability-to-governed-production-5g7k)
