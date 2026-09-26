import shutil
from pathlib import Path

from agent_lab_trust.cli import main


FIXTURES = Path(__file__).parent / "fixtures" / "gen-mentor" / "replay-sample"


def _copy_run(root: Path, name: str, *, include_structured: bool) -> Path:
    run_dir = root / name
    run_dir.mkdir()
    shutil.copy2(FIXTURES / "archive.json", run_dir / "archive.json")
    shutil.copy2(FIXTURES / "summary.json", run_dir / "summary.json")
    if include_structured:
        structured = run_dir / "output"
        structured.mkdir()
        (structured / "structured.json").write_text('{"entries": []}', encoding="utf-8")
    return run_dir


def test_cli_validate_includes_cost_and_failure_code(tmp_path: Path, capsys) -> None:
    _copy_run(tmp_path, "ok-run", include_structured=True)

    exit_code = main(["validate", str(tmp_path)])

    assert exit_code == 0
    line = capsys.readouterr().out.strip()
    assert '"failure_code": "ok"' in line
    assert '"cost_per_call"' in line


def test_cli_report_aggregates_and_hashes(tmp_path: Path, capsys) -> None:
    _copy_run(tmp_path, "ok-run", include_structured=True)
    _copy_run(tmp_path, "broken-run", include_structured=False)

    exit_code = main(["report", str(tmp_path)])

    assert exit_code == 0
    report = capsys.readouterr().out.strip()
    assert '"runs": 2' in report
    assert '"success": 1' in report
    assert '"failure": 1' in report
    assert '"missing_artifact": 1' in report
    assert '"report_hash"' in report
