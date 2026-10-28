# Case Pattern: Controlled Adoption Is Not Asset Reproduction

## Problem

An asset can be successfully selected and accepted inside a controlled
experiment while never appearing in later normal work. Reporting such an
experiment as “asset reuse” or “compounding” overstates what happened.

## Mechanism

```text
stock
→ review and mapping
→ controlled activation
→ human acceptance
→ cohort cutoff
→ later normal workflow
→ natural selection
→ accepted material use
→ asset reproduction
```

## Production case

Controlled activation:

```text
controlled projects: 17
human-accepted outputs: 17 / 17
reviewed claim cards used: 41 / 45
remaining cards: 4 non-argumentative, deliberately excluded
```

Later intranet natural-reuse cohort:

```text
eligible projects in snapshot: 97
primary preregistered sample: earliest 50
target-claim natural usage: 0
target claims with usage: 0 / 27
accepted natural uses: 0
adoption decisions in primary sample: 4 regenerate
```

All-97 sensitivity analysis also found zero target-claim usage.

## Cohort caution

The zero-use result is highly concentrated:

```text
source kind: training_profile for 97 / 97
config families: al1 / liang1 only
large creation-time clusters
```

It is a valid result for this cohort, not a general conclusion about all
docs-domain workflows.

## Policy mapping

```json
{
  "id": "natural_reuse_requires_uncontrolled_selection",
  "policy_type": "required_transition",
  "fail_closed": true,
  "expected_inputs": [
    "cohort_cutoff",
    "controlled_project_exclusions",
    "eligible_workflow_count",
    "natural_selection_rows",
    "accepted_material_use_rows"
  ]
}
```

## Evidence worth retaining

```text
controlled activation ledger
human acceptance decisions
cohort cutoff
controlled-project exclusions
eligible workflow count
workflow/source/config distribution
natural selection rows
accepted material-use rows
creation-time concentration
```

## Boundary

This case does not prove that:

- the target assets are useless;
- the matcher is broken;
- controlled activation was invalid;
- all normal workflows will reject the assets;
- reuse would imply causal productivity improvement.

It proves that this cohort did not provide natural-reproduction evidence.

## Related artifacts

- [Natural-reuse method card](../method-cards-20261026.md#7-natural-reuse-observation)
- [Governed production essay](https://dev.to/janzong/from-capability-to-governed-production-5g7k)
- [Policy candidates](../policy-candidates-v0.json)
