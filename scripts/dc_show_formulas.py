"""Tipărește formulele native din workbook pentru celulele cerute.

Rulare: .venv\\Scripts\\python.exe scripts/dc_show_formulas.py Foaie!A1 Foaie!B2 ...
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from openpyxl import load_workbook  # noqa: E402

from config.settings import TEMPLATES_DIR  # noqa: E402

WORKBOOK = TEMPLATES_DIR / "11_model_analiza_pariu_sansadubla_optimizat_V2.xlsx"


def main() -> None:
    wb = load_workbook(WORKBOOK, data_only=False)
    for addr in sys.argv[1:]:
        sheet, _, ref = addr.partition("!")
        value = wb[sheet][ref].value
        print(f"{addr:24s} = {value!r}")


if __name__ == "__main__":
    main()
