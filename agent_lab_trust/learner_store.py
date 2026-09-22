"""Minimal local store for synthetic learner records."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Mapping


_ALLOWED_KEYS = {"probe_id", "question_id", "selected_index", "submitted_at_ms", "attempt", "source"}
_SAFE_ID = re.compile(r"[A-Za-z0-9_-]{1,64}")


class LearnerStoreError(ValueError):
    """Raised when a synthetic learner record violates the local contract."""


class LocalLearnerStore:
    """Store synthetic learner records as restricted local JSON files."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        os.chmod(self.root, 0o700)

    def _path(self, record_id: str) -> Path:
        if not _SAFE_ID.fullmatch(record_id):
            raise LearnerStoreError("record_id must be a safe identifier")
        return self.root / f"{record_id}.json"

    def _validate(self, payload: Mapping[str, Any]) -> None:
        if set(payload) - _ALLOWED_KEYS:
            raise LearnerStoreError("record contains fields outside the allowlist")
        selected = payload.get("selected_index")
        if type(selected) is not int or selected < 0:
            raise LearnerStoreError("selected_index must be a non-negative integer")
        submitted = payload.get("submitted_at_ms")
        if type(submitted) is not int or submitted < 0:
            raise LearnerStoreError("submitted_at_ms must be a non-negative integer")

    def put(self, record_id: str, payload: Mapping[str, Any]) -> None:
        self._validate(payload)
        destination = self._path(record_id)
        fd, temporary = tempfile.mkstemp(dir=self.root, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(dict(payload), handle, sort_keys=True)
        os.chmod(temporary, 0o600)
        os.replace(temporary, destination)

    def get(self, record_id: str) -> dict[str, Any]:
        return json.loads(self._path(record_id).read_text(encoding="utf-8"))

    def delete(self, record_id: str) -> bool:
        path = self._path(record_id)
        try:
            path.unlink()
        except FileNotFoundError:
            return False
        return True

    def count(self) -> int:
        return len(list(self.root.glob("*.json")))

    def audit(self) -> dict[str, Any]:
        digests = []
        for path in sorted(self.root.glob("*.json")):
            digests.append(hashlib.sha256(path.read_bytes()).hexdigest())
        combined = hashlib.sha256("".join(sorted(digests)).encode("utf-8")).hexdigest()
        return {"files": len(digests), "sha256": combined}
