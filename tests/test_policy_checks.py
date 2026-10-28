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
