"""Adaptor Șansă Dublă — un workbook pe meci (Input_Meci vertical)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.adapters.base import BaseAdapter
from src.engines.double_chance import python_result_writes
from src.engines.double_chance.engine import DoubleChanceOfficialResult
from src.excel.integrity import IntegrityError
from src.models.match_data import MatchData
from src.orchestration.snapshot import DoubleChanceMatchArtifacts

_PYTHON_RESULT_COORDS = tuple(
    f"{col}{row}" for row in range(60, 64) for col in ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J")
)


class DoubleChanceAdapter(BaseAdapter):
    model_id = "double_chance"

    def build_whitelist(self) -> set[str]:
        wl = super().build_whitelist()
        for cell in (
            "B4",
            "C4",
            "B5",
            "C5",
            "B6",
            "B7",
            "B12",
            "C12",
            "B13",
            "C13",
            "B14",
            "C14",
            "B15",
            "C15",
            "B16",
            "C16",
            "B17",
            "C17",
            "B21",
            "C21",
            "B22",
            "C22",
            "B28",
            "B29",
            "B30",
            "B31",
            "B32",
            "B33",
            "B34",
            "B36",
            "C36",
            "B37",
            "B38",
            "B43",
            "C41",
            "B42",
            *_PYTHON_RESULT_COORDS,
        ):
            wl.add(f"Input_Meci!{cell}")
        for cell in (
            "B6",
            "C6",
            "D6",
            "B7",
            "C7",
            "D7",
        ):
            wl.add(f"Model_1X2!{cell}")
        for cell in (
            "C5",
            "D5",
            "E5",
            "F5",
            "I5",
            "J5",
            "C6",
            "D6",
            "E6",
            "F6",
            "I6",
            "J6",
            "C7",
            "D7",
            "E7",
            "F7",
            "I7",
            "J7",
            "C8",
            "E8",
            "F8",
            "I8",
            "J8",
            "C9",
            "D9",
            "E9",
            "F9",
            "I9",
            "J9",
            "C10",
            "D10",
            "E10",
            "F10",
            "G10",
            "H10",
            "I10",
            "J10",
            "K10",
            "C11",
            "D11",
            "E11",
            "F11",
            "I11",
            "J11",
            "K11",
        ):
            wl.add(f"Surse_Date!{cell}")
        return wl

    def write_matches(
        self,
        matches: list[MatchData],
        dest: Path,
        *,
        artifacts: dict[str, DoubleChanceMatchArtifacts] | None = None,
    ) -> Path:
        """Pentru un singur meci — dest este calea fișierului final."""
        if len(matches) != 1:
            raise IntegrityError(
                "EXPORT BLOCAT. Motiv: adaptorul Șansă Dublă acceptă un singur meci per fișier."
            )
        match = matches[0]
        self.prepare_copy(dest)
        writer = self.open_writer(dest)
        bundle = artifacts.get(match.match_id) if artifacts else None
        if bundle is not None:
            mapping = dict(bundle.mapping)
            official = bundle.official
        else:
            from src.engines.double_chance import compute_double_chance, match_to_double_chance_inputs

            mapping = match_to_double_chance_inputs(match)
            official = compute_double_chance(mapping)
        mapping.update(
            {f"Input_Meci!{coord}": value for coord, value in python_result_writes(official).items()}
        )
        if match.competition_name:
            mapping.setdefault("Input_Meci!C5", match.competition_name)
        for addr, value in mapping.items():
            if value is None:
                continue
            sheet, cell = addr.split("!", 1)
            writer.write(sheet, cell, value)
        return writer.save()
