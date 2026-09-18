"""Adaptor Over 0.5 — scrie pe Analize meciuri, rânduri A–BI."""

from __future__ import annotations

from datetime import timezone
from pathlib import Path

from src.adapters.base import BaseAdapter
from src.excel.generator import unix_to_excel_serial
from src.models.match_data import MatchData


class Over05Adapter(BaseAdapter):
    model_id = "over05"

    def write_matches(self, matches: list[MatchData], dest: Path) -> Path:
        self.prepare_copy(dest)
        writer = self.open_writer(dest)
        sheet = self.cfg["input_sheet"]
        start = int(self.cfg.get("data_start_row", 4))

        # Curăță rândurile demo (4–20) pe coloanele whitelist, fără a atinge formule
        clear_cols = self.cfg.get("write_columns") or []
        for row in range(start, start + 20):
            for col in clear_cols:
                # Nu ștergem dacă e în afara — whitelist deja acoperă
                try:
                    writer.write(sheet, f"{col}{row}", None)
                except Exception:
                    pass

        for idx, match in enumerate(matches):
            row = start + idx
            mapping = self._row_values(match)
            for col, value in mapping.items():
                writer.write(sheet, f"{col}{row}", value)

        return writer.save()

    def _row_values(self, match: MatchData) -> dict[str, object]:
        kickoff = match.kickoff_utc
        date_serial = None
        if kickoff is not None:
            date_serial = unix_to_excel_serial(kickoff.replace(tzinfo=timezone.utc).timestamp())

        def n(ind) -> float | int | None:
            return ind.numeric_or_none()

        return {
            "A": match.match_id,
            "B": "LIVE",
            "C": date_serial,
            "D": match.competition_name,
            "E": "Campionat intern",
            "F": match.round or "",
            "G": match.home.name,
            "H": match.away.name,
            "I": n(match.home.matches_played_home),
            "J": n(match.home.goals_for_home),
            "K": n(match.home.goals_against_home),
            "L": n(match.home.xg_for_home),
            "M": n(match.home.xg_against_home),
            "N": n(match.home.over05_pct_home),
            "O": n(match.home.fts_pct_home),
            "P": n(match.away.matches_played_away),
            "Q": n(match.away.goals_for_away),
            "R": n(match.away.goals_against_away),
            "S": n(match.away.xg_for_away),
            "T": n(match.away.xg_against_away),
            "U": n(match.away.over05_pct_away),
            "V": n(match.away.fts_pct_away),
            "W": n(match.home.last5_n),
            "X": n(match.home.last5_gf),
            "Y": n(match.home.last5_ga),
            "Z": n(match.home.last5_xgf),
            "AA": n(match.home.last5_xga),
            "AB": n(match.away.last5_n),
            "AC": n(match.away.last5_gf),
            "AD": n(match.away.last5_ga),
            "AE": n(match.away.last5_xgf),
            "AF": n(match.away.last5_xga),
            "AG": n(match.h2h_n),
            "AO": n(match.odds_ft_1),
            "AP": n(match.odds_ft_x),
            "AQ": n(match.odds_ft_2),
            "AR": n(match.odds_ft_over05),
            "AS": n(match.odds_ft_under05),
            "AT": 3,
            "BI": "https://footystats.org/",
        }
