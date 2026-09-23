import json
import shutil
from pathlib import Path

from agent_lab_trust.governance import audit_root, load_policy


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
