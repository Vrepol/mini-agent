"""Chapter 02: conversation state and a minimal local session store."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from uuid import UUID, uuid4


@dataclass
class Session:
    id: str = field(default_factory=lambda: str(uuid4()))
    workspace: str = "."
    messages: list[dict] = field(default_factory=list)
    status: str = "idle"  # idle / running / interrupted / paused
    total_steps: int = 0
    pending_tool_calls: list[dict] = field(default_factory=list)


class JsonSessionStore:
    """Single-process teaching store; not a transactional database."""

    def __init__(self, directory: str | Path = ".sessions"):
        self.directory = Path(directory).resolve()
        self.directory.mkdir(parents=True, exist_ok=True)

    def _path(self, session_id: str) -> Path:
        # A UUID-only filename prevents "../" path traversal.
        UUID(session_id)
        return self.directory / f"{session_id}.json"

    def save(self, session: Session) -> None:
        path = self._path(session.id)
        # Replace avoids a partially written JSON file in common failures.
        # TODO(DIY-02): add file locking and durable fsync semantics.
        tmp = self.directory / f".{session.id}.{uuid4().hex}.tmp"
        try:
            tmp.write_text(
                json.dumps(asdict(session), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            tmp.replace(path)
        finally:
            tmp.unlink(missing_ok=True)

    def load(self, session_id: str) -> Session:
        data = json.loads(self._path(session_id).read_text(encoding="utf-8"))
        session = Session(**data)
        if session.status == "running":
            # Crash recovery cannot assume an external tool did not execute.
            session.status = "interrupted"
            self.save(session)
        return session

    def list_sessions(self) -> list[Session]:
        # TODO(DIY-02): add updated_at and sort by latest activity.
        result: list[Session] = []
        for path in self.directory.glob("*.json"):
            try:
                result.append(self.load(path.stem))
            except (ValueError, TypeError, OSError, json.JSONDecodeError):
                continue
        return sorted(result, key=lambda item: item.id)
