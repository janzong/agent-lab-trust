import json
from pathlib import Path

import pytest

from agent_lab_trust.adapters.gen_mentor import GenMentorAdapter, RunParseError


def test_gen_mentor_adapter_normalizes_replay_archive(tmp_path: Path) -> None:
    source = Path(__file__).parent / "fixtures" / "gen-mentor" / "replay-sample"
    run_dir = tmp_path / "replay-sample"
    run_dir.mkdir()
    (run_dir / "output").mkdir()
    for name in ("archive.json", "summary.json"):
        (run_dir / name).symlink_to(source / name)
    (run_dir / "output" / "structured.json").symlink_to(source / "output" / "structured.json")

    run = GenMentorAdapter().discover(tmp_path)[0]

    assert run.run_id == "replay-sample"
    assert run.project == "gen-mentor"
    assert run.mode == "replay"
    assert run.success is True
    assert run.started_at == "2026-09-17T05:20:07+00:00"
    assert run.finished_at == "2026-09-20T05:20:07+00:00"
    assert run.metrics.calls == 4
    assert run.metrics.step_count == 1
    assert run.agents == ["Pandas Practice", "Python Fundamentals"]
    assert run.agent_goals == {
        "Pandas Practice": "intermediate",
        "Python Fundamentals": "beginner",
    }
    assert run.learning is not None
    assert run.learning.path_sessions == 2
    assert run.learning.completed_sessions == 1
    assert run.learning.generated_documents == 1
    assert run.learning.quizzes == 1
    assert run.learning.quiz_answered == 2
    assert run.learning.quiz_correct == 2
    assert run.learning.quiz_accuracy == 1.0
    assert [session.model_dump() for session in run.learning_sessions] == [
        {
            "index": 0,
            "title": "Load and inspect DataFrames",
            "completed": True,
            "has_document": True,
            "quiz_answered": 2,
            "quiz_correct": 2,
        },
        {
            "index": 1,
            "title": "Clean missing values",
            "completed": False,
            "has_document": False,
            "quiz_answered": None,
            "quiz_correct": None,
        },
    ]
    assert [event.summary for event in run.events] == [
        "Learning goal created: Learn Pandas fundamentals",
        "Lesson completed: Load and inspect DataFrames",
        "Quiz completed: 2/2 correct",
    ]
    assert [interaction.model_dump() for interaction in run.interactions] == [
        {"source": "Pandas Practice", "target": "Python Fundamentals", "weight": 1}
    ]


def test_gen_mentor_adapter_rejects_malformed_archive(tmp_path: Path) -> None:
    run_dir = tmp_path / "broken"
    run_dir.mkdir()
    (run_dir / "archive.json").write_text("{bad", encoding="utf-8")

    try:
        GenMentorAdapter().discover(tmp_path)
    except RunParseError as exc:
        assert "broken/archive.json" in str(exc)
    else:
        raise AssertionError("expected RunParseError")


def test_gen_mentor_adapter_reads_live_record_attempt_metrics(tmp_path: Path) -> None:
    source = Path(__file__).parent / "fixtures" / "gen-mentor" / "replay-sample"
    run_dir = tmp_path / "live-record"
    run_dir.mkdir()
    (run_dir / "archive.json").symlink_to(source / "archive.json")
    (run_dir / "summary.json").write_text(
        json.dumps(
            {
                "project": "gen-mentor",
                "run_id": "live-record",
                "mode": "live-record",
                "success": True,
                "record_attempts_calls": 244,
                "record_attempts_cost_usd": 3.9529266,
            }
        ),
        encoding="utf-8",
    )

    run = GenMentorAdapter().discover(tmp_path)[0]

    assert run.mode == "live-record"
    assert run.metrics.calls == 244
    assert run.metrics.cost_usd == 3.9529266


def test_gen_mentor_adapter_reads_delayed_mastery_probe(tmp_path: Path) -> None:
    source = Path(__file__).parent / "fixtures" / "gen-mentor" / "replay-sample"
    delayed = Path(__file__).parent / "fixtures" / "gen-mentor" / "delayed-probe"
    run_dir = tmp_path / "delayed-probe"
    run_dir.mkdir()
    (run_dir / "archive.json").symlink_to(source / "archive.json")
    (run_dir / "delayed_mastery.json").symlink_to(delayed / "delayed_mastery.json")

    run = GenMentorAdapter().discover(tmp_path)[0]

    assert run.delayed_mastery is not None
    delayed_metrics = run.delayed_mastery
    assert delayed_metrics.schema_version == 1
    assert delayed_metrics.baseline_answered == 4
    assert delayed_metrics.baseline_correct == 4
    assert delayed_metrics.baseline_accuracy == 1.0
    assert delayed_metrics.assigned == 12
    assert delayed_metrics.answered == 12
    assert delayed_metrics.correct == 9
    assert delayed_metrics.accuracy == 0.75
    assert delayed_metrics.kind_accuracy == {"retention": 0.875, "transfer": 0.5}
    assert delayed_metrics.condition_accuracy == {"closed_book": 0.625, "open_book": 1.0}
    assert delayed_metrics.source_archive_sha256 == "a" * 64
    assert delayed_metrics.probe_bank_sha256 == "b" * 64
    assert delayed_metrics.integrity == {
        "archive_unchanged": True,
        "leak_scan_passed": True,
        "scoring_recomputable": True,
        "window_timestamps_verified": True,
    }
    assert "Delayed mastery probe valid: 9/12 correct" in [
        event.summary for event in run.events
    ]
    assert run.artifacts["delayed_mastery"] == "delayed_mastery.json"


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ({"probes": []}, "at least one probe"),
        ({"baseline": {"quiz_answered": 3, "quiz_correct": 4}}, "baseline counts"),
        (
            {
                "probes": [
                    {
                        "id": "bad",
                        "kind": "unexpected",
                        "condition": "closed_book",
                        "window_hours": 24,
                        "session_index": 0,
                        "assigned": 4,
                        "answered": 4,
                        "correct": 4,
                    }
                ]
            },
            "unknown probe kind",
        ),
        (
            {
                "probes": [
                    {
                        "id": "bad-counts",
                        "kind": "retention",
                        "condition": "closed_book",
                        "window_hours": 24,
                        "session_index": 0,
                        "assigned": 4,
                        "answered": 5,
                        "correct": 4,
                    }
                ]
            },
            "probe counts",
        ),
        (
            {
                "integrity": {
                    "source_archive_sha256": "a" * 64,
                    "probe_bank_sha256": "b" * 64,
                    "archive_unchanged": False,
                    "leak_scan_passed": True,
                    "scoring_recomputable": True,
                    "window_timestamps_verified": True,
                }
            },
            "integrity gate",
        ),
    ],
)
def test_gen_mentor_adapter_rejects_invalid_delayed_mastery_probe(
    tmp_path: Path, mutation: dict, message: str
) -> None:
    source = Path(__file__).parent / "fixtures" / "gen-mentor" / "replay-sample"
    delayed = Path(__file__).parent / "fixtures" / "gen-mentor" / "delayed-probe"
    run_dir = tmp_path / "invalid-delayed"
    run_dir.mkdir()
    (run_dir / "archive.json").symlink_to(source / "archive.json")
    payload = json.loads(delayed.joinpath("delayed_mastery.json").read_text(encoding="utf-8"))
    payload.update(mutation)
    (run_dir / "delayed_mastery.json").write_text(
        json.dumps(payload), encoding="utf-8"
    )

    try:
        GenMentorAdapter().discover(tmp_path)
    except RunParseError as exc:
        assert message in str(exc)
    else:
        raise AssertionError("expected RunParseError")
