from src.excel.generator import write_double_chance_results_csv, write_over05_results_csv
from src.ui_tables import double_chance_summary_rows, over05_summary_rows, validation_summary_rows


def _fmt_prob(value):
    if value is None or value == "":
        return ""
    return f"{float(value) * 100:.2f}%"


def _fmt_score(value):
    if value is None or value == "":
        return ""
    return f"{float(value):.2f}"


SAMPLE = {
    "model_id": "over05",
    "ora_bucuresti": "16:00",
    "liga": "Premier League",
    "echipe": "Arsenal vs Chelsea",
    "model": "Over 0.5",
    "recommendation": "WATCH / NO BET",
    "risk_level": 2,
    "model_g0": "PASS",
    "p_over": 0.92,
    "p0_recalibrated": 0.81,
    "confidence": 59.19,
    "risk_score": 7.87,
    "data_status": "valid",
    "g0": "OK",
    "motiv": "",
    "match_id": "90001",
}


def test_over05_table_starts_with_kickoff_and_league():
    rows = over05_summary_rows([SAMPLE], fmt_prob=_fmt_prob, fmt_score=_fmt_score)
    assert list(rows[0].keys())[:3] == ["Oră de începere", "Ligă", "Echipe"]
    assert rows[0]["Oră de începere"] == "16:00"
    assert rows[0]["Ligă"] == "Premier League"


def test_validation_table_starts_with_kickoff_and_league():
    rows = validation_summary_rows(
        [SAMPLE],
        fmt_prob=_fmt_prob,
        fmt_score=_fmt_score,
        color_status=lambda v: v,
    )
    keys = list(rows[0].keys())
    assert keys[:3] == ["Oră de începere", "Ligă", "Echipe"]
    assert "Oră București" not in keys
    assert keys.count("Ligă") == 1


def test_over05_csv_starts_with_ora_and_liga(tmp_path):
    path = write_over05_results_csv(tmp_path, [SAMPLE])
    header = path.read_text(encoding="utf-8").splitlines()[0]
    assert header.startswith("ora,liga,match_id,echipe,")


DC_SAMPLE = {
    "model_id": "double_chance",
    "ora_bucuresti": "20:00",
    "liga": "Liga Test",
    "echipe": "Echipa Alfa vs Echipa Beta",
    "match_id": "dc-1",
    "dc_sample_status": "SMALL SAMPLE",
    "dc_prior_status": "PRIOR / SHRINKAGE",
    "dc_selections": [
        {
            "selection": "1X",
            "p_model": 0.93,
            "p_adj": 0.92,
            "pfail_model": 0.07,
            "pfail_market": 0.08,
            "pfail_dc": 0.08,
            "haircut_base": 0.01,
            "haircut_early": 0.0,
            "haircut_total": 0.01,
            "market_direction": "PASS",
            "protected_strength": "PASS",
            "draw_gate": "N/A",
            "p0_final": "PASS",
            "score": 16,
            "risk_score_before_cap": 16.0,
            "level": 1,
            "verdict": "DEFENSIV",
            "ranking_eligible": "YES",
            "defensive_eligible": "YES",
            "release": "READY",
        },
        {
            "selection": "X2",
            "p_adj": 0.165,
            "pfail_model": 0.825,
            "pfail_market": 0.82,
            "pfail_dc": 0.825,
            "p0_final": "FAIL",
            "score": 100,
            "risk_score_before_cap": 211.0,
            "level": 5,
            "verdict": "NO BET",
            "ranking_eligible": "NO",
            "defensive_eligible": "NO",
            "release": "READY",
        },
    ],
}


def test_double_chance_table_shows_verdict_and_selection():
    rows = double_chance_summary_rows([DC_SAMPLE], fmt_prob=_fmt_prob, fmt_score=_fmt_score)
    assert list(rows[0].keys())[:5] == [
        "Oră de începere",
        "Ligă",
        "Echipe",
        "Selecție",
        "Verdict",
    ]
    assert rows[0]["Selecție"] == "1X"
    assert rows[0]["Verdict"] == "DEFENSIV"
    assert rows[0]["P_adj"] == "92.00%"
    assert rows[0]["Eșantion"] == "SMALL SAMPLE"
    assert rows[0]["Prior"] == "PRIOR / SHRINKAGE"
    assert rows[0]["Stare date"] == "READY"


def test_double_chance_table_separates_pfail_model_market_and_conservative():
    rows = double_chance_summary_rows([DC_SAMPLE], fmt_prob=_fmt_prob, fmt_score=_fmt_score)
    assert rows[0]["Pfail model"] == "7.00%"
    assert rows[0]["Pfail piață"] == "8.00%"
    assert rows[0]["Pfail DC"] == "8.00%"
    assert "Pfail" not in rows[0]


def test_double_chance_table_separates_controls_from_verdict():
    rows = double_chance_summary_rows([DC_SAMPLE], fmt_prob=_fmt_prob, fmt_score=_fmt_score)
    keys = list(rows[0].keys())
    for column in ("Market Direction", "Protected Strength", "Draw Gate", "P0 final"):
        assert column in keys
    assert "Gate" not in keys
    assert rows[0]["Haircut bază"] == "1.00%"
    assert rows[0]["Haircut early"] == "0.00%"
    assert rows[0]["Haircut total"] == "1.00%"


def test_double_chance_default_view_hides_failed_selections_without_deleting_them():
    shortlist = double_chance_summary_rows(
        [DC_SAMPLE], fmt_prob=_fmt_prob, fmt_score=_fmt_score, show_all=False
    )
    everything = double_chance_summary_rows(
        [DC_SAMPLE], fmt_prob=_fmt_prob, fmt_score=_fmt_score, show_all=True
    )
    assert [r["Selecție"] for r in shortlist] == ["1X"]
    assert [r["Selecție"] for r in everything] == ["1X", "X2"]


def test_capped_score_keeps_raw_value_for_audit():
    rows = double_chance_summary_rows([DC_SAMPLE], fmt_prob=_fmt_prob, fmt_score=_fmt_score)
    x2 = next(r for r in rows if r["Selecție"] == "X2")
    assert x2["Scor"] == "100.00"
    assert x2["Scor brut"] == "211.00"


def test_double_chance_csv_one_row_per_selection(tmp_path):
    path = write_double_chance_results_csv(tmp_path, [DC_SAMPLE])
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith("ora,liga,match_id,echipe,selectie,")
    assert "1X" in lines[1]
    assert "DEFENSIV" in lines[1]


def test_fill_missing_liga_uses_listing_when_analysis_row_is_blank():
    from src.ui_tables import fill_missing_liga

    rows = fill_missing_liga(
        [{"match_id": "1", "liga": "", "echipe": "A vs B"}],
        [{"match_id": "1", "liga": "Romania Liga I"}],
    )
    assert rows[0]["liga"] == "Romania Liga I"
