import json
from pathlib import Path

from agent_lab_trust.policy_checks import (
    PolicyEvaluationError,
    evaluate_policy_evidence,
    load_policy_candidates,
)


ROOT = Path(__file__).resolve().parents[1]


def policy_payload():
    return json.loads((ROOT / "policy-candidates-v0.json").read_text(encoding="utf-8"))


def full_evidence(root: Path) -> dict:
    (root / "rollback.json").write_text("{}", encoding="utf-8")
    (root / "manifest.json").write_text("{}", encoding="utf-8")
    return {
        "schema_version": 0,
        "checks": {
            "exact_evidence_required": {
                "asset_id": "asset-1",
                "quote": "verified quote",
                "source_sha": "a" * 64,
                "chunk_id": "chunk-1",
                "source_status": "published",
                "quote_verified": True,
                "offset_valid": True,
                "chunk_current": True,
            },
            "negative_result_gate": {
                "candidate_count": 308,
                "human_sample_count": 50,
                "correct_count": 10,
                "production_write_count": 0,
            },
            "human_precision_threshold": {
                "sample_count": 25,
                "agreement_count": 22,
            },
            "rollback_manifest_required": {
                "rollback_path": "rollback.json",
                "manifest_path": "manifest.json",
            },
            "natural_reuse_requires_uncontrolled_selection": {
                "claimed_natural_reuse": False,
                "cohort_cutoff": "2026-10-22 05:28:46",
                "controlled_project_exclusions": ["controlled-1"],
                "eligible_workflow_count": 97,
                "natural_selection_rows": 0,
                "accepted_material_use_rows": 0,
            },
            "runtime_identity_required": {
                "target_commit": "abc123",
                "actual_commit": "abc123",
                "process_start_time": "2026-10-28T15:00:00+08:00",
                "health_version": "0.4.18",
                "artifact_hash": "b" * 64,
                "table_counts": {"nodes": 3940},
                "rollback_path": "rollback.json",
                "requested_model": "deepseek-chat",
                "served_model": "deepseek-chat",
                "provider": "deepseek",
            },
        },
    }


def test_negative_result_gate_passes_when_failed_precision_blocks_write(tmp_path: Path) -> None:
    evidence = full_evidence(tmp_path)

    result = evaluate_policy_evidence(policy_payload(), evidence, root=tmp_path)

    assert result["passed"] is True
    check = {item["id"]: item for item in result["results"]}["negative_result_gate"]
    assert check["id"] == "negative_result_gate"
    assert check["result"] == "pass"
    assert check["precision"] == 0.2
    assert check["production_write_count"] == 0


def test_negative_result_gate_fails_when_failed_precision_wrote_production(tmp_path: Path) -> None:
    evidence = full_evidence(tmp_path)
    evidence["checks"]["negative_result_gate"]["production_write_count"] = 3

    result = evaluate_policy_evidence(policy_payload(), evidence, root=tmp_path)

    assert result["passed"] is False
    check = {item["id"]: item for item in result["results"]}["negative_result_gate"]
    assert check["reason"] == "failed precision wrote production rows"


def test_human_precision_requires_threshold_and_minimum_sample(tmp_path: Path) -> None:
    evidence = full_evidence(tmp_path)
    evidence["checks"]["human_precision_threshold"] = {
        "sample_count": 24,
        "agreement_count": 24,
    }

    result = evaluate_policy_evidence(policy_payload(), evidence, root=tmp_path)

    assert result["passed"] is False
    check = {item["id"]: item for item in result["results"]}["human_precision_threshold"]
    assert check["reason"] == "sample below minimum"

    evidence["checks"]["human_precision_threshold"] = {
        "sample_count": 25,
        "agreement_count": 22,
    }
    result = evaluate_policy_evidence(policy_payload(), evidence, root=tmp_path)
    assert result["passed"] is True
    check = {item["id"]: item for item in result["results"]}["human_precision_threshold"]
    assert check["precision"] == 0.88


def test_rollback_manifest_requires_non_empty_files(tmp_path: Path) -> None:
    evidence = full_evidence(tmp_path)

    passed = evaluate_policy_evidence(policy_payload(), evidence, root=tmp_path)
    assert passed["passed"] is True

    (tmp_path / "manifest.json").write_text("", encoding="utf-8")
    failed = evaluate_policy_evidence(policy_payload(), evidence, root=tmp_path)
    assert failed["passed"] is False
    check = {item["id"]: item for item in failed["results"]}["rollback_manifest_required"]
    assert check["reason"] == "manifest file missing or empty"


def test_natural_reuse_gate_passes_without_claim_and_fails_with_unsupported_claim(tmp_path: Path) -> None:
    evidence = full_evidence(tmp_path)

    no_claim = evaluate_policy_evidence(policy_payload(), evidence, root=tmp_path)
    assert no_claim["passed"] is True
    natural = {item["id"]: item for item in no_claim["results"]}[
        "natural_reuse_requires_uncontrolled_selection"
    ]
    assert natural["result"] == "pass"
    assert natural["reason"] == "no natural-reuse claim"

    evidence["checks"]["natural_reuse_requires_uncontrolled_selection"]["claimed_natural_reuse"] = True
    unsupported = evaluate_policy_evidence(policy_payload(), evidence, root=tmp_path)
    assert unsupported["passed"] is False
    natural = {item["id"]: item for item in unsupported["results"]}[
        "natural_reuse_requires_uncontrolled_selection"
    ]
    assert natural["reason"] == "claimed reuse lacks natural selection or accepted material use"


def test_exact_evidence_requires_current_verified_published_quote(tmp_path: Path) -> None:
    evidence = full_evidence(tmp_path)
    evidence["checks"]["exact_evidence_required"]["chunk_current"] = False

    result = evaluate_policy_evidence(policy_payload(), evidence, root=tmp_path)
    check = {item["id"]: item for item in result["results"]}["exact_evidence_required"]

    assert result["passed"] is False
    assert check["reason"] == "exact evidence not current or verified"


def test_runtime_identity_requires_matching_commit_and_rollback(tmp_path: Path) -> None:
    evidence = full_evidence(tmp_path)
    evidence["checks"]["runtime_identity_required"]["actual_commit"] = "different"

    result = evaluate_policy_evidence(policy_payload(), evidence, root=tmp_path)
    check = {item["id"]: item for item in result["results"]}["runtime_identity_required"]

    assert result["passed"] is False
    assert check["reason"] == "target and actual commit differ"


def test_missing_evidence_is_fail_closed_and_hash_is_stable(tmp_path: Path) -> None:
    policy = policy_payload()
    evidence = {"schema_version": 0, "checks": {}}

    first = evaluate_policy_evidence(policy, evidence, root=tmp_path)
    second = evaluate_policy_evidence(policy, evidence, root=tmp_path)

    assert first["passed"] is False
    assert "negative_result_gate" in first["missing_inputs"]
    assert first["policy_sha256"] == second["policy_sha256"]


def test_rejects_unknown_evidence_schema() -> None:
    try:
        evaluate_policy_evidence(
            policy_payload(),
            {"schema_version": 99, "checks": {}},
            root=ROOT,
        )
    except PolicyEvaluationError as exc:
        assert "schema_version" in str(exc)
    else:
        raise AssertionError("expected PolicyEvaluationError")
