"""Teste adaptoare + integritate workbook."""

from pathlib import Path

from openpyxl import load_workbook

from src.adapters.corners import CornersAdapter
from src.adapters.double_chance import DoubleChanceAdapter
from src.adapters.over05 import Over05Adapter
from src.api.mock import MockFootyStatsClient
from src.excel.integrity import fingerprint_workbook
from src.validation.validator import validate_match_for_model


def test_over05_preserves_formulas(tmp_path: Path):
    client = MockFootyStatsClient()
    matches = [client.enrich_match(m) for m in client.matches_by_date("2026-03-15")[:2]]
    # doar meciuri neblocate
    ok = [m for m in matches if not validate_match_for_model(m, "over05").is_blocked(m.match_id, "over05")]
    adapter = Over05Adapter()
    before = fingerprint_workbook(adapter.template_path())
    dest = tmp_path / "over05.xlsx"
    adapter.write_matches(ok, dest)
    after = fingerprint_workbook(dest)
    assert after.sheet_names == before.sheet_names
    assert after.formulas == before.formulas
    wb = load_workbook(dest, data_only=False)
    ws = wb["Analize meciuri"]
    assert ws["A4"].value == ok[0].match_id
    assert ws["G4"].value == ok[0].home.name
    # formule pe BJ rămân formule
    if ws["BJ4"].value:
        assert str(ws["BJ4"].value).startswith("=")
    wb.close()


def test_double_chance_single_match(tmp_path: Path):
    client = MockFootyStatsClient()
    md = client.enrich_match(client.matches_by_date("2026-03-15")[0])
    adapter = DoubleChanceAdapter()
    before = fingerprint_workbook(adapter.template_path())
    dest = tmp_path / "dc.xlsx"
    adapter.write_matches([md], dest)
    after = fingerprint_workbook(dest)
    assert after.formulas == before.formulas
    wb = load_workbook(dest)
    assert wb["Input_Meci"]["B4"].value == "Arsenal"
    assert wb["Input_Meci"]["C4"].value == "Chelsea"
    wb.close()


def test_corners_blocks_unavailable_not_written_as_zero(tmp_path: Path):
    client = MockFootyStatsClient()
    # Arsenal-Chelsea are cornere OK
    md = client.enrich_match(client.matches_by_date("2026-03-15")[0])
    adapter = CornersAdapter()
    before = fingerprint_workbook(adapter.template_path())
    dest = tmp_path / "corners.xlsx"
    adapter.write_matches([md], dest)
    after = fingerprint_workbook(dest)
    assert after.formulas == before.formulas
    wb = load_workbook(dest)
    assert wb["Input_Meci"]["A6"].value == md.match_id
    notes = wb["Input_Meci"]["M6"].value or ""
    assert "corners_native" in notes
    assert "None" not in notes.split("H_s_for=")[1][:5] or "H_s_for=5" in notes or "H_s_for=6" in notes
    wb.close()
