"""Cache determinist pentru apeluri FootyStats (memorie + fișiere locale)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from config.settings import CACHE_DIR, ensure_runtime_dirs


def cache_key(endpoint: str, params: dict[str, Any]) -> str:
    """Cheie deterministă pe endpoint + parametri (fără cheia API)."""
    safe = {k: v for k, v in sorted(params.items()) if k != "key"}
    raw = json.dumps({"endpoint": endpoint, "params": safe}, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class ResponseCache:
    """Cache pe rulare (dict) + opțional pe disc în `.cache/`."""

    def __init__(self, use_disk: bool = True) -> None:
        self._memory: dict[str, Any] = {}
        self.use_disk = use_disk
        if use_disk:
            ensure_runtime_dirs()

    def get(self, key: str) -> Any | None:
        if key in self._memory:
            return self._memory[key]
        if not self.use_disk:
            return None
        path = CACHE_DIR / f"{key}.json"
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            self._memory[key] = data
            return data
        return None

    def set(self, key: str, value: Any) -> None:
        self._memory[key] = value
        if self.use_disk:
            path = CACHE_DIR / f"{key}.json"
            path.write_text(json.dumps(value, ensure_ascii=False, default=str), encoding="utf-8")

    def clear_memory(self) -> None:
        self._memory.clear()
