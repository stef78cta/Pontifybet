#!/usr/bin/env python3
"""Inspectează un șablon Excel read-only: foi, formule vs valori, data validations."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from openpyxl import load_workbook


def inspect(path: Path, sheet_name: str | None = None, max_rows: int = 20) -> None:
    wb = load_workbook(path, data_only=False, read_only=True)
    print(f"FILE: {path.name}")
    print(f"SHEETS ({len(wb.sheetnames)}): {', '.join(wb.sheetnames)}")
    sheets = [sheet_name] if sheet_name else wb.sheetnames
    for name in sheets:
        if name not in wb.sheetnames:
            print(f"MISSING SHEET: {name}")
            continue
        ws = wb[name]
        formulas = 0
        values = 0
        samples_f: list[str] = []
        samples_v: list[str] = []
        for row in ws.iter_rows(max_row=max_rows):
            for cell in row:
                if cell.value is None:
                    continue
                addr = f"{cell.coordinate}"
                if isinstance(cell.value, str) and cell.value.startswith("="):
                    formulas += 1
                    if len(samples_f) < 8:
                        samples_f.append(addr)
                else:
                    values += 1
                    if len(samples_v) < 8:
                        samples_v.append(f"{addr}={cell.value!r}"[:60])
        print(f"\n[{name}] formulas~{formulas} values~{values} (first {max_rows} rows)")
        print(f"  formula samples: {samples_f}")
        print(f"  value samples: {samples_v}")
    wb.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect Excel template (read-only)")
    parser.add_argument("path", type=Path)
    parser.add_argument("--sheet", default=None)
    parser.add_argument("--rows", type=int, default=20)
    args = parser.parse_args()
    if not args.path.exists():
        print(f"Not found: {args.path}", file=sys.stderr)
        return 1
    inspect(args.path, args.sheet, args.rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
