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
    required = payload.get("required_artifacts")
    if required is not None:
        if not isinstance(required, list) or any(not isinstance(item, str) or not item for item in required):
            raise PolicyError("required_artifacts must be a list of non-empty strings")
    mode = payload.get("required_artifacts_mode", "all")
    if mode not in ("all", "any"):
        raise PolicyError("required_artifacts_mode must be 'all' or 'any'")
    return payload


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _required_artifacts(policy: Mapping[str, Any]) -> tuple[list[str], str]:
    if "required_artifacts" in policy:
        return list(policy["required_artifacts"]), str(policy.get("required_artifacts_mode", "all"))
    if policy.get("require_structured_artifact", True):
        return ["output/structured.json", "results/structured.json"], "any"
    return [], "all"


def _artifact_check(run_dir: Path, artifacts: list[str], mode: str) -> tuple[bool, list[str], list[str]]:
    present: list[str] = []
    missing: list[str] = []
    for relative in artifacts:
        candidate = run_dir / relative
        if candidate.is_file() and candidate.stat().st_size > 0:
            present.append(relative)
        else:
            missing.append(relative)
    if mode == "any":
        return bool(present), present, missing
    return not missing, present, missing


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
    artifacts, artifact_mode = _required_artifacts(policy)

    for run in runs:
        run_dir = root / run.source_dir
        artifact_ok, present, missing = _artifact_check(run_dir, artifacts, artifact_mode)
        if not artifact_ok:
            findings.append(
                {"code": "missing_artifact", "run_id": run.run_id, "missing": missing, "present": present}
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
        "required_artifacts": artifacts,
        "required_artifacts_mode": artifact_mode,
    }
    result["audit_hash"] = hashlib.sha256(_canonical(result).encode("utf-8")).hexdigest()
    return result
