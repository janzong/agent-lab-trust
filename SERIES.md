# The agent trust series

Write it down → test it → govern it.

| Piece | Question | Artifact |
|---|---|---|
| **1. Write it down** | What do people actually tell agents? | `agent-charters`: corpus, tools, and external readers for AGENTS.md / CLAUDE.md — <https://github.com/janzong/agent-charters> · <https://gitee.com/janzong/agent-charters> |
| **2. Test it** | Do agents actually behave as claimed? | `agent-lab-trust`: validate runs, hashed reports, deletion proof, one-command reproduction, Docker image — <https://github.com/janzong/agent-lab-trust> · <https://gitee.com/janzong/agent-lab-trust> |
| **3. Govern it** | How do we constrain, audit, and prove effect? | `agent-lab-trust audit <root> --policy policy.example.json`: policy-as-code checks for cost/call caps, structured artifacts, forbidden markers, and a canonical `audit_hash`; `deletion-proof --output` writes the deletion proof for the same policy flow. |

Underlying method package: <https://github.com/janzong/agent-lab-method>.

## Reproduce

```bash
docker run --rm ghcr.io/janzong/agent-lab-trust@sha256:9f9428557933004514ec6b54988fc3668071e1b73f87e0c3ac2e04ba4536f3a0
```

or `bash scripts/reproduce.sh`.

Expected: `13 passed` under both `TZ=UTC` and `TZ=Asia/Shanghai`, `report_hash` `a841b192981fd7e7`, deletion `audit_hash` `4f0193abbd49a0f9`.

## Independent reproductions

The trust layer is looking for 3 non-author reproductions: <https://github.com/janzong/agent-lab-trust/issues/1>.

## Non-claims

Synthetic evidence only. No real learner data, no RMAS integration, and no cross-task transfer claim.
