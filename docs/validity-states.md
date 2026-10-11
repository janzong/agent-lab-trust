# Validity States and the Absent-Zero Rule

## Scope

This note defines the three validity states used by `agent-lab-trust` and the
measurement rule that motivated them. It is written for tool builders and
specification authors who need to decide when a number may be reported at all.

## Three states

Every measured outcome is one of exactly three states:

1. **valid** — the measurement was executed and its preconditions held.
2. **invalid** — the measurement was executed and a declared check failed.
3. **unknown-or-unattributable** — the event required for the measurement was
   absent, blocked, or cannot be attributed to this subject.

The third state is mandatory. Collapsing it into either of the other two
produces a silent error: an absent event is rendered as a confident `0`, or an
unattributable effect is rendered as a confirmed result.

## The absent-zero rule

> **An absent event must be reported as unknown, never as zero.**

A counter may report `0` only when the counter was actually evaluated for the
subject and observed no matching events. If the recording path was never
reached — the field was never populated, the call site never passed the
identifier, or the attribution cannot be resolved — the correct value is
unknown, not zero.

This rule is about measurement semantics, not arithmetic. Summing an unknown
with known values must yield unknown; dashboards and downstream consumers must
propagate it or refuse to display a number.

## Sanitized incident used in discussions

A research-reporting system reused one boolean-like field for two meanings:
workflow state ("this item was converted into a task") and consumption
measurement ("this item was cited by an output"). Reports had accumulated
thousands of citations, but the consumption side recorded zero because the
citation path never wrote to that field. Dashboards and prioritization read the
confident zero as "never used".

The fix separated the two concerns:

- a dedicated citation event ledger with per-output identifiers;
- every consumption call site passes those identifiers, including paths where
  other outputs are empty;
- red-first regression tests, including malformed-input tolerance;
- independent recomputation before deployment.

## Billing mapping

The same triad appears independently in billing semantics:

| Measurement | Billing |
|---|---|
| valid | billable |
| invalid | non-billable |
| unknown-or-unattributable | unattributable |

The shared failure mode is identical: one field carrying both a workflow
decision and a measurement silently deletes the third state.

## Implementation guidance

1. Never derive a usage count from a workflow-status field.
2. Record explicit events with stable subject identifiers.
3. Distinguish `no events observed` from `event stream not present`.
4. Propagate unknown through aggregation; do not coerce it to zero.
5. Write the failing test first for the absent case before fixing the ledger.
