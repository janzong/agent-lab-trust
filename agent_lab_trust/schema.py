from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class CamelModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        alias_generator=lambda field_name: "".join(
            part if index == 0 else part.capitalize()
            for index, part in enumerate(field_name.split("_"))
        ),
        populate_by_name=True,
    )


class RunMetrics(CamelModel):

    calls: int | None = None
    failures: int | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    cache_read_tokens: int | None = None
    cost_usd: float | None = None
    duration_seconds: float | None = None
    step_count: int | None = None


class LearningMetrics(CamelModel):
    path_sessions: int
    completed_sessions: int
    generated_documents: int
    quizzes: int
    quiz_answered: int
    quiz_correct: int
    quiz_accuracy: float | None = None


class LearningSession(CamelModel):
    index: int
    title: str
    completed: bool
    has_document: bool
    quiz_answered: int | None = None
    quiz_correct: int | None = None


class DelayedMasteryMetrics(CamelModel):
    schema_version: int
    baseline_answered: int
    baseline_correct: int
    baseline_accuracy: float
    assigned: int
    answered: int
    correct: int
    accuracy: float
    kind_accuracy: dict[str, float]
    condition_accuracy: dict[str, float]
    source_archive_sha256: str
    probe_bank_sha256: str
    integrity: dict[str, bool]


class UsagePoint(CamelModel):

    timestamp: str
    elapsed_ms: float | None = None
    calls: int | None = None
    total_tokens: int | None = None
    cost_usd: float | None = None


class RunProgress(CamelModel):
    active: bool = False
    started_at: str | None = None
    last_usage_at: str | None = None
    calls: int | None = None
    total_tokens: int | None = None
    cost_usd: float | None = None


class RunProvenance(CamelModel):
    provenance_status: str
    lab_core_commit: str
    runner_version: str
    runner_sha256: str
    scenario: str
    scenario_version: int
    upstream_engine: str
    upstream_engine_commit: str


class RunEvent(CamelModel):

    step: int | None = None
    entity: str | None = None
    component: str | None = None
    type: str
    summary: str


class AgentInteraction(CamelModel):

    source: str
    target: str
    weight: int


class TaskMetrics(CamelModel):
    active_agents: list[str] = []
    agent_action_counts: dict[str, int] = {}
    terminal_outcome: str | None = None


class Run(CamelModel):

    schema_version: int = 1
    run_id: str
    project: str
    mode: str
    source_dir: str
    started_at: str | None = None
    finished_at: str | None = None
    success: bool
    error: str | None = None
    agents: list[str] = []
    agent_goals: dict[str, str] = {}
    metrics: RunMetrics = RunMetrics()
    progress: RunProgress = RunProgress()
    provenance: RunProvenance | None = None
    learning: LearningMetrics | None = None
    learning_sessions: list[LearningSession] = []
    delayed_mastery: DelayedMasteryMetrics | None = None
    task_metrics: TaskMetrics | None = None
    events: list[RunEvent] = []
    interactions: list[AgentInteraction] = []
    usage: list[UsagePoint] = []
    artifacts: dict[str, str] = {}
