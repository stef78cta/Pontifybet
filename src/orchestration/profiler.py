"""Timing minimal și contoare pentru fluxul de analiză."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class FetchCounters:
    """Contoare operaționale — fără date sensibile."""

    league_teams: int = 0
    league_matches: int = 0
    lastx_5: int = 0
    lastx_10: int = 0
    team: int = 0
    derived_1x2_trace: int = 0
    compute_over05: int = 0
    compute_double_chance: int = 0
    compute_corners: int = 0


@dataclass
class RunProfiler:
    """Măsoară faze și durate cu `time.perf_counter()`."""

    counters: FetchCounters = field(default_factory=FetchCounters)
    phases: dict[str, float] = field(default_factory=dict)
    _marks: dict[str, float] = field(default_factory=dict)
    time_to_table: float | None = None
    time_to_export: float | None = None
    total: float | None = None

    def start(self, name: str) -> None:
        self._marks[name] = time.perf_counter()

    def stop(self, name: str) -> None:
        started = self._marks.pop(name, None)
        if started is None:
            return
        self.phases[name] = self.phases.get(name, 0.0) + (time.perf_counter() - started)

    def mark_time_to_table(self) -> None:
        if self.time_to_table is None:
            self.time_to_table = sum(self.phases.values())

    def mark_time_to_export(self) -> None:
        self.time_to_export = sum(self.phases.values())

    def finalize_total(self) -> None:
        self.total = sum(self.phases.values())

    def to_dict(self) -> dict[str, Any]:
        return {
            "phases_sec": dict(self.phases),
            "counters": {
                "league_teams": self.counters.league_teams,
                "league_matches": self.counters.league_matches,
                "lastx_5": self.counters.lastx_5,
                "lastx_10": self.counters.lastx_10,
                "team": self.counters.team,
                "derived_1x2_trace": self.counters.derived_1x2_trace,
                "compute_over05": self.counters.compute_over05,
                "compute_double_chance": self.counters.compute_double_chance,
                "compute_corners": self.counters.compute_corners,
            },
            "time_to_table_sec": self.time_to_table,
            "time_to_export_sec": self.time_to_export,
            "total_sec": self.total,
        }
