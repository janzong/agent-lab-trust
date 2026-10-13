import json
import shutil
from pathlib import Path

from agent_lab_trust.governance import audit_root, load_policy, PolicyError


FIXTURES = Path(__file__).parent / "fixtures" / "gen-mentor" / "replay-sample"
POLICY = {"max_cost_usd": 1.0, "max_calls": 100, "require_structured_artifact": True}


def _make_run(root: Path, name: str, *, structured: bool = True, cost: float = 0.01, calls: int = 10, extra: tuple[str, str] | None = None) -> Path:
    run = root / name
    run.mkdir()
    shutil.copy2(FIXTURES / "archive.json", run / "archive.json")
    (run / "summary.json").write_text(
        json.dumps({"project": "gen-mentor", "run_id": name, "mode": "replay", "success": True, "fixture_calls": calls, "cost_usd": cost}),
        encoding="utf-8",
    )
    if structured:
        (run / "output").mkdir()
        (run / "output" / "structured.json").write_text('{"entries": []}', encoding="utf-8")
    if extra is not None:
        (run / extra[0]).write_text(extra[1], encoding="utf-8")
    return run


def test_audit_passes_clean_run(tmp_path: Path) -> None:
    _make_run(tmp_path, "clean-run")
    result = audit_root(tmp_path, POLICY)
    assert result["passed"] is True
    assert result["runs"] == 1
    assert result["findings"] == []
    assert len(result["audit_hash"]) == 64


def test_audit_flags_missing_artifact(tmp_path: Path) -> None:
    _make_run(tmp_path, "broken-run", structured=False)
    result = audit_root(tmp_path, POLICY)
    assert result["passed"] is False
    assert any(finding["code"] == "missing_artifact" for finding in result["findings"])


def test_audit_flags_cost_and_calls(tmp_path: Path) -> None:
    _make_run(tmp_path, "expensive-run", cost=2.0, calls=200)
    result = audit_root(tmp_path, POLICY)
    codes = {finding["code"] for finding in result["findings"]}
    assert {"cost_exceeded", "calls_exceeded"} <= codes


def test_audit_flags_forbidden_marker(tmp_path: Path) -> None:
    _make_run(tmp_path, "marker-run", extra=("notes.txt", "contains SECRET in text"))
    result = audit_root(tmp_path, {**POLICY, "forbidden_markers": ["SECRET"]})
    assert result["passed"] is False
    assert any(finding["code"] == "forbidden_marker" for finding in result["findings"])


def test_audit_hash_is_deterministic(tmp_path: Path) -> None:
    _make_run(tmp_path, "clean-run")
    assert audit_root(tmp_path, POLICY) == audit_root(tmp_path, POLICY)


def test_load_policy_rejects_bad_shape(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text('{"forbidden_markers": "SECRET"}', encoding="utf-8")
    try:
        load_policy(bad)
    except Exception as exc:
        assert "forbidden_markers" in str(exc)
    else:
        raise AssertionError("expected PolicyError")


def test_audit_accepts_policy_declared_artifacts(tmp_path: Path) -> None:
    _make_run(tmp_path, "genmentor-run", structured=False)
    policy = {
        "max_cost_usd": 1.0,
        "max_calls": 100,
        "required_artifacts": ["archive.json", "summary.json"],
        "required_artifacts_mode": "all",
    }
    result = audit_root(tmp_path, policy)
    assert result["passed"] is True
    assert result["required_artifacts"] == ["archive.json", "summary.json"]


def test_audit_flags_missing_policy_declared_artifact(tmp_path: Path) -> None:
    _make_run(tmp_path, "genmentor-run", structured=False)
    policy = {
        "max_cost_usd": 1.0,
        "max_calls": 100,
        "required_artifacts": ["archive.json", "missing.json"],
        "required_artifacts_mode": "all",
    }
    result = audit_root(tmp_path, policy)
    assert result["passed"] is False
    assert any("missing.json" in finding.get("missing", []) for finding in result["findings"])


def test_audit_binds_full_policy_content(tmp_path: Path) -> None:
    _make_run(tmp_path, "clean-run")
    policy_a = {**POLICY, "max_cost_usd": 0.60}
    policy_b = {**POLICY, "max_cost_usd": 100.0}
    result_a = audit_root(tmp_path, policy_a)
    result_b = audit_root(tmp_path, policy_b)
    assert result_a["audit_hash"] != result_b["audit_hash"]
    assert result_a["policy"]["max_cost_usd"] == 0.60
    assert len(result_a["policy_sha256"]) == 64


def test_policy_rejects_invalid_batch_contract() -> None:
    import json
    import tempfile
    import pytest

    for bad in [
        {"batch_contract": []},
        {"batch_contract": {"metrics_file": ""}},
        {"batch_contract": {"metrics_file": "a.json", "metrics": {}}},
        {"batch_contract": {"metrics_file": "a.json", "metrics": {"x": "not-object"}}},
        {"batch_contract": {"metrics_file": "a.json", "metrics": {"x": {"min": "bad"}}}},
    ]:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump(bad, handle)
            policy_path = Path(handle.name)
        try:
            with pytest.raises(PolicyError):
                load_policy(policy_path)
        finally:
            policy_path.unlink(missing_ok=True)


def test_batch_contract_passes_when_metrics_meet_thresholds(tmp_path: Path) -> None:
    run_dir = tmp_path / "run-a"
    run_dir.mkdir()
    (run_dir / "archive.json").write_text(
        json.dumps({"goals": [{"id": "g1", "title": "T"}], "active_goal_id": "g1"})
    )
    output_dir = run_dir / "output"
    output_dir.mkdir()
    (output_dir / "structured.json").write_text(
        json.dumps({"metrics": {"citation_reconciliation": 0.9, "dirty_entries": 2}})
    )
    policy = {
        "require_structured_artifact": False,
        "batch_contract": {
            "metrics_file": "output/structured.json",
            "metrics": {
                "metrics.citation_reconciliation": {"min": 0.5},
                "metrics.dirty_entries": {"max": 4},
            },
        },
    }
    result = audit_root(tmp_path, policy)
    assert result["passed"] is True
    assert result["findings"] == []


def test_batch_contract_flags_violation_and_unknown(tmp_path: Path) -> None:
    run_dir = tmp_path / "run-a"
    run_dir.mkdir()
    (run_dir / "archive.json").write_text(
        json.dumps({"goals": [{"id": "g1", "title": "T"}], "active_goal_id": "g1"})
    )
    output_dir = run_dir / "output"
    output_dir.mkdir()
    (output_dir / "structured.json").write_text(
        json.dumps({"metrics": {"citation_reconciliation": 0.2, "dirty_entries": 9}})
    )
    policy = {
        "require_structured_artifact": False,
        "batch_contract": {
            "metrics_file": "output/structured.json",
            "metrics": {
                "metrics.citation_reconciliation": {"min": 0.5},
                "metrics.dirty_entries": {"max": 4},
                "metrics.method_honesty": {"min": 0.95},
            },
        },
    }
    result = audit_root(tmp_path, policy)
    assert result["passed"] is False
    codes = {finding["code"] for finding in result["findings"]}
    assert "batch_metric_violation" in codes
    assert "batch_metric_unknown" in codes


def test_shipped_example_policy_passes_bundled_fixture() -> None:
    root = Path(__file__).parent / "fixtures" / "gen-mentor"
    policy = json.loads((Path(__file__).parent.parent / "policy.example.json").read_text())
    result = audit_root(root, policy)
    assert result["passed"] is True, result["findings"]
