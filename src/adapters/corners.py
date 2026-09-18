"""Adaptor Cornere Multi-Line V14 — Input_Meci A–AG pe rânduri."""

from __future__ import annotations

from datetime import timedelta, timezone
from pathlib import Path

from src.adapters.base import BaseAdapter
from src.excel.generator import unix_to_excel_serial
from src.models.match_data import MatchData


class CornersAdapter(BaseAdapter):
    model_id = "corners"

    def write_matches(self, matches: list[MatchData], dest: Path) -> Path:
        self.prepare_copy(dest)
        writer = self.open_writer(dest)
        sheet = self.cfg["input_sheet"]
        start = int(self.cfg.get("data_start_row", 6))
        clear_cols = self.cfg.get("write_columns") or []

        for row in range(start, start + 15):
            for col in clear_cols:
                try:
                    writer.write(sheet, f"{col}{row}", None)
                except Exception:
                    pass

        for idx, match in enumerate(matches):
            row = start + idx
            for col, value in self._row_values(match).items():
                writer.write(sheet, f"{col}{row}", value)

        return writer.save()

    def _row_values(self, match: MatchData) -> dict[str, object]:
        def n(ind):
            return ind.numeric_or_none()

        kick = match.kickoff_utc
        kick_serial = None
        cutoff_serial = None
        if kick is not None:
            ts = kick.replace(tzinfo=timezone.utc).timestamp()
            kick_serial = unix_to_excel_serial(ts)
            cutoff_serial = unix_to_excel_serial((kick - timedelta(hours=1)).timestamp())

        # Bundle G0 native corners în Notes (coloane dedicate native lipsesc în layout input)
        notes = (
            f"corners_native|"
            f"H_s_for={n(match.home.corners_for_overall)};"
            f"H_s_ag={n(match.home.corners_against_overall)};"
            f"H_h_for={n(match.home.corners_for_home)};"
            f"H_h_ag={n(match.home.corners_against_home)};"
            f"H_r_for={n(match.home.last5_corners_for)};"
            f"H_r_ag={n(match.home.last5_corners_against)};"
            f"A_s_for={n(match.away.corners_for_overall)};"
            f"A_s_ag={n(match.away.corners_against_overall)};"
            f"A_a_for={n(match.away.corners_for_away)};"
            f"A_a_ag={n(match.away.corners_against_away)};"
            f"A_r_for={n(match.away.last5_corners_for)};"
            f"A_r_ag={n(match.away.last5_corners_against)};"
            f"H_n={n(match.home.matches_played_overall)};"
            f"A_n={n(match.away.matches_played_overall)}"
        )

        return {
            "A": match.match_id,
            "B": match.competition_name,
            "C": match.season,
            "D": match.home.name,
            "E": match.away.name,
            "F": kick_serial,
            "G": cutoff_serial,
            "H": "LIVE",
            "I": "AUTO",
            "M": notes,
        }
