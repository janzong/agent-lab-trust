import shutil
import json
from pathlib import Path

from agent_lab_trust.cli import main


FIXTURES = Path(__file__).parent / "fixtures" / "gen-mentor" / "replay-sample"


def test_cli_validate_prints_run_summary(tmp_path: Path, capsys) -> None:
    run_dir = tmp_path / "replay-sample"
    run_dir.mkdir()
    shutil.copy2(FIXTURES / "archive.json", run_dir / "archive.json")
    shutil.copy2(FIXTURES / "summary.json", run_dir / "summary.json")

    exit_code = main(["validate", str(tmp_path)])

    assert exit_code == 0
    lines = [line for line in capsys.readouterr().out.splitlines() if line.strip()]
    assert len(lines) == 1
    assert '"run_id": "replay-sample"' in lines[0]
    assert '"project": "gen-mentor"' in lines[0]


def test_cli_policy_check_emits_canonical_evaluation(tmp_path: Path, capsys) -> None:
    (tmp_path / "rollback.json").write_text("{}", encoding="utf-8")
    (tmp_path / "manifest.json").write_text("{}", encoding="utf-8")
    evidence = {
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
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text(json.dumps(evidence), encoding="utf-8")

    exit_code = main([
        "policy-check",
        str(evidence_path),
        "--policy",
        str(Path(__file__).parent.parent / "policy-candidates-v0.json"),
        "--root",
        str(tmp_path),
    ])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["passed"] is True
    assert payload["policy_sha256"]
    assert payload["evaluation_sha256"]


def test_shipped_policy_evidence_example_passes(capsys) -> None:
    root = Path(__file__).parent.parent / "examples" / "policy-evidence"
    exit_code = main([
        "policy-check",
        str(root / "evidence.json"),
        "--policy",
        str(Path(__file__).parent.parent / "policy-candidates-v0.json"),
        "--root",
        str(root),
    ])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["passed"] is True
    assert payload["implemented_checks"] == [
        "exact_evidence_required",
        "human_precision_threshold",
        "natural_reuse_requires_uncontrolled_selection",
        "negative_result_gate",
        "rollback_manifest_required",
        "runtime_identity_required",
    ]
