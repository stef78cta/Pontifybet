"""Oracle Microsoft Excel pentru Cornere Multi-Line V14. SKIPPED dacă Excel lipsește.

Testele de paritate din `test_corners_excel_parity.py` compară motorul cu valorile
din cache-ul workbook-ului și cu cele 42 de selecții din pachetul tehnic. Aici
Microsoft Excel recalculează efectiv o copie cu aceleași inputuri native, ca
paritatea să fie confirmată de motorul de calcul original, nu de un cache.
"""

from __future__ import annotations

import math
import time
from pathlib import Path
from typing import Any

import pytest
from openpyxl import load_workbook

from config.settings import TEMPLATES_DIR
from src.engines.corners import compute_corners_batch
from src.engines.corners.engine import (
    CORE_FIRST_ROW,
    CORE_ROWS_PER_SLOT,
    DASHBOARD_FIRST_ROW,
    DISTRIBUTION_FIRST_ROW,
    DISTRIBUTION_SHEET,
    LINES_SHEET,
    MOTOR_FIRST_ROW,
    MOTOR_SHEET,
    CORE_SHEET,
    TEMPLATE_NAME,
    core_columns,
    distribution_columns,
    lines_columns,
    motor_columns,
)
from src.engines.corners.inputs import CornersBatchInput, build_overrides
from tests.corners_synthetic import match_input, oos_record, round_robin, source

TOL = 1e-10
REL_TOL = 1e-12

#: Coloanele rezultatului oficial pe linie, verificate integral față de Excel.
LINE_COLUMNS: tuple[str, ...] = (
    "Release",
    "G0",
    "Mu",
    "D",
    "P_Raw",
    "P_Calibrated",
    "P_FINAL",
    "Failure_Model",
    "Failure_Gate",
    "Risk_Score",
    "Risk_Level_Raw",
    "Risk_Level_FINAL",
    "Confidence_Final",
    "Candidate_Confidence",
    "Tail_Gate",
    "Defensive_Candidate",
    "Defensive_Gate",
    "Verdict_FINAL",
    "Rank_In_Match",
    "Rank_LIVE",
    "Eligible",
    "Builder",
    "Live_Eligible_Best",
    "Reason",
    "OOS_Status",
    "Model_Signature",
)


def _excel_capability() -> str:
    """Verifică dacă Excel-ul local poate evalua formulele V14.

    `Core_Nativ` construiește ferestrele recente cu `_xlfn._xlws.FILTER`. Un Excel
    fără matrici dinamice (perpetual 2019/2021) returnează `#NAME?` pentru ea, iar
    `G0` cade în `FAIL` pe tot workbook-ul. Într-un asemenea Excel oracle-ul nu are
    sens: nu compară două implementări ale aceluiași model, ci un model complet cu
    unul din care lipsește o funcție.

    @returns - șir gol dacă oracle-ul poate rula, altfel motivul de skip.
    """
    try:
        import pythoncom
        import win32com.client
    except ImportError:
        return "pywin32 indisponibil"
    excel = None
    workbook = None
    try:
        pythoncom.CoInitialize()
        excel = win32com.client.DispatchEx("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False
        workbook = excel.Workbooks.Add()
        sheet = workbook.Worksheets(1)
        try:
            sheet.Range("A1").Formula = "=_xlfn._xlws.FILTER({1;2;3},{1;0;1})"
        except Exception:
            return f"Excel {excel.Version} build {excel.Build} nu suportă FILTER"
        if "#NAME" in str(sheet.Range("A1").Text):
            return f"Excel {excel.Version} build {excel.Build} nu suportă FILTER"
        return ""
    except Exception as exc:  # noqa: BLE001
        return f"Microsoft Excel indisponibil ({type(exc).__name__})"
    finally:
        if workbook is not None:
            try:
                workbook.Close(False)
            except Exception:
                pass
        if excel is not None:
            try:
                excel.Quit()
            except Exception:
                pass
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass


SKIP_REASON = _excel_capability()

pytestmark = pytest.mark.skipif(
    bool(SKIP_REASON), reason=f"oracle Cornere SKIPPED: {SKIP_REASON}"
)


def _blank(value: Any) -> bool:
    return value is None or value == ""


def _same(actual: Any, expected: Any) -> bool:
    if _blank(actual) and _blank(expected):
        return True
    if isinstance(actual, bool) or isinstance(expected, bool):
        return bool(actual) == bool(expected)
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        return math.isclose(
            float(actual), float(expected), rel_tol=REL_TOL, abs_tol=TOL
        )
    if isinstance(actual, (int, float)) or isinstance(expected, (int, float)):
        return False
    return str(actual) == str(expected)


def _recalculate_with_excel(path: Path) -> None:
    """Deschide copia, CalculateFullRebuild, salvează valorile native."""
    import pythoncom
    import win32com.client

    pythoncom.CoInitialize()
    excel = win32com.client.DispatchEx("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False
    excel.AskToUpdateLinks = False
    excel.EnableEvents = False
    wb = None
    try:
        wb = excel.Workbooks.Open(str(path), UpdateLinks=0, ReadOnly=False)
        excel.Calculation = -4105
        excel.CalculateFullRebuild()
        # V14 are 85.647 de formule și tabele întinse pe 1405 rânduri: rebuild-ul
        # complet cere sensibil mai mult decât modelele cu o singură foaie.
        deadline = time.time() + 600
        while int(excel.CalculationState) != 0 and time.time() < deadline:
            time.sleep(0.5)
        if int(excel.CalculationState) != 0:
            raise RuntimeError("Excel CalculationState nu a ajuns xlDone")
        wb.Save()
        wb.Close(SaveChanges=True)
        wb = None
    finally:
        if wb is not None:
            try:
                wb.Close(SaveChanges=False)
            except Exception:
                pass
        try:
            excel.Quit()
        except Exception:
            pass
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass


def _materialize(batch: CornersBatchInput, dest: Path) -> None:
    """Scrie inputurile lotului într-o copie a șablonului, fără alte modificări."""
    dest.write_bytes((TEMPLATES_DIR / TEMPLATE_NAME).read_bytes())
    wb = load_workbook(dest)
    try:
        for (sheet, coord), value in build_overrides(batch).items():
            wb[sheet][coord] = value
        wb.save(dest)
    finally:
        wb.close()


@pytest.fixture(scope="module")
def oracle(tmp_path_factory) -> dict[str, Any]:
    """Un lot sintetic recalculat o singură dată de Microsoft Excel.

    FIXTURE SINTETIC: două meciuri LIVE pe un istoric round-robin construit în
    `tests/corners_synthetic.py`, plus o înregistrare OOS, ca să fie exercitate
    simultan ramurile de distribuție, gate-urile și clasamentul.
    """
    history = round_robin(count=60)
    batch = CornersBatchInput(
        matches=(
            match_input(match_id="ORACLE-1"),
            match_input(match_id="ORACLE-2", home="Gama FC", away="Delta FC"),
        ),
        history=tuple(history),
        sources=(source(rows=len(history)),),
        oos_records=(oos_record(fixture_id="ORACLE-OOS", line="O3,5", total_corners=9),),
    )
    python = compute_corners_batch(batch)

    dest = tmp_path_factory.mktemp("corners-oracle") / "corners_v14_oracle.xlsx"
    _materialize(batch, dest)
    _recalculate_with_excel(dest)
    cached = load_workbook(dest, data_only=True)
    return {"batch": batch, "python": python, "workbook": cached}


def _excel_row(cached: Any, sheet: str, row: int, columns: dict[str, str]) -> dict[str, Any]:
    ws = cached[sheet]
    return {name: ws[f"{letter}{row}"].value for name, letter in columns.items()}


def test_all_fourteen_lines_match_microsoft_excel(oracle):
    cached = oracle["workbook"]
    columns = lines_columns()
    mismatches: list[str] = []
    for result in oracle["python"].ordered():
        for line in result.lines:
            excel = _excel_row(cached, LINES_SHEET, line.excel_row, columns)
            for name in LINE_COLUMNS:
                if not _same(line.cells.get(name), excel.get(name)):
                    mismatches.append(
                        f"{result.match_id} {line.label} {name}: "
                        f"python={line.cells.get(name)!r} excel={excel.get(name)!r}"
                    )
    assert not mismatches, "Diferențe față de Microsoft Excel:\n" + "\n".join(mismatches)


def test_match_engine_row_matches_microsoft_excel(oracle):
    cached = oracle["workbook"]
    columns = motor_columns()
    mismatches: list[str] = []
    for index, result in enumerate(oracle["python"].ordered()):
        excel = _excel_row(cached, MOTOR_SHEET, MOTOR_FIRST_ROW + index, columns)
        for name, value in result.motor.items():
            if not _same(value, excel.get(name)):
                mismatches.append(
                    f"{result.match_id} {name}: python={value!r} excel={excel.get(name)!r}"
                )
    assert not mismatches, "Diferențe `Motor_Meciuri`:\n" + "\n".join(mismatches)


def test_native_averages_match_microsoft_excel(oracle):
    cached = oracle["workbook"]
    columns = core_columns()
    mismatches: list[str] = []
    for index, result in enumerate(oracle["python"].ordered()):
        first = CORE_FIRST_ROW + index * CORE_ROWS_PER_SLOT
        for offset, row in enumerate(result.core):
            excel = _excel_row(cached, CORE_SHEET, first + offset, columns)
            for name, value in row.items():
                if not _same(value, excel.get(name)):
                    mismatches.append(
                        f"{result.match_id} Core[{offset}] {name}: "
                        f"python={value!r} excel={excel.get(name)!r}"
                    )
    assert not mismatches, "Diferențe `Core_Nativ`:\n" + "\n".join(mismatches)


def test_distribution_row_matches_microsoft_excel(oracle):
    cached = oracle["workbook"]
    columns = distribution_columns()
    mismatches: list[str] = []
    for index, result in enumerate(oracle["python"].ordered()):
        excel = _excel_row(
            cached, DISTRIBUTION_SHEET, DISTRIBUTION_FIRST_ROW + index, columns
        )
        for name, value in result.distribution.items():
            if not _same(value, excel.get(name)):
                mismatches.append(
                    f"{result.match_id} {name}: python={value!r} excel={excel.get(name)!r}"
                )
    assert not mismatches, "Diferențe `Distributie`:\n" + "\n".join(mismatches)


def test_dashboard_selection_matches_microsoft_excel(oracle):
    cached = oracle["workbook"]
    ws = cached["Dashboard"]
    mismatches: list[str] = []
    for index, result in enumerate(oracle["python"].ordered()):
        row = DASHBOARD_FIRST_ROW + index
        for letter, value in result.dashboard.items():
            excel_value = ws[f"{letter}{row}"].value
            if not _same(value, excel_value):
                mismatches.append(
                    f"{result.match_id} Dashboard!{letter}{row}: "
                    f"python={value!r} excel={excel_value!r}"
                )
    assert not mismatches, "Diferențe `Dashboard`:\n" + "\n".join(mismatches)
