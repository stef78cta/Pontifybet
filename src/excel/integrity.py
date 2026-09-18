"""Integritate workbook: amprentă formule/foi + verificare post-scriere."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from openpyxl import load_workbook
from openpyxl.workbook.workbook import Workbook


@dataclass
class WorkbookFingerprint:
    sheet_names: list[str]
    formulas: dict[str, str]  # "Sheet!A1" -> formula
    version_hints: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "sheet_names": self.sheet_names,
            "formula_count": len(self.formulas),
            "version_hints": self.version_hints,
        }


class IntegrityError(Exception):
    """Export blocat din cauza integrității."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def _cell_key(sheet: str, coord: str) -> str:
    return f"{sheet}!{coord}"


def fingerprint_workbook(path: Path | Workbook, max_rows: int = 200, max_cols: int = 120) -> WorkbookFingerprint:
    """Creează amprenta foilor + formulelor."""
    close_after = False
    if isinstance(path, Path):
        wb = load_workbook(path, data_only=False)
        close_after = True
    else:
        wb = path

    formulas: dict[str, str] = {}
    hints: list[str] = []
    for name in wb.sheetnames:
        ws = wb[name]
        if name.upper().startswith("CHANGELOG") or "DOCUMENT" in name.upper():
            for row in ws.iter_rows(max_row=30, max_col=5):
                for cell in row:
                    if isinstance(cell.value, str) and cell.value.strip():
                        hints.append(f"{name}:{cell.value.strip()[:80]}")
                        if len(hints) >= 5:
                            break
        for row in ws.iter_rows(min_row=1, max_row=max_rows, max_col=max_cols):
            for cell in row:
                if isinstance(cell.value, str) and cell.value.startswith("="):
                    formulas[_cell_key(name, cell.coordinate)] = cell.value

    fp = WorkbookFingerprint(sheet_names=list(wb.sheetnames), formulas=formulas, version_hints=hints[:5])
    if close_after:
        wb.close()
    return fp


def compare_fingerprints(before: WorkbookFingerprint, after: WorkbookFingerprint) -> None:
    """Ridică IntegrityError dacă foile/formulele s-au schimbat."""
    deleted = set(before.sheet_names) - set(after.sheet_names)
    renamed_or_added = set(after.sheet_names) - set(before.sheet_names)
    if deleted or renamed_or_added:
        raise IntegrityError(
            f"EXPORT BLOCAT. Motiv: foi șterse/redenumite ({sorted(deleted)} / {sorted(renamed_or_added)})."
        )

    for key, formula in before.formulas.items():
        if key not in after.formulas:
            raise IntegrityError(f"EXPORT BLOCAT. Motiv: formula {key} a fost eliminată.")
        if after.formulas[key] != formula:
            raise IntegrityError(f"EXPORT BLOCAT. Motiv: formula {key} a fost modificată.")

    # Formule noi pe celule care erau fără formulă = suspect
    new_formulas = set(after.formulas) - set(before.formulas)
    if new_formulas:
        sample = sorted(new_formulas)[0]
        raise IntegrityError(f"EXPORT BLOCAT. Motiv: formula {sample} a fost modificată.")


def assert_whitelist_write(
    sheet: str,
    coordinate: str,
    whitelist: set[str],
) -> None:
    """Whitelist conține chei Sheet!A1 sau Sheet!A (coloană pe multi-row)."""
    key = f"{sheet}!{coordinate}"
    col = "".join(ch for ch in coordinate if ch.isalpha())
    col_key = f"{sheet}!{col}"
    if key not in whitelist and col_key not in whitelist:
        raise IntegrityError(
            f"EXPORT BLOCAT. Motiv: scriere în afara listei albe ({key})."
        )


def count_formulas(path: Path) -> int:
    return len(fingerprint_workbook(path).formulas)
