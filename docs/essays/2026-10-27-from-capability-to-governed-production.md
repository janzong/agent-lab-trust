# From Capability to Governed Production: A Minimal Theory of AI Agent Systems

> Draft: 2026-10-27  
> Status: public theory draft  
> Related artifacts: [method cards](../method-cards-20261026.md) · [policy
candidates](../policy-candidates-v0.md)

## Abstract

The dominant AI-agent narrative is capability-centered: agents can code,
search, browse, call tools, plan, and execute long tasks. Capability alone,
however, does not make a production system. An agent becomes production-grade
only when its outputs, assets, failures, environments, model identities, and
human decisions can be audited and compounded.

This essay proposes a minimal theory of governed agent production. Its central
claim is that the decisive transition is not from less automation to more
automation, but from capability accumulation to governance structure:

```text
tool use
→ workflow automation
→ governed production
→ evidence-addressable organizational capability
```

Six mechanisms define the minimal structure:

```text
evidence chain
human semantic gate
negative-result gate
asset reproduction
deployment and model identity
bounded expansion
```

Together they answer a question that capability benchmarks do not:

> Why should the next run, the next worker, or the next reviewer trust—and
> safely reuse—what this agent system produced?

## 1. The capability trap

An agent that writes a report, finds a document, or modifies a repository is
still only demonstrating a capability. A production system must answer broader
questions:

- Which source supports this sentence?
- Which model actually served the request?
- Which code and data were live?
- Who reviewed meaning, and against what sample?
- What happens when a candidate misses a preregistered threshold?
- Can a later workflow reuse the accepted asset without a controlled prompt?
- Can the operation be rolled back?

Without those answers, impressive local behavior remains operationally
opaque. It may be useful as an assistant, but it is not yet an organizational
production system.

## 2. Six subsystems of agent production

A governed agent production system has six interlocking subsystems.

### 2.1 Task process

Production work is not one prompt. It is a labor process:

```text
intention
→ context assembly
→ tool action
→ generation
→ verification
→ human semantic review
→ delivery
→ asset recovery
```

The system is only as trustworthy as its weakest transition.

### 2.2 Means of production

Its durable means include:

- knowledge sources;
- evidence spans;
- claims and insights;
- policies;
- charters;
- tests;
- manifests;
- rollback records;
- deployment events;
- accepted reports and teaching materials.

These are not interchangeable. An authoritative claim, a report-derived
insight, a critique, an unverified discovery, and a question-only expansion
belong in different tiers.

### 2.3 Tool boundary

Tools are production relations, not merely features. Each integration needs:

```text
allowed caller
read scope
write scope
failure behavior
audit event
disable or rollback path
```

A plugin marketplace without those controls expands capability while reducing
operational knowledge.

### 2.4 Human organization

Humans should not merely "review at the end." They govern meaning, value,
authority, risk, and responsibility. Machines can verify form; humans must
sample and judge semantics.

### 2.5 Runtime environment

Outputs are produced by a particular combination of:

- code commit;
- database schema and data snapshot;
- model and provider;
- process start time;
- deployment target;
- artifact hashes.

Runtime identity is therefore part of output truth.

### 2.6 Reproduction

A production system compounds only when accepted assets are naturally selected
and materially used by later uncontrolled workflows. Controlled activation is
necessary evidence, but it is not natural reuse.

## 3. Evidence chain: trust is addressable, not rhetorical

The first mechanism is an exact evidence chain:

```text
citable object
⇒ authorized source object
⇒ verified evidence span
⇒ quote reproduced at the recorded offset
⇒ current chunk covers the interval
⇒ source is published
```

This turns "the model cited a source" into a set of checkable facts:

- what source;
- which version;
- where the quote starts and ends;
- which current chunk covers it;
- why the object is authorized;
- who or what verified it.

The boundary is essential: an exact evidence chain proves source existence and
reproducibility, not semantic fit. A real quote may still fail to support the
sentence around it. That next question belongs to the human semantic gate.

## 4. Human semantic gate: form is not meaning

Mechanical gates are excellent at form:

- offset validity;
- schema conformance;
- uniqueness;
- source status;
- threshold presence;
- test result.

They are insufficient for meaning:

- Is this a concept rather than an institution, event, policy, or sentence
  fragment?
- Is this relation true in the direction claimed?
- Does this source support this use?
- Is this output useful to the receiving practice?

A human semantic gate is therefore not optional human polish. It is a
production relation:

```text
machine pre-label
→ stratified human sample
→ measured precision or agreement
→ preregistered threshold
→ apply, reject, or increase sample
→ preserve sample and manifest
```

This creates a new kind of labor division. Machines compress inspection scale;
humans govern meaning and consequence; governance preserves the evidence needed
to understand the decision later.

## 5. Negative-result gate: rejection as productive capital

Most product narratives treat rejected work as waste. In governed production,
a preserved negative result can be more valuable than a plausible unsafe write.

A negative-result gate has this form:

```text
preregister method and threshold
→ generate candidates
→ human sample
→ measure precision
→ if below threshold: retain artifacts, write zero rows, mark deferred
```

The production case behind the method cards generated 308 candidate graph
relations. Human review found 10 of 50 sampled candidates correct: 20 percent
precision against an 80 percent threshold. The gate wrote zero production
relations.

That rejection produced five forms of capital:

1. **Pollution prevention** — an unreliable graph did not enter production.
2. **Boundary knowledge** — the system learned where the method failed.
3. **Comparative evidence** — a future method can be compared with the failed
   candidate set.
4. **Recovery cost avoidance** — no later cleanup of thousands of false edges
   was required.
5. **Trust** — users can see that the system prefers a truthful gap to a
   fabricated sense of completeness.

The boundary remains: a failed trial does not prove the method is permanently
impossible. It rejects one method, representation, prompt, evidence binding,
and threshold combination.

## 6. Asset reproduction: controlled adoption is not compound growth

Agent systems often claim that assets make them "better with use." That claim
needs a stricter chain:

```text
stock
→ review and mapping
→ controlled activation
→ human acceptance
→ later normal workflow
→ natural selection
→ accepted material use
→ asset reproduction
```

Controlled activation proves that an asset can be selected and can satisfy an
experimental workflow. It does not prove natural reuse. Natural reproduction
requires later, uncontrolled work to select the asset and an accepted output to
use it materially.

This distinction prevents a common overclaim:

```text
successful experiment ≠ natural reuse ≠ causal productivity gain
```

Even natural reuse is not proof of quality by itself; it is evidence that the
asset became part of a living production process.

## 7. Deployment and model identity

A healthy endpoint is not the same thing as a known runtime.

Deployment identity should bind:

```text
endpoint alias
target commit
actual commit
health version
process start time
artifact hash
table counts or checksums
rollback position
```

This principle—**health is not identity**—addresses a familiar failure: a
service reports the expected version while the process predates a code change,
a working tree contains dirty files, or a secondary environment has stale data.

Model identity has the same structure:

```text
requested model
served model
provider
base URL
input hash
output hash
token usage
```

**Requested is not served.** A stable request alias can silently route to a new
served model. Without provider-returned identity, attribution drifts.

## 8. Bounded expansion: seeds, not walls

Agent usefulness often requires going beyond the supplied context: a teacher
wants a course to connect with broader theory; a researcher wants a document to
connect with prior findings. Yet unbounded expansion turns inference into
false authority.

A bounded expansion layer separates:

```text
course or task seed
→ whitelisted theory or canonical references
→ evidence-backed external expansion
→ question-only fallback
```

The rule is:

> The agent may expand perspective, but unsupported inference may become a
> question, not a conclusion.

This is not a limitation on usefulness; it is what makes expansion reviewable.

## 9. Production-theory reading

Seeing agent systems through production theory changes the vocabulary.

| Dimension | Governance question |
|---|---|
| Instruments | Which models, retrievers, harnesses, and tools are involved? |
| Labor process | How is work divided across generation, checking, and review? |
| Means of production | Which knowledge assets and environments are required? |
| Relations of production | Who may read, write, deploy, accept, reject, or roll back? |
| Reproduction | Which accepted assets enter later work without being forced? |
| Failure | Which rejected trials are retained as boundaries? |

Agent charters and policies are therefore not documentation niceties. They are
explicit representations of production relations.

## 10. Comparison with the frontier

Current frontier systems are productizing mechanisms such as permissions,
sandboxes, audit events, context retention, plugin boundaries, cloud
environments, safety telemetry, remote control, and model selection. Those
mechanisms matter, but they are only part of the production transition.

The complementary question is organizational:

```text
external system: does the mechanism exist?
production system: does the mechanism change accepted work under audit?
public charter corpus: do written rules become executable?
```

A mature account needs all three layers: product capability, governed
production, and public ecological change.

## 11. Policy candidates

The method cards and this theory point toward named, fail-closed checks:

```text
exact_evidence_required
dry_run_required
negative_result_gate
human_precision_threshold
source_purity_required
host_parity_required
rollback_manifest_required
```

The policy candidates are design-only in the current validator. They are the
bridge from theory to executable governance:

```text
concept
→ method card
→ named check
→ required inputs
→ threshold or artifact contract
→ fail-closed behavior
```

## 12. Research agenda

This line suggests at least nine research questions:

1. How should evidence-addressability be defined for agent outputs?
2. What is the optimal division between mechanical gates and human semantic
   gates?
3. Do negative-result gates reduce long-run contamination and cleanup costs?
4. How can controlled activation and natural asset reuse be separated
   formally?
5. Which fields constitute minimal deployment identity?
6. Which organizational indicators make asset reproduction comparable?
7. Under what conditions do prose charters become executable policy?
8. How should plugin permission, audit, rollback, and review be co-designed?
9. How should human sample size, cost, and error tolerance be traded off?

## 13. Non-claims

This is a grounded theory draft, not a universal causal result.

It does not claim that:

- exact source existence proves semantic support;
- passing tests proves business productivity;
- controlled adoption proves natural reuse;
- a rejected trial proves a method is impossible;
- health proves runtime identity;
- evidence provenance proves user value.

## 14. Conclusion

Capability asks what an agent can do. Governed production asks why the next
run, reviewer, and organization can safely depend on what it did.

The minimal theory proposed here is:

```text
evidence chain
+ human semantic gate
+ negative-result gate
+ asset reproduction
+ deployment/model identity
+ bounded expansion
= governed agent production
```

When these mechanisms are observable, fail-closed, and reusable, an agent
system stops being only a clever tool and becomes a production system capable
of accumulating trust.
