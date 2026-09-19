"""Raportul celor trei meciuri-martor V14 (exemplele REPLAY din pachetul tehnic).

Rulează motorul pe `fixture_input_original.json` și afișează, pentru fiecare meci,
starea de model plus linia selectată, alături de valorile din `expected_42_selectii.csv`.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from tests.test_corners_excel_parity import _batch, _expected  # noqa: E402
from src.engines.corners import compute_corners_batch  # noqa: E402


def main() -> None:
    result = compute_corners_batch(_batch())
    expected = {(row["Match_ID"], row["Line"]): row for row in _expected()}

    for match in result.ordered():
        selected = match.selected_line
        print(f"\n=== {match.match_id} | slot {match.slot} | mod {match.mode}")
        print(
            f"    Release={match.release} G0={match.g0} "
            f"distributie={match.distribution_kind} Mu={match.motor.get('Mu')} "
            f"D={match.motor.get('D')}"
        )
        print(
            f"    {'Linie':<8}{'P_Raw':>14}{'P_FINAL':>14}{'Failure':>10}"
            f"{'Risk':>10}{'Conf':>8}{'Niv':>5}  Verdict / Tail / Def / OOS"
        )
        for item in match.lines:
            ref = expected.get((match.match_id, item.label), {})
            flag = "" if ref else "  (fără referință)"
            print(
                f"    {item.label:<8}{item.p_raw or 0:>14.10f}{item.p_final or 0:>14.10f}"
                f"{item.failure_model or 0:>10.4f}{item.risk_score or 0:>10.3f}"
                f"{item.confidence_final or 0:>8.1f}{item.risk_level:>5}"
                f"  {item.verdict} / {item.tail_gate} / {item.defensive_gate} /"
                f" {item.oos_status}{flag}"
            )
        if selected is not None:
            print(
                f"    -> selecție: {selected.label} rang_in_meci={selected.rank_in_match} "
                f"eligibil={selected.eligible} rank_live={selected.rank_live} "
                f"motiv={selected.reason}"
            )

    csv_path = ROOT / "audit" / "corners_witness_lines.csv"
    csv_path.parent.mkdir(exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["Match_ID", "Line", "P_Raw", "P_FINAL", "Failure_Model", "Risk_Score",
             "Confidence_Final", "Risk_Level_FINAL", "Verdict_FINAL", "Eligible"]
        )
        for match in result.ordered():
            for item in match.lines:
                writer.writerow(
                    [match.match_id, item.label, item.p_raw, item.p_final,
                     item.failure_model, item.risk_score, item.confidence_final,
                     item.risk_level, item.verdict, int(item.eligible)]
                )
    print(f"\nScris {csv_path}")


if __name__ == "__main__":
    main()
