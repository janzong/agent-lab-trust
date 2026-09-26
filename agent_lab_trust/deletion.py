"""Synthetic-only deletion proof for the trust layer."""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

from agent_lab_trust.learner_store import LocalLearnerStore


def _canonical(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def run_deletion_proof() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        store = LocalLearnerStore(Path(tmp))
        for index in range(1, 4):
            store.put(
                f"synthetic-s{index}",
                {
                    "probe_id": f"p{index}",
                    "selected_index": index % 4,
                    "submitted_at_ms": 1000 + index,
                    "attempt": 1,
                    "source": "synthetic-fixture",
                },
            )
        before = store.audit()
        before_count = store.count()
        for index in range(1, 4):
            store.delete(f"synthetic-s{index}")
        after = store.audit()
        after_count = store.count()
        store.delete("synthetic-s1")
        idempotent_count = store.count()
        result = {
            "before_count": before_count,
            "before_sha256": before["sha256"],
            "after_count": after_count,
            "after_sha256": after["sha256"],
            "idempotent_delete_count": idempotent_count,
            "clean": after_count == 0 and idempotent_count == 0,
        }
        result["audit_hash"] = hashlib.sha256(_canonical(result).encode("utf-8")).hexdigest()[:16]
        return result
