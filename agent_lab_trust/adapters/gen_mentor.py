from __future__ import annotations

import datetime as dt
import itertools
import json
from pathlib import Path
import re
from typing import Any

from agent_lab_trust.schema import (
    AgentInteraction,
    DelayedMasteryMetrics,
    LearningMetrics,
    LearningSession,
    Run,
    RunEvent,
    RunMetrics,
)


class RunParseError(RuntimeError):
    """Raised when a GenMentor archive cannot be parsed."""


class GenMentorAdapter:
    project = "gen-mentor"

    def discover(self, root: Path) -> list[Run]:
        if not root.exists():
            return []
        if not root.is_dir():
            raise RunParseError(f"run root is not a directory: {root}")
        runs = [
            self._load_run(path)
            for path in sorted(root.iterdir())
            if path.is_dir() and (path / "archive.json").exists()
        ]
        return sorted((run for run in runs if run is not None), key=lambda run: run.run_id)

    def _load_run(self, run_dir: Path) -> Run | None:
        archive_path = run_dir / "archive.json"
        summary_path = run_dir / "summary.json"
        summary = self._read_json(summary_path) if summary_path.exists() else {}
        archive = self._read_json(archive_path)
        structured_path = next(
            (
                candidate
                for candidate in (
                    run_dir / "output" / "structured.json",
                    run_dir / "results" / "structured.json",
                )
                if candidate.exists()
            ),
            None,
        )
        structured = self._read_json(structured_path) if structured_path else {}
        goals = archive.get("goals") or []
        if not goals:
            raise RunParseError(f"GenMentor archive has no goals: {archive_path}")
        active_id = archive.get("active_goal_id")
        goal = next((item for item in goals if item.get("id") == active_id), goals[0])

        requirements = goal.get("skill_requirements") or []
        agents = sorted(str(item.get("name")) for item in requirements if item.get("name"))
        goals_by_agent = {
            str(item["name"]): str(item.get("required_level") or "")
            for item in requirements
            if item.get("name")
        }
        path_items = goal.get("learning_path") or []
        sessions = goal.get("sessions") or {}
        completed = [item for item in sessions.values() if item.get("completed_at") is not None]
        documents = [item for item in sessions.values() if item.get("document")]
        quiz_results = [item for item in sessions.values() if item.get("quiz_results")]
        answered = sum(int(item["quiz_results"].get("answered") or 0) for item in quiz_results)
        correct = sum(int(item["quiz_results"].get("correct") or 0) for item in quiz_results)
        accuracy = (correct / answered) if answered else None
        delayed_mastery = self._delayed_mastery(run_dir)
        events = self._events(goal)
        if delayed_mastery is not None:
            events.append(
                RunEvent(
                    step=len(completed),
                    entity="learner",
                    component="delayed-mastery",
                    type="stage",
                    summary=(
                        "Delayed mastery probe valid: "
                        f"{delayed_mastery.correct}/{delayed_mastery.answered} correct"
                    ),
                )
            )
        artifacts = {"archive": "archive.json"}
        if delayed_mastery is not None:
            artifacts["delayed_mastery"] = "delayed_mastery.json"
        if structured_path is not None:
            artifacts["structured"] = str(structured_path.relative_to(run_dir))
        success = bool(structured_path is not None and structured)

        return Run(
            run_id=run_dir.name,
            project=self.project,
            mode=str(summary.get("mode") or "replay"),
            source_dir=run_dir.name,
            started_at=self._iso_ms(goal.get("created_at")),
            finished_at=self._iso_ms(archive.get("exported_at")),
            success=success,
            error=None if success else "structured.json is missing or empty",
            agents=agents,
            agent_goals=goals_by_agent,
            metrics=RunMetrics(
                calls=self._optional_int(
                    summary.get("fixture_calls", summary.get("record_attempts_calls"))
                ),
                cost_usd=self._optional_float(
                    summary.get("cost_usd", summary.get("record_attempts_cost_usd"))
                ),
                step_count=len(completed),
            ),
            learning=LearningMetrics(
                path_sessions=len(path_items),
                completed_sessions=len(completed),
                generated_documents=len(documents),
                quizzes=len(quiz_results),
                quiz_answered=answered,
                quiz_correct=correct,
                quiz_accuracy=accuracy,
            ),
            learning_sessions=self._learning_sessions(goal, path_items, sessions),
            events=events,
            interactions=self._interactions(path_items, agents),
            delayed_mastery=delayed_mastery,
            artifacts=artifacts,
        )

    def _delayed_mastery(self, run_dir: Path) -> DelayedMasteryMetrics | None:
        artifact_path = run_dir / "delayed_mastery.json"
        if not artifact_path.exists():
            return None
        payload = self._read_json(artifact_path)
        if not isinstance(payload, dict):
            raise RunParseError(
                f"GenMentor delayed mastery artifact is not an object: {artifact_path}"
            )
        if payload.get("schema_version") != 1:
            raise RunParseError(
                f"GenMentor delayed mastery artifact has unsupported schema: {artifact_path}"
            )

        baseline = self._mapping(payload.get("baseline"), artifact_path, "baseline")
        baseline_answered = self._nonnegative_int(
            baseline.get("quiz_answered"), artifact_path, "baseline quiz_answered"
        )
        baseline_correct = self._nonnegative_int(
            baseline.get("quiz_correct"), artifact_path, "baseline quiz_correct"
        )
        if baseline_answered == 0 or baseline_correct > baseline_answered:
            raise RunParseError(
                f"GenMentor delayed mastery baseline counts are inconsistent: {artifact_path}"
            )

        probes_value = payload.get("probes")
        if not isinstance(probes_value, list) or not probes_value:
            raise RunParseError(
                f"GenMentor delayed mastery artifact needs at least one probe: {artifact_path}"
            )
        allowed_kinds = {"retention", "transfer"}
        allowed_conditions = {"closed_book", "open_book"}
        probe_ids: set[str] = set()
        kind_counts: dict[str, list[int]] = {}
        condition_counts: dict[str, list[int]] = {}
        total = [0, 0, 0]
        for raw_probe in probes_value:
            if not isinstance(raw_probe, dict):
                raise RunParseError(
                    f"GenMentor delayed mastery probe is not an object: {artifact_path}"
                )
            probe_id = str(raw_probe.get("id") or "")
            if not probe_id or probe_id in probe_ids:
                raise RunParseError(
                    f"GenMentor delayed mastery probe id is empty or duplicated: {artifact_path}"
                )
            probe_ids.add(probe_id)
            kind = str(raw_probe.get("kind") or "")
            if kind not in allowed_kinds:
                raise RunParseError(
                    f"GenMentor delayed mastery artifact has unknown probe kind {kind!r}: "
                    f"{artifact_path}"
                )
            condition = str(raw_probe.get("condition") or "")
            if condition not in allowed_conditions:
                raise RunParseError(
                    f"GenMentor delayed mastery artifact has unknown condition {condition!r}: "
                    f"{artifact_path}"
                )
            window_hours = raw_probe.get("window_hours")
            if type(window_hours) is not int or window_hours < 1:
                raise RunParseError(
                    f"GenMentor delayed mastery window_hours is invalid: {artifact_path}"
                )
            session_index = raw_probe.get("session_index")
            if type(session_index) is not int or session_index < 0:
                raise RunParseError(
                    f"GenMentor delayed mastery session_index is invalid: {artifact_path}"
                )
            assigned = self._nonnegative_int(
                raw_probe.get("assigned"), artifact_path, "probe assigned"
            )
            answered = self._nonnegative_int(
                raw_probe.get("answered"), artifact_path, "probe answered"
            )
            correct = self._nonnegative_int(
                raw_probe.get("correct"), artifact_path, "probe correct"
            )
            if assigned == 0 or correct > answered or answered > assigned:
                raise RunParseError(
                    f"GenMentor delayed mastery probe counts are inconsistent: {artifact_path}"
                )
            for bucket, key in (
                (kind_counts, kind),
                (condition_counts, condition),
            ):
                counts = bucket.setdefault(key, [0, 0, 0])
                counts[0] += assigned
                counts[1] += answered
                counts[2] += correct
            total[0] += assigned
            total[1] += answered
            total[2] += correct

        integrity = self._mapping(payload.get("integrity"), artifact_path, "integrity")
        required_integrity = (
            "archive_unchanged",
            "leak_scan_passed",
            "scoring_recomputable",
            "window_timestamps_verified",
        )
        integrity_flags: dict[str, bool] = {}
        for key in required_integrity:
            value = integrity.get(key)
            if value is not True:
                raise RunParseError(
                    f"GenMentor delayed mastery integrity gate failed for {key}: "
                    f"{artifact_path}"
                )
            integrity_flags[key] = True

        sha256_pattern = re.compile(r"[0-9a-f]{64}")
        source_hash = str(integrity.get("source_archive_sha256") or "")
        probe_hash = str(integrity.get("probe_bank_sha256") or "")
        if not sha256_pattern.fullmatch(source_hash):
            raise RunParseError(
                f"GenMentor delayed mastery source archive hash is invalid: {artifact_path}"
            )
        if not sha256_pattern.fullmatch(probe_hash):
            raise RunParseError(
                f"GenMentor delayed mastery probe bank hash is invalid: {artifact_path}"
            )

        def accuracy(counts: list[int]) -> float:
            return counts[2] / counts[1]

        return DelayedMasteryMetrics(
            schema_version=1,
            baseline_answered=baseline_answered,
            baseline_correct=baseline_correct,
            baseline_accuracy=accuracy([0, baseline_answered, baseline_correct]),
            assigned=total[0],
            answered=total[1],
            correct=total[2],
            accuracy=accuracy(total),
            kind_accuracy={key: accuracy(value) for key, value in kind_counts.items()},
            condition_accuracy={
                key: accuracy(value) for key, value in condition_counts.items()
            },
            source_archive_sha256=source_hash,
            probe_bank_sha256=probe_hash,
            integrity=integrity_flags,
        )

    def _mapping(
        self, value: Any, artifact_path: Path, name: str
    ) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise RunParseError(
                f"GenMentor delayed mastery {name} is not an object: {artifact_path}"
            )
        return value

    def _nonnegative_int(self, value: Any, artifact_path: Path, name: str) -> int:
        if type(value) is not int or value < 0:
            raise RunParseError(
                f"GenMentor delayed mastery {name} is invalid: {artifact_path}"
            )
        return value

    def _learning_sessions(
        self,
        goal: dict[str, Any],
        path_items: list[dict[str, Any]],
        sessions: dict[str, Any],
    ) -> list[LearningSession]:
        goal_id = goal.get("id")
        result: list[LearningSession] = []
        for index, item in enumerate(path_items):
            session = sessions.get(f"{goal_id}:{index}") or {}
            quiz = session.get("quiz_results") or {}
            result.append(
                LearningSession(
                    index=index,
                    title=str(item.get("title") or f"Session {index + 1}"),
                    completed=bool(session.get("completed_at")) or bool(item.get("if_learned")),
                    has_document=bool(session.get("document")),
                    quiz_answered=self._optional_int(quiz.get("answered")),
                    quiz_correct=self._optional_int(quiz.get("correct")),
                )
            )
        return result

    def _events(self, goal: dict[str, Any]) -> list[RunEvent]:
        events = [
            RunEvent(
                step=0,
                entity="learner",
                component="goal",
                type="learning",
                summary=f"Learning goal created: {goal.get('learning_goal') or goal.get('original_goal')}",
            )
        ]
        path_items = goal.get("learning_path") or []
        sessions = goal.get("sessions") or {}
        for index in range(len(path_items)):
            session = sessions.get(f"{goal.get('id')}:{index}")
            if not session:
                continue
            title = path_items[index].get("title") or f"Session {index + 1}"
            skills = path_items[index].get("associated_skills") or []
            entity = str(skills[0]) if skills else "learner"
            if session.get("completed_at") is not None:
                events.append(
                    RunEvent(
                        step=index + 1,
                        entity=entity,
                        component="lesson",
                        type="learning",
                        summary=f"Lesson completed: {title}",
                    )
                )
            result = session.get("quiz_results")
            if result:
                events.append(
                    RunEvent(
                        step=index + 1,
                        entity=entity,
                        component="quiz",
                        type="assessment",
                        summary=f"Quiz completed: {result.get('correct')}/{result.get('answered')} correct",
                    )
                )
        return events

    def _interactions(self, path_items: list[dict[str, Any]], agents: list[str]) -> list[AgentInteraction]:
        agent_set = set(agents)
        weights: dict[tuple[str, str], int] = {}
        for item in path_items:
            skills = sorted({str(skill) for skill in item.get("associated_skills") or [] if skill in agent_set})
            for source, target in itertools.combinations(skills, 2):
                weights[(source, target)] = weights.get((source, target), 0) + 1
        return [
            AgentInteraction(source=source, target=target, weight=weight)
            for (source, target), weight in sorted(weights.items())
        ]

    def _read_json(self, path: Path) -> Any:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RunParseError(f"cannot parse {path}: {exc}") from exc

    def _iso_ms(self, value: Any) -> str | None:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return None
        return dt.datetime.fromtimestamp(value / 1000, tz=dt.timezone.utc).isoformat(timespec="seconds")

    def _optional_int(self, value: Any) -> int | None:
        return int(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None

    def _optional_float(self, value: Any) -> float | None:
        return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None
