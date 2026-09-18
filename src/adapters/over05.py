"""Adaptor Over 0.5 — scrie inputurile mapate și rezultatele Python în HL:HR."""

from __future__ import annotations

from datetime import timezone
from pathlib import Path

from src.adapters.base import BaseAdapter
from src.engines.over05 import (
    PYTHON_RESULT_COLUMNS,
    compute_over05,
    match_to_over05_inputs,
    python_result_values,
)
from src.engines.over05.inputs import INPUT_COLUMNS
from src.excel.generator import unix_to_excel_serial
from src.models.match_data import MatchData


class Over05Adapter(BaseAdapter):
    model_id = "over05"

    def write_matches(self, matches: list[MatchData], dest: Path) -> Path:
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
            mapping = self._row_values(match)
            for col, value in mapping.items():
                if col == "FB" or value is None:
                    continue
                writer.write(sheet, f"{col}{row}", value)

        return writer.save()

    def _row_values(self, match: MatchData) -> dict[str, object]:
        """Inputuri mapate + verdictul Python, fără a atinge formulele GL:HK."""
        values = match_to_over05_inputs(match)
        official = compute_over05(values)
        values.update(python_result_values(official))
        kickoff = match.kickoff_utc
        if kickoff is not None:
            values["C"] = unix_to_excel_serial(kickoff.replace(tzinfo=timezone.utc).timestamp())
        return {col: value for col, value in values.items() if col != "FB"}
