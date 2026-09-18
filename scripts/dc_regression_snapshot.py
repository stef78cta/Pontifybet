"""Snapshot de regresie pentru Șansă Dublă V2.

Scrie un CSV cu toate celulele oficiale pentru cele 37 de fixture-uri Excel plus
rândurile produse de pipeline-ul MOCK. Folosit ca baseline/after în auditul de
paritate: orice diferență numerică între două snapshot-uri trebuie explicată.

Rulare:
    .venv\\Scripts\\python.exe scripts/dc_regression_snapshot.py <cale_csv>
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.api.mock import MockFootyStatsClient  # noqa: E402
from src.engines.double_chance import (  # noqa: E402
    compute_double_chance,
    match_to_double_chance_inputs,
)

SPEC = ROOT / "docs" / "PontifyBet_Sansa_Dubla_V2_Pachet_Cursor"
COLUMNS = (
    "B", "D", "E", "F", "H", "I", "K", "L", "M", "N",
    "O", "P", "Q", "T", "U", "X", "Y", "AA", "AB", "AC", "AD", "AE", "AF",
)
HEADER = ["source", "case_id", "selection", *COLUMNS]


def _rows_for(source: str, case_id: str, inputs: dict) -> list[list[object]]:
    result = compute_double_chance(inputs)
    out: list[list[object]] = []
    for code, row in (("1X", 4), ("X2", 5), ("12", 6)):
        values = [result.cells.get(f"Double_Chance!{col}{row}") for col in COLUMNS]
        out.append([source, case_id, code, *values])
    return out


def main() -> None:
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dc_snapshot.csv"
    rows: list[list[object]] = []

    cases = json.loads((SPEC / "cazuri_test.json").read_text(encoding="utf-8"))["cases"]
    for case in cases:
        rows.extend(_rows_for("fixture", case["id"], case["inputs"]))

    client = MockFootyStatsClient()
    for raw in client.matches_by_date("2026-03-15"):
        match = client.enrich_match(raw)
        rows.extend(_rows_for("mock", match.match_id, match_to_double_chance_inputs(match)))
        # Varianta early-season a aceluiași meci: ramura prior/shrinkage.
        match.home.matches_played_home.value = 6
        match.away.matches_played_away.value = 5
        rows.extend(
            _rows_for("mock_small", match.match_id, match_to_double_chance_inputs(match))
        )

    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(HEADER)
        writer.writerows(rows)
    print(f"{len(rows)} rows -> {dest}")


if __name__ == "__main__":
    main()
