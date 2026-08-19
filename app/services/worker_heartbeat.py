"""Lightweight worker heartbeat persisted in shared storage."""

from datetime import datetime, timezone
from pathlib import Path

from app.config import settings


class WorkerHeartbeat:
    """Persist worker liveness without requiring a schema migration."""

    def __init__(self, storage_path: str | None = None) -> None:
        root = Path(storage_path or settings.STORAGE_PATH)
        self.path = root / ".amip-worker-heartbeat"

    def touch(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(datetime.now(timezone.utc).isoformat(), encoding="utf-8")

    def age_seconds(self) -> float | None:
        if not self.path.exists():
            return None
        modified = datetime.fromtimestamp(self.path.stat().st_mtime, tz=timezone.utc)
        return max(0.0, (datetime.now(timezone.utc) - modified).total_seconds())
