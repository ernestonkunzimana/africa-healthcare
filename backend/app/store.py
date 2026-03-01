from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Any

from .config import settings


class JsonStore:
    def __init__(self, filename: str) -> None:
        self._filename = filename
        self._lock = Lock()

    def _path(self) -> Path:
        directory = Path(settings.storage_dir)
        directory.mkdir(parents=True, exist_ok=True)
        return directory / self._filename

    def load(self, default: Any) -> Any:
        with self._lock:
            path = self._path()
            if not path.exists():
                return default
            return json.loads(path.read_text())

    def save(self, data: Any) -> None:
        with self._lock:
            path = self._path()
            tmp = path.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, separators=(",", ":")))
            tmp.replace(path)


consent_store = JsonStore("consents.json")
preference_store = JsonStore("preferences.json")
audit_store = JsonStore("audit.json")
