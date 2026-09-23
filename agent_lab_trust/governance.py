"""Policy-as-code governance audit for agent-lab-trust."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from agent_lab_trust.adapters.gen_mentor import GenMentorAdapter


class PolicyError(ValueError):
    """Raised when a governance policy file is invalid."""


def load_policy(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PolicyError(f"cannot read policy: {path}") from exc
    if not isinstance(payload, dict):
        raise PolicyError("policy must be a JSON object")
    for key in ("max_cost_usd", "max_calls"):
        if key in payload and not isinstance(payload[key], (int, float)):
            raise PolicyError(f"{key} must be numeric")
    markers = payload.get("forbidden_markers", [])
    if not isinstance(markers, list) or any(not isinstance(marker, str) for marker in markers):
        raise PolicyError("forbidden_markers must be a list of strings")
    return payload


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _marker_hits(root: Path, markers: list[str]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    if not markers:
        return hits
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        try:
            if path.stat().st_size > 2_000_000:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for marker in markers:
            if marker in text:
                hits.append({"path": str(path.relative_to(root)), "marker": marker})
    return hits


def audit_root(root: Path, policy: Mapping[str, Any]) -> dict[str, Any]:
    root = Path(root)
    runs = GenMentorAdapter().discover(root)
    findings: list[dict[str, Any]] = []

    for run in runs:
        if policy.get("require_structured_artifact", True) and not run.success:
            findings.append(
                {"code": "missing_artifact", "run_id": run.run_id, "detail": run.error or "not valid"}
            )
        cost = run.metrics.cost_usd
        max_cost = policy.get("max_cost_usd")
        if cost is not None and max_cost is not None and cost > float(max_cost):
            findings.append(
                {"code": "cost_exceeded", "run_id": run.run_id, "cost_usd": cost, "max_cost_usd": max_cost}
            )
        calls = run.metrics.calls
        max_calls = policy.get("max_calls")
        if calls is not None and max_calls is not None and calls > int(max_calls):
            findings.append(
                {"code": "calls_exceeded", "run_id": run.run_id, "calls": calls, "max_calls": max_calls}
            )

    for hit in _marker_hits(root, list(policy.get("forbidden_markers", []))):
        findings.append({"code": "forbidden_marker", "path": hit["path"], "marker": hit["marker"]})

    result = {
        "runs": len(runs),
        "findings": findings,
        "passed": not findings,
        "policy_keys": sorted(policy),
    }
    result["audit_hash"] = hashlib.sha256(_canonical(result).encode("utf-8")).hexdigest()
    return result
