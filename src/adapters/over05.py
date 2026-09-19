"""Adaptor Over 0.5 — scrie inputurile mapate și rezultatele Python în HL:HR."""

from __future__ import annotations

from datetime import timezone
from pathlib import Path
from typing import Any

from src.adapters.base import BaseAdapter
from src.engines.over05 import (
    PYTHON_RESULT_COLUMNS,
    match_to_over05_inputs,
    python_result_values,
)
from src.engines.over05.engine import Over05OfficialResult
from src.engines.over05.inputs import INPUT_COLUMNS
from src.excel.generator import unix_to_excel_serial
from src.models.match_data import MatchData


class Over05Adapter(BaseAdapter):
    model_id = "over05"

    def write_matches(
        self,
        matches: list[MatchData],
        dest: Path,
        *,
        artifacts: dict[str, tuple[dict[str, Any], Over05OfficialResult]] | None = None,
    ) -> Path:
        self.prepare_copy(dest)
        writer = self.open_writer(dest)
        sheet = self.cfg["input_sheet"]
        start = int(self.cfg.get("data_start_row", 4))
        header_row = int(self.cfg.get("header_row", 3))
        clear_cols = self.cfg.get("write_columns") or list(INPUT_COLUMNS)

        for row in range(start, start + 20):
            for col in clear_cols:
                if col == "FB":
                    continue
                try:
                    writer.write(sheet, f"{col}{row}", None)
                except Exception:
                    pass

        for col, title in PYTHON_RESULT_COLUMNS.items():
            writer.write(sheet, f"{col}{header_row}", title)

        for idx, match in enumerate(matches):
            row = start + idx
            mapping = self._row_values(match, artifacts=artifacts)
            for col, value in mapping.items():
                if col == "FB" or value is None:
                    continue
                writer.write(sheet, f"{col}{row}", value)

        return writer.save()

    def _row_values(
        self,
        match: MatchData,
        *,
        artifacts: dict[str, tuple[dict[str, Any], Over05OfficialResult]] | None = None,
    ) -> dict[str, object]:
        """Inputuri mapate + verdictul Python, fără a atinge formulele GL:HK."""
        bundle = artifacts.get(match.match_id) if artifacts else None
        if bundle is not None:
            values = dict(bundle[0])
            official = bundle[1]
        else:
            from src.engines.over05 import compute_over05

            values = match_to_over05_inputs(match)
            official = compute_over05(values)
        values.update(python_result_values(official))
        kickoff = match.kickoff_utc
        if kickoff is not None:
            values["C"] = unix_to_excel_serial(kickoff.replace(tzinfo=timezone.utc).timestamp())
        return {col: value for col, value in values.items() if col != "FB"}
