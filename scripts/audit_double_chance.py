"""Dump de audit pentru Șansă Dublă V2: lanțul complet de celule Excel per selecție.

Rulare: .venv\\Scripts\\python.exe scripts/audit_double_chance.py [fixture_id ...]

Nu modifică nimic; doar evaluează șablonul cu inputurile date și tipărește
celulele din lanțul P_model → Pfail → haircut → gates → scor → verdict.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.engines.double_chance import compute_double_chance  # noqa: E402

SPEC = ROOT / "docs" / "PontifyBet_Sansa_Dubla_V2_Pachet_Cursor"

CHAIN_COLUMNS = ("B", "D", "X", "Y", "E", "F", "H", "O", "P", "Q", "T", "U", "L", "M", "N", "AA", "AD", "AE")
CONTEXT_CELLS = (
    "Model_1X2!J6",
    "Model_1X2!K6",
    "Model_1X2!L6",
    "Model_1X2!J7",
    "Model_1X2!K7",
    "Model_1X2!L7",
    "Model_1X2!J8",
    "Model_1X2!K8",
    "Model_1X2!L8",
    "Model_1X2!B10",
    "Model_1X2!C10",
    "Model_1X2!D10",
    "Uncertainty_v2!B4",
    "Uncertainty_v2!B5",
    "Uncertainty_v2!B7",
    "Uncertainty_v2!B8",
    "Uncertainty_v2!B9",
    "Uncertainty_v2!B10",
    "P0_Gates_v2!I6",
    "P0_Gates_v2!J6",
    "Surse_Date!L9",
    "Surse_Date!L10",
)


def audit(case_id: str, inputs: dict) -> None:
    wanted = [f"Double_Chance!{col}{row}" for row in (4, 5, 6) for col in CHAIN_COLUMNS]
    result = compute_double_chance(inputs, evaluate=[*wanted, *CONTEXT_CELLS])
    print(f"\n=== {case_id} ===")
    for cell in CONTEXT_CELLS:
        print(f"  {cell:22s} = {result.cells.get(cell)!r}")
    for code, row in (("1X", 4), ("X2", 5), ("12", 6)):
        print(f"  --- {code} (rând {row}) ---")
        for col in CHAIN_COLUMNS:
            print(f"    {col:3s} = {result.cells.get(f'Double_Chance!{col}{row}')!r}")


def main() -> None:
    cases = {c["id"]: c for c in json.loads((SPEC / "cazuri_test.json").read_text(encoding="utf-8"))["cases"]}
    wanted = sys.argv[1:] or ["baseline", "early_season_A"]
    for case_id in wanted:
        audit(case_id, cases[case_id]["inputs"])


if __name__ == "__main__":
    main()
