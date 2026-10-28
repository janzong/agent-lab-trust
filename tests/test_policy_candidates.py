import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_policy_candidate_contract_is_unique_fail_closed_and_linked() -> None:
    payload = json.loads((ROOT / "policy-candidates-v0.json").read_text(encoding="utf-8"))
    checks = payload["checks"]

    assert payload["schema_version"] == 0
    assert payload["status"] == "design_not_executable"
    assert len(checks) == 10
    assert len({check["id"] for check in checks}) == 10
    assert all(check["fail_closed"] is True for check in checks)
    assert all((ROOT / check["method_card"].split("#")[0]).exists() for check in checks)


def test_threshold_checks_define_metric_and_failure_action() -> None:
    payload = json.loads((ROOT / "policy-candidates-v0.json").read_text(encoding="utf-8"))
    threshold_checks = [check for check in payload["checks"] if check["policy_type"] == "threshold"]

    assert {check["id"] for check in threshold_checks} == {
        "negative_result_gate",
        "human_precision_threshold",
    }
    for check in threshold_checks:
        assert check["threshold"]["metric"] == "human_precision"
        assert check["threshold"]["minimum"] == 0.8
        assert check["on_failure"].endswith("block")


def test_reproduction_and_natural_reuse_checks_are_fail_closed() -> None:
    payload = json.loads((ROOT / "policy-candidates-v0.json").read_text(encoding="utf-8"))
    checks = {check["id"]: check for check in payload["checks"]}

    assert checks["natural_reuse_requires_uncontrolled_selection"]["fail_closed"] is True
    assert checks["runtime_identity_required"]["fail_closed"] is True
    assert checks["bounded_expansion_tiering_required"]["fail_closed"] is True
