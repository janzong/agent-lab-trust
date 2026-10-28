# Agent Trust Method Cards — 2026-10-26

These cards abstract governance patterns used by a production research system.
They are intentionally independent of private hosts, prompts, users, and model
responses. Each card defines the problem, the check, the boundary, and the
evidence worth retaining.

## 1. Exact Evidence Chain

### Problem

An agent cites a real document title, but the cited content does not support
the generated sentence.

### Method

Before an object is allowed into the citable layer, require:

```text
source object exists and is published
quote exists verbatim in source
quote offsets are correct
quote is covered by the currently effective chunk
evidence is verified
```

A useful SQL shape is:

```sql
substr(source.content, evidence.start + 1, evidence.end - evidence.start)
  = evidence.quote
```

and:

```sql
chunk.start <= evidence.start
AND chunk.end >= evidence.end
AND substr(chunk.text, evidence.start - chunk.start + 1,
           evidence.end - evidence.start) = evidence.quote
```

### Boundary

This proves exact source existence, not semantic fit, claim importance, or
user-facing correctness.

### Evidence

Store aggregate counts for:

- citable objects;
- objects with verified evidence;
- offset mismatches;
- stale/non-current chunk coverage;
- archived or unpublished sources.

## 2. Dry-run First

### Problem

A batch script can accidentally rewrite production data before its behavior is
understood.

### Method

Every mutating script has two modes:

```text
default: dry-run, read-only
explicit: --apply --yes
```

Before apply, emit:

- planned rows;
- skipped rows;
- rejected rows and reasons;
- rollback or manifest path.

### Boundary

A dry-run proves plan semantics only. It does not prove transactional safety or
concurrent-write behavior.

### Evidence

Retain:

- command;
- input count;
- planned mutation count;
- actual mutation count;
- manifest path;
- rollback path;
- database integrity result.

## 3. Negative Result Gate

### Problem

An agent can generate plausible structured candidates that are mostly wrong.

### Method

Declare the quality threshold before the trial:

```text
method
predicate/category set
minimum output
human sample size
minimum precision
```

If the result misses the threshold:

```text
do not write production
retain candidate artifact
retain human-review table
mark method deferred
```

### Boundary

A failed trial does not prove the method is impossible forever. It only proves
that this method, prompt, data representation, and threshold combination is not
safe for production.

### Evidence

Retain:

- candidate count;
- human sample count;
- correct count;
- precision;
- threshold;
- production write count, normally zero.

Public case pattern:
[`docs/cases/negative-result-gate.md`](cases/negative-result-gate.md).

## 4. Human-Sample Semantic Gate

### Problem

Mechanical gates can verify form but not meaning.

### Method

Use a two-layer process:

```text
machine pre-label
→ stratified human sample
→ measured agreement/precision
→ explicit apply decision
```

The sample should cover:

- each label/category;
- hard or borderline cases;
- low-frequency categories;
- failure-prone source domains.

### Boundary

Sampling estimates quality; it does not prove every unsampled item. If sample
precision is marginal, increase the sample or reject the batch.

### Evidence

Retain:

- model and prompt version;
- label distribution;
- human sample IDs;
- per-category agreement;
- apply/reject decision;
- manifest path.

## 5. Source Purity View

### Problem

A knowledge graph mixes authoritative literature, research output, generated
discoveries, and auto-generated objects. Users may mistake generated proximity
for authoritative evidence.

### Method

Expose an explicit source selector:

```text
literature
research
discovery
auto-research
all
```

Cache by source key, and validate:

```text
requested source = response source
no cross-source leakage
invalid selector falls back to a safe default
```

### Boundary

Source purity is not semantic correctness. A literature-only view still needs
exact evidence and semantic review.

### Evidence

Retain per-view checks for:

- node count;
- link count;
- non-target source count;
- fallback behavior;
- cache key.

## 6. Dual-Host Parity

### Problem

Two runtime hosts can drift after one receives a knowledge-base migration or
repair.

### Method

Use a five-step contract:

```text
1. hot backup
2. integrity check
3. schema/table parity plan
4. controlled swap
5. readback metrics
```

Preserve:

- rollback position;
- user-data exclusion proof;
- source/target checksums;
- count parity by table.

### Boundary

Data parity does not imply identical runtime code or identical operational
event history. Track deployment commit and observability events separately.

### Evidence

Retain:

- per-table counts;
- document/chunk/evidence counts;
- checksums for large binary artifacts;
- user-data counts;
- rollback path;
- health and deployment verification.

## 7. Natural-Reuse Observation

### Problem

A controlled experiment can prove that an asset can be selected and accepted,
but that does not prove a later normal workflow will naturally choose it.

### Method

Separate the observation stages:

```text
controlled activation
→ cohort cutoff
→ later non-controlled workflow
→ natural selection event
→ accepted material use
```

Exclude controlled project IDs and experimental config families from the later
cohort. Record both selection and accepted material use; do not infer reuse from
stock or invocation counts alone.

### Boundary

A zero-use cohort is a negative observation, not proof that the asset is
useless. A highly concentrated cohort should not be generalized to all workflow
families.

### Evidence

Retain:

- cohort cutoff;
- target asset IDs;
- controlled-project exclusions;
- eligible workflow count;
- natural selection rows;
- accepted material-use rows;
- workflow/config/source distribution;
- creation-time concentration.

## 8. Runtime Identity

### Problem

A health endpoint can report success while the process, code, artifact, data, or
served model differs from the intended runtime.

### Method

Bind runtime identity before attributing output:

```text
target commit
actual commit
process start time
health version
artifact hash
table parity
rollback path
requested model
served model
provider
```

### Boundary

Runtime identity proves provenance. It does not prove semantic correctness,
output quality, or business value.

### Evidence

Retain:

- target/actual commit comparison;
- process start timestamp;
- frontend artifact hash;
- table counts or checksums;
- rollback position;
- requested and served model fields;
- provider/base URL;
- deployment verification result.

## 9. Bounded Expansion Tiering

### Problem

An assistant often needs to move beyond the supplied course or task context,
but unbounded expansion can convert inference into false authority.

### Method

Label every expansion tier:

```text
course/task seed
→ canonical reference or theory whitelist
→ evidence-backed external expansion
→ question-only fallback
```

Unsupported statements must remain questions rather than conclusions.

### Boundary

Tiering improves provenance and reviewability. It does not by itself prove
teaching effectiveness or user value.

### Evidence

Retain:

- seed context identifier;
- canonical/theory references;
- external evidence identifiers;
- unsupported statements;
- question-only fallbacks;
- reviewer or teacher decision where available.

## Use in an Audit Policy

These cards can be represented in policy as required checks:

```text
exact_evidence_required
production_write_requires_explicit_apply
human_precision_threshold
natural_reuse_requires_uncontrolled_selection
negative_result_gate
source_purity_required
host_parity_required
runtime_identity_required
bounded_expansion_tiering_required
rollback_manifest_required
```

The important design rule is that a passing check should leave enough evidence
for a later non-author to reproduce the decision from artifacts.

The design-level successor to this list is
[`../policy-candidates-v0.json`](../policy-candidates-v0.json), which names the
checks, required inputs, thresholds, and fail-closed behavior. It is not yet an
executable policy.
