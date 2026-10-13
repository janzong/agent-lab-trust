# Field Manual: Agent Governance in Practice

> A thematic guide distilled from eight published articles and 30 preregistered
> real tasks. Unlike the article series, which follows a timeline, this manual
> organizes the same knowledge by topic so practitioners can jump to what they
> need.

## Contents

1. [Measurement](#1-measurement)
2. [Governance](#2-governance)
3. [Collaboration](#3-collaboration)
4. [Cognitive Framework](#4-cognitive-framework)
5. [Negative Results](#5-negative-results)

---

## 1. Measurement

### The absent-zero rule

An absent event must be reported as unknown, never as zero. A counter may
report zero only when it was actually evaluated for the subject and observed
no matching events. If the recording path was never reached, the correct value
is unknown.

**Real incident**: reports had accumulated 9,107 citations of research gaps;
the consumption ledger recorded zero because a boolean field meant "converted
to a task" was being read as "cited."

→ [Full specification](validity-states.md#the-absent-zero-rule)

### Measurement-window validity

A measurement can execute successfully and still be invalid as evidence: it
may run before the object has reached its final state. Only final-object
measurements may be marked valid.

**Real incident**: a quality grader inspected only the first 6,000 characters
of each report; references and conclusions were appended later. The grader
looked valid but had measured a prefix.

→ [Full specification](validity-states.md#measurement-window-validity)

### Three states

Every measured outcome is one of: **valid**, **invalid**, or
**unknown-or-unattributable**. The third state is mandatory; collapsing it
into the other two silently deletes the information that something was
unmeasured.

### Batch contract

Per-run quality metrics can be audited against declared thresholds using the
optional `batch_contract` policy section. Missing metrics are
`batch_metric_unknown` (fail-closed), not zero.

→ [Usage guide](../README.md#governance-audit)

---

## 2. Governance

### The shadow-to-gate pipeline

The sequence for fixing a systemic quality problem:

```text
blind review → shadow audit → source fix → calibrated gate → batch dashboard
```

1. **Blind review**: two independent agents analyze the same corpus without
   seeing each other's conclusions. Convergence means the problem is real.
2. **Shadow audit**: record metrics without blocking. Learn the distribution
   before setting any threshold.
3. **Source fix**: repair the mechanism, not individual instances.
4. **Calibrated gate**: block ingestion, not delivery. Set thresholds from the
   shadow distribution's percentiles.
5. **Batch dashboard**: five mechanical metrics computed after every batch,
   stored in a governance database.

**Real result**: citation reconciliation median went from 0.32 to 1.00 in one
production batch; fixed closing-sentence rate went from 97.3% to 0%.

### Block ingestion, not delivery

A report with broken citations may still be useful to the requester; poisoned
knowledge is not. The cost asymmetry runs in one direction: visible badness
can be corrected, silent contamination compounds.

### Contract-change assertion sync

When a tracked field name or metric contract changes, every assertion point
that references it must be updated simultaneously. A contract change with zero
assertion updates is suspect. This rule was learned from a real rework cycle
where adding a `surface` field to a tracking event broke five test assertions.

---

## 3. Collaboration

### Paired-agent verification

One agent implements; a second agent from a different harness independently
recomputes the full test suite and production probes before anything ships.
The implementer does not self-certify.

### Blind review convergence

When two independent analyses of the same corpus converge on the same
priority failures, that convergence is stronger evidence than either analysis
alone. We ran this with two agent harnesses on 150 generated reports; both
found the same three priority failures.

### Human gates

Some decisions should not be delegated:
- Whether to publish or export data
- Whether to resume a paused pipeline
- Whether a threshold change is safe

A gate that can say "ready" while a human still says "not worth the risk" is
working correctly. A gate that can only say "no" is theater.

---

## 4. Cognitive Framework

### Four cognitive operations

Every agent-assisted knowledge task should strengthen exactly one of:

1. **Systematize** — organize scattered material into structure
2. **Theorize** — connect specific observations to general principles
3. **Academicize** — bring scholarly rigor: citations, methods, evidence chains
4. **Systematize as architecture** — turn working pieces into a reproducible pipeline

If a proposed capability does not strengthen one of these, it does not get built.

### The knowledge flywheel

```text
Documents → Extract → Research → Discover → Challenge → Feed back → New Research
```

Each turn measurably increases the knowledge base. The flywheel is not a
metaphor — it is countable: more nodes, more links, more reports, more challenges.

### Editor, not author

The agent receives curated material nodes and organizes them into a coherent
narrative. It does not receive a blank page. This is the difference between a
system that generates text and one that generates knowledge.

### The gate question

Before any batch: which cognitive operation does this strengthen? Which
flywheel stage does it feed? Which evolution line — breadth or depth? What
are the three expected outcomes? Fuzzy answers mean fuzzy work.

---

## 5. Negative Results

### Reservation discipline breaks under density

In a preregistered cohort of 30 real tasks, three slots were reserved after
implementation had already begun. One working day produced 17 unslotted
commits. Writing the rule down did not change behavior.

### Rework = 0 is a blind spot

The cohort recorded 0/30 rework events although real rework demonstrably
occurred. Voluntary rework reporting produced zero coverage. An absent record
was rendered as a confident zero — the same error as the gap incident, wearing
a governance costume.

### Duration coverage drifted mid-cohort

Only 9 of 30 slots carried explicit durations because the recorder changed
mid-cohort. Any trend in that column is a measurement artifact, not a process
improvement.

### What v2 changes

Machine-checked reservation timing, mandatory rework events, frozen recorder
before slot 1, multi-operator requirement, contract-change assertion sync,
and publication defaulting to private.

→ [v2 draft](https://github.com/janzong/agent-lab-data/blob/main/field-lab/policies/realtime-cohort-v2-preregistration-draft.md) *(private repository)*
