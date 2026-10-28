"""Input-first evaluator for the executable v0 policy candidates."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping


class PolicyEvaluationError(ValueError):
    """Raised when a policy candidate or evidence document is invalid."""


IMPLEMENTED_CHECKS = {
    "exact_evidence_required",
    "dry_run_required",
    "negative_result_gate",
    "human_precision_threshold",
    "source_purity_required",
    "host_parity_required",
    "rollback_manifest_required",
    "natural_reuse_requires_uncontrolled_selection",
    "runtime_identity_required",
    "bounded_expansion_tiering_required",
}


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def load_policy_candidates(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PolicyEvaluationError(f"cannot read policy candidates: {path}") from exc
    if not isinstance(payload, dict):
        raise PolicyEvaluationError("policy candidates must be an object")
    if payload.get("schema_version") != 0:
        raise PolicyEvaluationError("policy candidates schema_version must be 0")
    checks = payload.get("checks")
    if not isinstance(checks, list) or not checks:
        raise PolicyEvaluationError("policy candidates checks must be a non-empty list")
    ids: set[str] = set()
    for check in checks:
        if not isinstance(check, dict) or not check.get("id"):
            raise PolicyEvaluationError("each policy candidate requires an id")
        if check["id"] in ids:
            raise PolicyEvaluationError(f"duplicate policy candidate: {check['id']}")
        ids.add(check["id"])
    return payload


def _require_int(check: Mapping[str, Any], field: str) -> int:
    value = check.get(field)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise PolicyEvaluationError(f"{field} must be a non-negative integer")
    return value


def _evaluate_negative_result_gate(check: Mapping[str, Any], evidence: Mapping[str, Any]) -> dict[str, Any]:
    candidate_count = _require_int(evidence, "candidate_count")
    sample_count = _require_int(evidence, "human_sample_count")
    correct_count = _require_int(evidence, "correct_count")
    write_count = _require_int(evidence, "production_write_count")
    if sample_count == 0:
        raise PolicyEvaluationError("human_sample_count must be positive")
    if correct_count > sample_count:
        raise PolicyEvaluationError("correct_count cannot exceed human_sample_count")
    threshold = float(check["threshold"]["minimum"])
    precision = round(correct_count / sample_count, 6)
    blocked = precision < threshold
    if blocked and write_count != 0:
        return {
            "id": check["id"],
            "result": "fail",
            "reason": "failed precision wrote production rows",
            "candidate_count": candidate_count,
            "human_sample_count": sample_count,
            "correct_count": correct_count,
            "precision": precision,
            "threshold": threshold,
            "production_write_count": write_count,
        }
    return {
        "id": check["id"],
        "result": "pass",
        "reason": "failed precision blocked production write" if blocked else "precision met threshold",
        "candidate_count": candidate_count,
        "human_sample_count": sample_count,
        "correct_count": correct_count,
        "precision": precision,
        "threshold": threshold,
        "production_write_count": write_count,
    }


def _evaluate_exact_evidence(check: Mapping[str, Any], evidence: Mapping[str, Any]) -> dict[str, Any]:
    required_text = ["asset_id", "quote", "chunk_id", "source_status"]
    for field in required_text:
        if not isinstance(evidence.get(field), str) or not evidence[field].strip():
            raise PolicyEvaluationError(f"{field} must be a non-empty string")
    source_sha = evidence.get("source_sha")
    if not isinstance(source_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", source_sha):
        raise PolicyEvaluationError("source_sha must be 64 lowercase hex characters")
    flags = [
        evidence.get("quote_verified"),
        evidence.get("offset_valid"),
        evidence.get("chunk_current"),
    ]
    if any(not isinstance(flag, bool) for flag in flags):
        raise PolicyEvaluationError("evidence verification flags must be booleans")
    published = evidence["source_status"] == "published"
    verified = published and all(flags)
    return {
        "id": check["id"],
        "result": "pass" if verified else "fail",
        "reason": "exact evidence verified" if verified else "exact evidence not current or verified",
        "asset_id": evidence["asset_id"],
        "chunk_id": evidence["chunk_id"],
        "source_status": evidence["source_status"],
        "quote_verified": evidence["quote_verified"],
        "offset_valid": evidence["offset_valid"],
        "chunk_current": evidence["chunk_current"],
    }


def _evaluate_human_precision(check: Mapping[str, Any], evidence: Mapping[str, Any]) -> dict[str, Any]:
    sample_count = _require_int(evidence, "sample_count")
    agreement_count = _require_int(evidence, "agreement_count")
    if agreement_count > sample_count:
        raise PolicyEvaluationError("agreement_count cannot exceed sample_count")
    threshold = check["threshold"]
    minimum = float(threshold["minimum"])
    minimum_sample = int(threshold.get("minimum_sample", 1))
    precision = round(agreement_count / sample_count, 6) if sample_count else 0.0
    if sample_count < minimum_sample:
        result, reason = "fail", "sample below minimum"
    elif precision < minimum:
        result, reason = "fail", "precision below threshold"
    else:
        result, reason = "pass", "precision met threshold"
    return {
        "id": check["id"],
        "result": result,
        "reason": reason,
        "sample_count": sample_count,
        "agreement_count": agreement_count,
        "precision": precision,
        "threshold": minimum,
        "minimum_sample": minimum_sample,
    }


def _evaluate_rollback_manifest(check: Mapping[str, Any], evidence: Mapping[str, Any], root: Path) -> dict[str, Any]:
    rollback_path = evidence.get("rollback_path")
    manifest_path = evidence.get("manifest_path")
    if not isinstance(rollback_path, str) or not rollback_path:
        raise PolicyEvaluationError("rollback_path must be a non-empty string")
    if not isinstance(manifest_path, str) or not manifest_path:
        raise PolicyEvaluationError("manifest_path must be a non-empty string")

    def present(relative: str) -> bool:
        path = Path(relative)
        resolved = path if path.is_absolute() else root / path
        return resolved.is_file() and resolved.stat().st_size > 0

    rollback_present = present(rollback_path)
    manifest_present = present(manifest_path)
    if not rollback_present:
        result, reason = "fail", "rollback file missing or empty"
    elif not manifest_present:
        result, reason = "fail", "manifest file missing or empty"
    else:
        result, reason = "pass", "rollback and manifest present"
    return {
        "id": check["id"],
        "result": result,
        "reason": reason,
        "rollback_path": rollback_path,
        "manifest_path": manifest_path,
        "rollback_present": rollback_present,
        "manifest_present": manifest_present,
    }


def _evaluate_natural_reuse(check: Mapping[str, Any], evidence: Mapping[str, Any]) -> dict[str, Any]:
    claimed = evidence.get("claimed_natural_reuse")
    if not isinstance(claimed, bool):
        raise PolicyEvaluationError("claimed_natural_reuse must be a boolean")
    cohort_cutoff = evidence.get("cohort_cutoff")
    if not isinstance(cohort_cutoff, str) or not cohort_cutoff.strip():
        raise PolicyEvaluationError("cohort_cutoff must be a non-empty string")
    exclusions = evidence.get("controlled_project_exclusions")
    if not isinstance(exclusions, list):
        raise PolicyEvaluationError("controlled_project_exclusions must be a list")
    eligible = _require_int(evidence, "eligible_workflow_count")
    selection_rows = _require_int(evidence, "natural_selection_rows")
    accepted_rows = _require_int(evidence, "accepted_material_use_rows")
    if accepted_rows > selection_rows:
        raise PolicyEvaluationError("accepted_material_use_rows cannot exceed natural_selection_rows")
    if not claimed:
        result, reason = "pass", "no natural-reuse claim"
    elif eligible == 0 or selection_rows == 0 or accepted_rows == 0:
        result, reason = "fail", "claimed reuse lacks natural selection or accepted material use"
    else:
        result, reason = "pass", "natural selection and accepted material use present"
    return {
        "id": check["id"],
        "result": result,
        "reason": reason,
        "claimed_natural_reuse": claimed,
        "cohort_cutoff": cohort_cutoff,
        "controlled_project_exclusion_count": len(exclusions),
        "eligible_workflow_count": eligible,
        "natural_selection_rows": selection_rows,
        "accepted_material_use_rows": accepted_rows,
    }


def _evaluate_runtime_identity(check: Mapping[str, Any], evidence: Mapping[str, Any], root: Path) -> dict[str, Any]:
    fields = [
        "target_commit",
        "actual_commit",
        "process_start_time",
        "health_version",
        "artifact_hash",
        "rollback_path",
        "requested_model",
        "served_model",
        "provider",
    ]
    for field in fields:
        if not isinstance(evidence.get(field), str) or not evidence[field].strip():
            raise PolicyEvaluationError(f"{field} must be a non-empty string")
    table_counts = evidence.get("table_counts")
    if not isinstance(table_counts, dict) or not table_counts:
        raise PolicyEvaluationError("table_counts must be a non-empty object")
    rollback = Path(evidence["rollback_path"])
    rollback_path = rollback if rollback.is_absolute() else root / rollback
    if not rollback_path.is_file() or rollback_path.stat().st_size == 0:
        return {
            "id": check["id"],
            "result": "fail",
            "reason": "rollback file missing or empty",
            "target_commit": evidence["target_commit"],
            "actual_commit": evidence["actual_commit"],
        }
    if evidence["target_commit"] != evidence["actual_commit"]:
        return {
            "id": check["id"],
            "result": "fail",
            "reason": "target and actual commit differ",
            "target_commit": evidence["target_commit"],
            "actual_commit": evidence["actual_commit"],
        }
    return {
        "id": check["id"],
        "result": "pass",
        "reason": "runtime identity verified",
        "target_commit": evidence["target_commit"],
        "actual_commit": evidence["actual_commit"],
        "health_version": evidence["health_version"],
        "requested_model": evidence["requested_model"],
        "served_model": evidence["served_model"],
        "provider": evidence["provider"],
    }


def _present(root: Path, relative: str) -> bool:
    path = Path(relative)
    resolved = path if path.is_absolute() else root / path
    return resolved.is_file() and resolved.stat().st_size > 0


def _evaluate_dry_run(check: Mapping[str, Any], evidence: Mapping[str, Any], root: Path) -> dict[str, Any]:
    attempted = evidence.get("production_write_attempted")
    applied = evidence.get("apply_flag")
    recorded = evidence.get("dry_run_recorded")
    for field, value in (
        ("production_write_attempted", attempted),
        ("apply_flag", applied),
        ("dry_run_recorded", recorded),
    ):
        if not isinstance(value, bool):
            raise PolicyEvaluationError(f"{field} must be a boolean")
    plan = evidence.get("plan_artifact")
    manifest = evidence.get("manifest_path")
    if not isinstance(plan, str) or not plan or not isinstance(manifest, str) or not manifest:
        raise PolicyEvaluationError("plan_artifact and manifest_path must be non-empty strings")
    if not attempted:
        return {"id": check["id"], "result": "pass", "reason": "no production write attempted"}
    if not recorded or not applied:
        return {"id": check["id"], "result": "fail", "reason": "production write lacks dry-run record"}
    if not _present(root, plan):
        return {"id": check["id"], "result": "fail", "reason": "dry-run plan missing or empty"}
    if not _present(root, manifest):
        return {"id": check["id"], "result": "fail", "reason": "manifest missing or empty"}
    return {"id": check["id"], "result": "pass", "reason": "dry-run and manifest present"}


def _evaluate_source_purity(check: Mapping[str, Any], evidence: Mapping[str, Any]) -> dict[str, Any]:
    requested = evidence.get("requested_source")
    returned = evidence.get("returned_source")
    if not isinstance(requested, str) or not requested or not isinstance(returned, str) or not returned:
        raise PolicyEvaluationError("requested_source and returned_source must be non-empty strings")
    non_target = _require_int(evidence, "non_target_count")
    fallback = evidence.get("fallback_source")
    if fallback is not None and not isinstance(fallback, str):
        raise PolicyEvaluationError("fallback_source must be a string or null")
    if requested != returned:
        result, reason = "fail", "requested and returned source differ"
    elif non_target != 0:
        result, reason = "fail", "source view contains non-target objects"
    else:
        result, reason = "pass", "source view isolated"
    return {
        "id": check["id"],
        "result": result,
        "reason": reason,
        "requested_source": requested,
        "returned_source": returned,
        "non_target_count": non_target,
        "fallback_source": fallback,
    }


def _evaluate_host_parity(check: Mapping[str, Any], evidence: Mapping[str, Any], root: Path) -> dict[str, Any]:
    groupings = {}
    for field in ("table_counts", "checksums", "user_data_counts"):
        value = evidence.get(field)
        if not isinstance(value, dict) or len(value) < 2:
            raise PolicyEvaluationError(f"{field} must contain at least two hosts")
        groupings[field] = value
    rollback = evidence.get("rollback_path")
    if not isinstance(rollback, str) or not rollback or not _present(root, rollback):
        return {"id": check["id"], "result": "fail", "reason": "rollback file missing or empty"}
    for field, values in groupings.items():
        canonical = {_canonical(value) for value in values.values()}
        if len(canonical) != 1:
            return {"id": check["id"], "result": "fail", "reason": "host parity mismatch"}
    return {"id": check["id"], "result": "pass", "reason": "host parity verified"}


def _evaluate_bounded_expansion(check: Mapping[str, Any], evidence: Mapping[str, Any]) -> dict[str, Any]:
    for field in ("seed_context_id",):
        if not isinstance(evidence.get(field), str) or not evidence[field].strip():
            raise PolicyEvaluationError(f"{field} must be a non-empty string")
    for field in ("canonical_reference_ids", "external_evidence_ids", "unsupported_statements", "question_only_fallbacks"):
        if not isinstance(evidence.get(field), list):
            raise PolicyEvaluationError(f"{field} must be a list")
    unsupported = set(map(str, evidence["unsupported_statements"]))
    fallbacks = set(map(str, evidence["question_only_fallbacks"]))
    if not unsupported <= fallbacks:
        return {
            "id": check["id"],
            "result": "fail",
            "reason": "unsupported statements not converted to questions",
        }
    return {
        "id": check["id"],
        "result": "pass",
        "reason": "expansion tiers preserved",
    }


def evaluate_policy_evidence(
    policy: Mapping[str, Any],
    evidence: Mapping[str, Any],
    *,
    root: Path,
) -> dict[str, Any]:
    if evidence.get("schema_version") != 0:
        raise PolicyEvaluationError("evidence schema_version must be 0")
    evidence_checks = evidence.get("checks")
    if not isinstance(evidence_checks, dict):
        raise PolicyEvaluationError("evidence checks must be an object")
    checks = {check["id"]: check for check in policy.get("checks", [])}
    results: list[dict[str, Any]] = []
    missing_inputs: list[str] = []
    for check_id in sorted(IMPLEMENTED_CHECKS):
        check = checks.get(check_id)
        if check is None:
            raise PolicyEvaluationError(f"policy file does not define {check_id}")
        check_evidence = evidence_checks.get(check_id)
        if not isinstance(check_evidence, dict):
            missing_inputs.append(check_id)
            results.append({
                "id": check_id,
                "result": "fail",
                "reason": "evidence missing",
            })
            continue
        if check_id == "exact_evidence_required":
            result = _evaluate_exact_evidence(check, check_evidence)
        elif check_id == "dry_run_required":
            result = _evaluate_dry_run(check, check_evidence, root)
        elif check_id == "negative_result_gate":
            result = _evaluate_negative_result_gate(check, check_evidence)
        elif check_id == "human_precision_threshold":
            result = _evaluate_human_precision(check, check_evidence)
        elif check_id == "source_purity_required":
            result = _evaluate_source_purity(check, check_evidence)
        elif check_id == "host_parity_required":
            result = _evaluate_host_parity(check, check_evidence, root)
        elif check_id == "rollback_manifest_required":
            result = _evaluate_rollback_manifest(check, check_evidence, root)
        elif check_id == "natural_reuse_requires_uncontrolled_selection":
            result = _evaluate_natural_reuse(check, check_evidence)
        elif check_id == "runtime_identity_required":
            result = _evaluate_runtime_identity(check, check_evidence, root)
        else:
            result = _evaluate_bounded_expansion(check, check_evidence)
        results.append(result)

    unimplemented = sorted(set(checks) - IMPLEMENTED_CHECKS)
    passed = not missing_inputs and all(result["result"] == "pass" for result in results)
    evaluation = {
        "schema_version": 0,
        "passed": passed,
        "implemented_checks": sorted(IMPLEMENTED_CHECKS),
        "unimplemented_checks": unimplemented,
        "missing_inputs": missing_inputs,
        "results": results,
        "policy_sha256": _sha256(policy),
    }
    evaluation["evaluation_sha256"] = _sha256(evaluation)
    return evaluation


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--policy", type=Path, default=Path("policy-candidates-v0.json"))
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    policy = load_policy_candidates(args.policy)
    try:
        evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PolicyEvaluationError(f"cannot read evidence: {args.evidence}") from exc
    result = evaluate_policy_evidence(policy, evidence, root=args.root)
    rendered = json.dumps(result, ensure_ascii=False, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
