"""Cele 14 linii Cornere V14, în ordinea din `Analiza_Linii` / `Calibrare_Linii`.

Ordinea este parte din model: `Rank_In_Match` și `Rank_LIVE` sparg egalitățile
prin poziția liniei în bloc, deci lista nu poate fi reordonată. Valorile sunt
verificate față de șablon în `tests/test_corners_excel_parity.py`.
"""

from __future__ import annotations

from dataclasses import dataclass

#: Numărul de rânduri pe care fiecare meci ocupă în `Analiza_Linii`.
LINES_PER_SLOT = 14


@dataclass(frozen=True)
class CornersLine:
    """O linie Cornere: eticheta din workbook plus pragul numeric asociat."""

    offset: int
    """Poziția în blocul slotului (0–13), folosită la spargerea egalităților."""

    label: str
    """Eticheta exactă din workbook, cu virgulă zecimală (`O3,5`)."""

    market_type: str
    """`OVER` sau `UNDER`, conform coloanei `Type`."""

    k: int
    """Pragul întreg din coloana `k`; linia comercială este `k + 0.5`."""

    @property
    def line(self) -> float:
        """Pragul comercial (`3` → `3.5`), formatul folosit de istoricul SQLite."""
        return self.k + 0.5

    @property
    def is_over(self) -> bool:
        return self.market_type == "OVER"


CORNERS_LINES: tuple[CornersLine, ...] = (
    CornersLine(0, "O3,5", "OVER", 3),
    CornersLine(1, "O4,5", "OVER", 4),
    CornersLine(2, "O5,5", "OVER", 5),
    CornersLine(3, "O6,5", "OVER", 6),
    CornersLine(4, "O7,5", "OVER", 7),
    CornersLine(5, "O8,5", "OVER", 8),
    CornersLine(6, "U10,5", "UNDER", 10),
    CornersLine(7, "U11,5", "UNDER", 11),
    CornersLine(8, "U12,5", "UNDER", 12),
    CornersLine(9, "U13,5", "UNDER", 13),
    CornersLine(10, "U14,5", "UNDER", 14),
    CornersLine(11, "U15,5", "UNDER", 15),
    CornersLine(12, "U16,5", "UNDER", 16),
    CornersLine(13, "U17,5", "UNDER", 17),
)

assert len(CORNERS_LINES) == LINES_PER_SLOT


def line_by_label(label: str) -> CornersLine:
    """Caută o linie după eticheta din workbook."""
    for line in CORNERS_LINES:
        if line.label == label:
            return line
    raise KeyError(label)
