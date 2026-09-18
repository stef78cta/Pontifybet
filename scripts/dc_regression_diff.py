"""Compară două snapshot-uri Șansă Dublă și scrie diferențele celulă cu celulă.

Rulare:
    .venv\\Scripts\\python.exe scripts/dc_regression_diff.py baseline.csv after.csv diff.csv

Orice rând din diff trebuie clasificat manual în raportul de audit. Un diff gol
înseamnă NO NUMERIC CHANGE pentru întreg setul de control.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path


def _load(path: Path) -> dict[tuple[str, str, str], dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return {
            (row["source"], row["case_id"], row["selection"]): row for row in reader
        }


def main() -> None:
    baseline = _load(Path(sys.argv[1]))
    after = _load(Path(sys.argv[2]))
    dest = Path(sys.argv[3])

    rows: list[list[str]] = []
    for key in sorted(set(baseline) | set(after)):
        before = baseline.get(key)
        now = after.get(key)
        if before is None or now is None:
            rows.append([*key, "<rând>", str(before is not None), str(now is not None)])
            continue
        for column in before:
            if column in {"source", "case_id", "selection"}:
                continue
            if before[column] != now.get(column):
                rows.append([*key, column, before[column], now.get(column, "")])

    with dest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["source", "case_id", "selection", "camp", "baseline", "after"])
        writer.writerows(rows)
    print(f"{len(rows)} diff rows -> {dest}")


if __name__ == "__main__":
    main()
