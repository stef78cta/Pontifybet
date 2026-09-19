"""Teste adaptoare + integritate workbook."""

from pathlib import Path

import pytest
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
    assert ws["N4"].value == pytest.approx(0.93)
    assert ws["J4"].value == pytest.approx(32 / 14)
    assert ws["EV4"].value == pytest.approx(0.07)
    assert ws["FB4"].value is None
    if ws["BJ4"].value:
        assert str(ws["BJ4"].value).startswith("=")
    assert ws["HK4"].value is None or str(ws["HK4"].value).startswith("=")
    assert ws["HR4"].value
    assert ws["HR3"].value == "Recomandare finala (HK)"
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
    assert wb["Model_1X2"]["B6"].value is not None
    assert wb["Surse_Date"]["C6"].value == "DERIVED"
    assert wb["Surse_Date"]["G9"].value is None or str(wb["Surse_Date"]["G9"].value).startswith("=")
    assert wb["Input_Meci"]["G61"].value not in {None, "VERIFICARE NECESARĂ – NO RANK"}
    assert wb["Input_Meci"]["A60"].value == "Selecție"
    wb.close()


def test_double_chance_small_sample_writes_real_prior_row(tmp_path: Path):
    client = MockFootyStatsClient()
    md = client.enrich_match(client.matches_by_date("2026-03-15")[0])
    md.home.matches_played_home.value = 6
    md.away.matches_played_away.value = 5
    adapter = DoubleChanceAdapter()
    dest = tmp_path / "dc_small.xlsx"
    adapter.write_matches([md], dest)
    wb = load_workbook(dest)
    assert wb["Surse_Date"]["C9"].value == "SMALL SAMPLE"
    assert wb["Surse_Date"]["C10"].value == "PRIOR / SHRINKAGE"
    assert wb["Surse_Date"]["K10"].value == "INTEGRAT IN MODELE"
    assert wb["Surse_Date"]["G10"].value == md.league_avg_gf_home.n
    assert wb["Surse_Date"]["H10"].value == md.league_avg_gf_away.n
    assert wb["Surse_Date"]["G10"].value != 30
    assert wb["Input_Meci"]["B36"].value == 6
    assert wb["Input_Meci"]["C36"].value == 5
    assert wb["Input_Meci"]["G61"].value not in {None, "VERIFICARE NECESARĂ – NO RANK"}
    wb.close()


def _corners_bundle(match_ids: list[str]):
    """Rulează ANALYSIS pe mock și întoarce bundle-ul Cornere din snapshot."""
    import src.pipeline as pipeline

    original = pipeline.get_client
    pipeline.get_client = lambda: MockFootyStatsClient()
    try:
        analysis = pipeline.run_analysis(
            date_iso="2026-03-15",
            league_ids=[2012, 2013],
            match_ids=match_ids,
            model_ids=["corners"],
            timezone_name="Europe/Bucharest",
        )
    finally:
        pipeline.get_client = original
    return analysis["snapshot"]


def test_corners_export_writes_native_inputs_and_python_results(tmp_path: Path):
    """Exportul completează inputurile native și copiază rezultatele deja calculate."""
    snapshot = _corners_bundle(["90001", "90002"])
    bundle = snapshot.corners
    matches = snapshot.allowed_by_model["corners"]
    adapter = CornersAdapter()
    before = fingerprint_workbook(
        adapter.template_path(), max_rows=adapter.integrity_max_rows
    )
    dest = tmp_path / "corners.xlsx"
    adapter.write_matches(matches, dest, artifacts=bundle)
    after = fingerprint_workbook(dest, max_rows=adapter.integrity_max_rows)
    assert after.formulas == before.formulas
    assert len(before.formulas) == 85647

    wb = load_workbook(dest)
    try:
        assert wb["Input_Meci"]["A6"].value == matches[0].match_id
        # Istoricul nativ ajunge în foaia lui, nu serializat în Notes.
        assert wb["Istoric_Nativ"]["A6"].value
        assert isinstance(wb["Istoric_Nativ"]["G6"].value, int)
        assert wb["Surse_Import"]["A6"].value
        assert wb["Surse_Import"]["D6"].value == "FootyStats"
        # Zona de rezultate: antet la 107, apoi 14 linii per meci.
        zone = adapter.cfg["result_zone"]
        first = int(zone["first_row"])
        assert wb["Input_Meci"][f"A{first}"].value == "Match_ID"
        assert wb["Input_Meci"][f"D{first + 1}"].value == "O3,5"
        labels = {
            wb["Input_Meci"][f"D{first + 1 + offset}"].value for offset in range(28)
        }
        assert len(labels) == 14
    finally:
        wb.close()


def test_corners_export_clears_demo_history(tmp_path: Path):
    """Inputurile demonstrative din șablon nu contaminează o rulare LIVE."""
    snapshot = _corners_bundle(["90001"])
    adapter = CornersAdapter()
    dest = tmp_path / "corners_clean.xlsx"
    adapter.write_matches(
        snapshot.allowed_by_model["corners"], dest, artifacts=snapshot.corners
    )
    template = load_workbook(adapter.template_path())
    exported = load_workbook(dest)
    try:
        demo_ids = {
            template["Istoric_Nativ"][f"A{row}"].value
            for row in range(6, 60)
            if template["Istoric_Nativ"][f"A{row}"].value
        }
        exported_ids = {
            exported["Istoric_Nativ"][f"A{row}"].value
            for row in range(6, 406)
            if exported["Istoric_Nativ"][f"A{row}"].value
        }
        assert demo_ids
        assert not (demo_ids & exported_ids)
    finally:
        template.close()
        exported.close()
