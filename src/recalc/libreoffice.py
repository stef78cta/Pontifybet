"""Stub recalculare LibreOffice — dezactivat în MVP."""

from __future__ import annotations

from pathlib import Path


class LibreOfficeRecalcService:
    """Pregătit pentru activare ulterioară; nu rulează în MVP."""

    enabled: bool = False

    def recalculate(self, workbook_path: Path) -> Path:
        if not self.enabled:
            raise RuntimeError(
                "Recalcularea LibreOffice este dezactivată. "
                "Deschide fișierul în Microsoft Excel pentru recalculare."
            )
        raise NotImplementedError("LibreOffice headless nu este activat în MVP.")
