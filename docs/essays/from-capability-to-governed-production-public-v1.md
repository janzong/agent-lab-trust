# From Capability to Governed Production

> Status: `ready_for_human_review`  
> Draft: 2026-10-27  
> Companion artifacts: [method cards](../method-cards-20261026.md) · [policy
 candidates](../policy-candidates-v0.md)

## The failure that capability scores miss

An agent can produce a paragraph with four plausible citations, run a test
suite, call a web tool, and still fail as a production system. The cited titles
can be real while the passages do not support the claims. The tests can pass
while the deployed process predates the code that was just checked out. The tool
call can succeed while leaving no auditable reason to trust its consequence. A
model can even be requested under one name and silently served under another.

These are not edge cases. They are the ordinary gaps between:

```text
what an agent can do
and
what an organization can safely depend on later
```

The question that matters in production is therefore not only, “What can this
agent do?” It is:

> Why should the next run, reviewer, or workflow trust, reproduce, reject, or
 reuse what this agent system just did?

That question motivates a minimal theory of governed agent production.

## From tool to production system

Agent deployments progress through three rough stages:

```text
tool use
→ workflow automation
→ governed production
```

**Tool use** performs an action: search, write, patch, call an API, or summarize
a document.

**Workflow automation** repeats a procedure and may coordinate tools.

**Governed production** makes the procedure organizationally durable:

- outputs carry provenance;
- assets accumulate under review;
- failures can block production writes;
- human semantic responsibility is explicit;
- runtime identity is checkable;
- accepted work can be reused without a hidden prompt forcing it.

Feature count does not cause this transition. Governance structure does.

## Six subsystems

A useful production-theory view separates six subsystems.

1. **Task process** — intention, context, action, generation, verification,
   human review, delivery, and asset recovery.
2. **Means of production** — sources, evidence, claims, policies, tests,
   manifests, rollback records, and accepted materials.
3. **Tool boundary** — caller identity, read/write scope, failure behavior,
   audit event, disable path, and rollback path.
4. **Human organization** — semantic sampling, approval, risk ownership, and
   responsibility.
5. **Runtime environment** — code commit, data snapshot, model identity,
   process start time, artifact hashes, and endpoint parity.
6. **Reproduction** — whether later uncontrolled workflows naturally select and
   materially use accepted assets.

These subsystems turn an agent from a local capability into a production
relation.

## 1. Trust is a chain, not a score

The first mechanism is an exact evidence chain:

```text
citable object
⇒ authorized source
⇒ verified evidence span
⇒ quote reproduced at a recorded offset
⇒ current chunk covers the interval
⇒ source is published
```

This replaces “the model cited a source” with questions a system can answer:

```text
which source
which version
where the quote begins and ends
which current chunk covers it
who or what verified it
why the object is authorized
```

A real title is not evidence support. A semantically similar passage is not an
exact quote. A quote in an obsolete chunk is not current provenance.

The boundary is equally important: an exact chain does not prove that the quote
supports the sentence around it. That requires semantic judgment.

## 2. Machines govern form; humans govern meaning

Mechanical gates are excellent at form:

- offset correctness;
- schema conformance;
- uniqueness;
- source status;
- threshold presence;
- test outcome.

They cannot decide:

- whether a label is a concept, institution, event, policy, or sentence fragment;
- whether a relation points in the right direction;
- whether a source supports this use;
- whether an output is valuable enough to accept.

A governed system therefore uses a **human semantic gate**:

```text
machine pre-label
→ stratified human sample
→ measured precision or agreement
→ preregistered threshold
→ apply, reject, or increase the sample
→ retain sample and manifest
```

Human review is not a nostalgic leftover. It becomes a measurable production
station. Machines compress inspection scale; humans govern meaning and
consequence; governance preserves the evidence needed to review the decision
later.

## 3. Negative results are production capital

Most demonstrations celebrate acceptance. Production systems also need the
ability to reject.

The production case behind the method cards generated 308 candidate typed graph
relations. A preregistered human sample found 10 of 50 candidates correct: 20
percent precision against an 80 percent threshold. The result was retained, but
the production graph received zero relations.

That rejection produced value:

1. it prevented a mostly wrong graph from entering production;
2. it recorded a quality boundary;
3. it retained candidate and review artifacts for future comparison;
4. it avoided a later cleanup campaign;
5. it made the system’s refusal observable.

The boundary matters: a failed trial does not prove typed relations are forever
impossible. It rejects one method, representation, prompt, evidence binding, and
threshold combination.

The general principle is:

> A governed agent system earns trust not only by shipping successful output,
> but by preserving and enforcing rejected work.

## 4. Controlled adoption is not asset reproduction

Agent systems often claim to improve with use. That claim needs a stricter
chain:

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
experimental workflow. It does not prove natural reuse.

Natural reproduction requires a later, uncontrolled workflow to choose the
asset, and an accepted output to use it materially. Even then, reuse is not
proof of causal productivity improvement. It is evidence that the asset became
part of a living production process.

This distinction prevents an attractive overclaim:

```text
successful experiment ≠ natural reuse ≠ productivity gain
```

## 5. Health is not identity

A health endpoint saying `"ok"` does not prove which runtime produced a result.
Runtime identity should bind:

```text
endpoint alias
target commit
actual commit
health version
process start time
frontend artifact hash
table counts or checksums
rollback position
```

Without those facts, a healthy endpoint can conceal:

- a process started before a later code commit;
- dirty working files;
- an artifact mismatch;
- stale secondary data;
- a partially completed deployment.

Model identity has the same shape:

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
model version. Logs that record only the request alias misattribute every
affected run.

## 6. Seeds, not walls

Useful agents often need to move beyond supplied context. A teaching assistant
should connect a course to broader theory. A research assistant should connect
a document to earlier findings. Yet unbounded expansion converts inference into
false authority.

A bounded expansion layer separates:

```text
course or task seed
→ whitelisted theory or canonical reference
→ evidence-backed external expansion
→ question-only fallback
```

The rule is:

> Unsupported expansion may become a question, not a conclusion.

This preserves usefulness while making expansion reviewable.

## A production-theory reading

Seeing agents as production systems changes the vocabulary:

| Dimension | Governance question |
|---|---|
| Instruments | Which models, retrievers, harnesses, and tools participate? |
| Labor process | How is work divided across generation, checking, and review? |
| Means of production | Which sources, assets, and environments are required? |
| Relations of production | Who may read, write, deploy, accept, reject, or roll back? |
| Reproduction | Which accepted assets enter later work without being forced? |
| Failure | Which rejected trials are retained as boundaries? |

Agent charters and policies are not documentation decorations. They are explicit
representations of production relations.

## Toward executable policy

These concepts can become named checks rather than slogans:

```text
exact_evidence_required
dry_run_required
negative_result_gate
human_precision_threshold
source_purity_required
host_parity_required
rollback_manifest_required
```

Each check needs required inputs, a threshold or artifact contract, and
fail-closed behavior. The current policy candidates are design-only, but they
mark the path from theory to executable governance.

## Non-claims

This theory is grounded in one production research practice and generalized
through method cards; it is not a universal causal result.

It does not claim that:

- exact source existence proves semantic support;
- passing tests proves business productivity;
- controlled adoption proves natural reuse;
- a rejected trial proves a method is impossible;
- health proves runtime identity;
- provenance proves user value.

## Conclusion

Capability asks what an agent can do once. Governed production asks why the
next run, reviewer, and organization can safely depend on what it did.

The minimal structure is:

```text
evidence chain
+ human semantic gate
+ negative-result gate
+ asset reproduction
+ deployment/model identity
+ bounded expansion
= governed agent production
```

When these mechanisms are observable and fail-closed, an agent system becomes
more than a clever tool. It becomes a production system capable of accumulating
trust.
