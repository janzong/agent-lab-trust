import shutil
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
