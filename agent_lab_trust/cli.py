"""Command-line entry point for the local-first trust layer skeleton."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from agent_lab_trust.adapters.gen_mentor import GenMentorAdapter
from agent_lab_trust.deletion import run_deletion_proof
from agent_lab_trust.governance import audit_root, load_policy


def _classify_failure(success: bool, error: str | None) -> str:
    if success:
        return "ok"
    text = (error or "").lower()
    if "parse" in text:
        return "parse_error"
    if "missing" in text or "structured" in text or "archive" in text:
        return "missing_artifact"
    return "unknown"


def _run_record(run) -> dict:
    calls = run.metrics.calls
    cost = run.metrics.cost_usd
    cost_per_call = (cost / calls) if calls and cost is not None else None
    return {
        "run_id": run.run_id,
        "project": run.project,
        "mode": run.mode,
        "success": run.success,
        "agents": len(run.agents),
        "steps": run.metrics.step_count,
        "calls": calls,
        "total_tokens": run.metrics.total_tokens,
        "cost_usd": cost,
        "cost_per_call": cost_per_call,
        "failure_code": _classify_failure(run.success, run.error),
    }


def _hash(payload: object) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agent-lab-trust")
    subcommands = parser.add_subparsers(dest="command", required=True)
    validate = subcommands.add_parser("validate", help="validate and summarize local runs")
    validate.add_argument("root", type=Path, help="directory containing run subdirectories")
    report = subcommands.add_parser("report", help="aggregate local runs into a hashed report")
    report.add_argument("root", type=Path, help="directory containing run subdirectories")
    deletion = subcommands.add_parser("deletion-proof", help="run the synthetic-only deletion proof")
    deletion.add_argument("--output", type=Path, default=None, help="write the proof JSON to this path")
    audit = subcommands.add_parser("audit", help="audit runs against a governance policy")
    audit.add_argument("root", type=Path, help="directory containing run subdirectories")
    audit.add_argument("--policy", type=Path, required=True, help="path to a JSON policy file")
    audit.add_argument("--output", type=Path, default=None, help="write the audit result JSON to this path")
    args = parser.parse_args(argv)

    if args.command in {"validate", "report"}:
        runs = GenMentorAdapter().discover(args.root)
        if not runs:
            print("no runs discovered", file=sys.stderr)
            return 1
        records = [_run_record(run) for run in runs]
        if args.command == "validate":
            for record in records:
                print(json.dumps(record, ensure_ascii=False, sort_keys=True))
            return 0
        if args.command == "report":
            failures: dict[str, int] = {}
            for record in records:
                code = record["failure_code"]
                failures[code] = failures.get(code, 0) + 1
            totals = {
                "runs": len(records),
                "success": sum(1 for record in records if record["success"]),
                "failure": sum(1 for record in records if not record["success"]),
                "calls": sum(record["calls"] or 0 for record in records),
                "total_tokens": sum(record["total_tokens"] or 0 for record in records),
                "cost_usd": sum(record["cost_usd"] or 0.0 for record in records),
                "failure_codes": failures,
            }
            totals["report_hash"] = _hash(totals)
            print(
                json.dumps(
                    totals,
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
            return 0

    if args.command == "deletion-proof":
        result = run_deletion_proof()
        payload = json.dumps(result, ensure_ascii=False, sort_keys=True)
        if args.output is not None:
            args.output.write_text(payload + "\n", encoding="utf-8")
        print(payload)
        return 0 if result["clean"] else 1

    if args.command == "audit":
        policy = load_policy(args.policy)
        result = audit_root(args.root, policy)
        payload = json.dumps(result, ensure_ascii=False, sort_keys=True)
        if args.output is not None:
            args.output.write_text(payload + "\n", encoding="utf-8")
        print(payload)
        return 0 if result["passed"] else 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
