"""Adaptor Șansă Dublă — un workbook pe meci (Input_Meci vertical)."""

from __future__ import annotations

from datetime import timezone
from pathlib import Path

from src.adapters.base import BaseAdapter
from src.excel.generator import unix_to_excel_serial
from src.excel.integrity import IntegrityError
from src.models.match_data import MatchData


class DoubleChanceAdapter(BaseAdapter):
    model_id = "double_chance"

    def build_whitelist(self) -> set[str]:
        wl = super().build_whitelist()
        for cell in (
            "C5", "B5", "B6", "B7", "B28", "B29", "B30", "B31", "B32", "B33",
            "B34", "B36", "C36", "B42", "B4", "C4",
        ):
            wl.add(f"Input_Meci!{cell}")
        # Surse_Date: doar status + sursă pe rânduri fără formulă pe D/G/H
        for cell in ("C5", "C8", "C9", "D5"):
            wl.add(f"Surse_Date!{cell}")
        return wl

    def write_matches(self, matches: list[MatchData], dest: Path) -> Path:
        """Pentru un singur meci — dest este calea fișierului final."""
        if len(matches) != 1:
            raise IntegrityError("EXPORT BLOCAT. Motiv: adaptorul Șansă Dublă acceptă un singur meci per fișier.")
        match = matches[0]
        self.prepare_copy(dest)
        writer = self.open_writer(dest)

        def n(ind):
            return ind.numeric_or_none()

        date_serial = None
        if match.kickoff_utc is not None:
            date_serial = unix_to_excel_serial(
                match.kickoff_utc.replace(tzinfo=timezone.utc).timestamp()
            )

        o1, ox, o2 = n(match.odds_ft_1), n(match.odds_ft_x), n(match.odds_ft_2)
        p1 = px = p2 = None
        odds_1x = odds_x2 = odds_12 = None
        if o1 and ox and o2 and o1 > 1 and ox > 1 and o2 > 1:
            inv = (1 / o1) + (1 / ox) + (1 / o2)
            p1, px, p2 = (1 / o1) / inv, (1 / ox) / inv, (1 / o2) / inv
            # cote double chance aproximative din prob de-vig
            odds_1x = 1 / (p1 + px) if (p1 + px) > 0 else None
            odds_x2 = 1 / (px + p2) if (px + p2) > 0 else None
            odds_12 = 1 / (p1 + p2) if (p1 + p2) > 0 else None

        writes = {
            ("Input_Meci", "B4"): match.home.name,
            ("Input_Meci", "C4"): match.away.name,
            ("Input_Meci", "B5"): match.competition_name,
            ("Input_Meci", "C5"): match.competition_name,
            ("Input_Meci", "B6"): date_serial,
            ("Input_Meci", "B7"): "NU",
            ("Input_Meci", "B28"): p1,
            ("Input_Meci", "B29"): px,
            ("Input_Meci", "B30"): p2,
            ("Input_Meci", "B31"): odds_1x,
            ("Input_Meci", "B32"): odds_x2,
            ("Input_Meci", "B33"): odds_12,
            ("Input_Meci", "B36"): n(match.home.matches_played_home),
            ("Input_Meci", "C36"): n(match.away.matches_played_away),
            ("Input_Meci", "B34"): "B",
            ("Input_Meci", "B42"): "FootyStats 1X2",
            ("Surse_Date", "C5"): "VERIFIED / DERIVED",
            ("Surse_Date", "D5"): "FootyStats",
            ("Surse_Date", "C8"): (
                "VERIFIED / DERIVED"
                if not match.odds_ft_1.is_unavailable()
                else "NOT AVAILABLE"
            ),
            ("Surse_Date", "C9"): (
                "AVAILABLE - NOT CHECKED"
                if (n(match.home.matches_played_home) or 99) < 8
                else "VERIFIED / DERIVED"
            ),
        }
        for (sheet, cell), value in writes.items():
            writer.write(sheet, cell, value)

        return writer.save()
